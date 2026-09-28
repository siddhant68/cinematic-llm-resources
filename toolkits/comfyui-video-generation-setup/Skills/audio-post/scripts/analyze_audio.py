#!/usr/bin/env python3
"""
analyze_audio.py — Measure a dialogue track and prescribe a processing chain.

Audio post fails in a specific way: people reach for compression and loudness
first, because those are the audible ones, and bake in noise, rumble and
sibilance that then get amplified. This measures what is actually wrong and emits
a chain in the order that fixes rather than amplifies.

  python analyze_audio.py dialogue.wav
  python analyze_audio.py video.mp4 --target -14 --json
  python analyze_audio.py dialogue.wav --emit-chain > chain.txt

Measures: integrated loudness, loudness range, true peak, noise floor, SNR,
clipping, DC offset, rumble energy, sibilance energy, and room-tone candidates.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
import os

# Delivery targets. YouTube normalises toward roughly -14 LUFS; going louder
# than the platform target just means it turns you down, and you lose the
# dynamics you crushed to get there.
TARGETS = {
    "youtube": (-14.0, -1.0),
    "podcast": (-16.0, -1.0),
    "broadcast": (-23.0, -2.0),
    "instagram": (-14.0, -1.0),
    "tiktok": (-14.0, -1.0),
}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def have_audio(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
             "stream=index,sample_rate,channels", "-of", "json", path])
    try:
        s = json.loads(r.stdout).get("streams", [])
        return s[0] if s else None
    except (json.JSONDecodeError, IndexError):
        return None


def measure_loudnorm(path, target_i, target_tp):
    """Pass 1 of two-pass loudnorm. These numbers feed pass 2."""
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-af",
             f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:print_format=json",
             "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def measure_astats(path):
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-af",
             "astats=metadata=1:reset=0", "-f", "null", "-"])
    out = {}
    for key in ("Peak level dB", "RMS level dB", "DC offset", "Flat factor",
                "Peak count", "Abs Peak count", "Noise floor dB",
                "Dynamic range", "Number of samples", "Entropy"):
        m = re.findall(rf"{re.escape(key)}:\s*(-?[\d.]+|inf|-inf)", r.stderr)
        if m:
            v = m[-1]
            out[key] = float(v) if v not in ("inf", "-inf") else (
                float("inf") if v == "inf" else float("-inf"))
    return out


def measure_silence(path, thresh_db, min_dur):
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-af",
             f"silencedetect=noise={thresh_db}dB:d={min_dur}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", r.stderr)]
    spans = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else None
        if e is not None and e > s:
            spans.append((s, e))
    return spans


def band_energy(path, lo, hi):
    """Mean RMS dB inside a frequency band — used for rumble and sibilance."""
    if lo <= 0:
        af = f"lowpass=f={hi},astats=metadata=1:reset=0"
    elif hi >= 20000:
        af = f"highpass=f={lo},astats=metadata=1:reset=0"
    else:
        af = f"highpass=f={lo},lowpass=f={hi},astats=metadata=1:reset=0"
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-af", af, "-f", "null", "-"])
    m = re.findall(r"RMS level dB:\s*(-?[\d.]+)", r.stderr)
    return float(m[-1]) if m else None


def find_quiet_spans(path, speech_rms, ln_thresh):
    """Sweep the silence threshold until quiet spans appear.

    A fixed threshold fails on the exact material that needs measuring: a noisy
    room has no region below -45 dB, so the noise floor becomes invisible
    precisely when it matters. Anchor the sweep to the measured speech level and
    loudnorm's own gating threshold instead.
    """
    # silencedetect thresholds on PEAK, so a threshold set from RMS runs several
    # dB too low. Sweep downward-then-upward and validate each hit.
    anchors = []
    if ln_thresh is not None:
        anchors.append(ln_thresh - 4)
    if speech_rms is not None:
        anchors += [speech_rms - 25, speech_rms - 18, speech_rms - 12,
                    speech_rms - 9, speech_rms - 6]
    anchors += [-50, -45, -40, -35, -30, -25, -22]

    tried = set()
    for th in anchors:
        th = round(th, 1)
        if th in tried or not (-80 < th < -12):
            continue
        tried.add(th)
        for min_dur in (0.35, 0.2):
            spans = measure_silence(path, th, min_dur)
            if not spans:
                continue
            # Reject a "silence" that is really just quieter speech: the span
            # must sit clearly below the global RMS to be a noise-floor sample.
            longest = max(spans, key=lambda x: x[1] - x[0])
            probe = _span_rms(path, longest)
            if probe is None:
                continue
            if speech_rms is None or probe <= speech_rms - 4.0:
                return spans, th
    return [], None


def _span_rms(path, span, max_dur=2.0):
    s, e = span
    dur = min(e - s, max_dur)
    if dur < 0.15:
        return None
    r = run(["ffmpeg", "-hide_banner", "-ss", f"{s + 0.05:.3f}", "-t",
             f"{dur:.3f}", "-i", path, "-af",
             "aformat=channel_layouts=mono:sample_rates=48000,"
             "astats=metadata=1:reset=0", "-f", "null", "-"])
    m = re.findall(r"RMS level dB:\s*(-?[\d.]+)", r.stderr)
    return float(m[-1]) if m else None


def noise_floor_from_silence(path, spans):
    """RMS inside the longest quiet span = the real noise floor, and the best
    source of room tone."""
    if not spans:
        return None, None
    longest = max(spans, key=lambda x: x[1] - x[0])
    return _span_rms(path, longest), longest


def analyse(path, target_i, target_tp):
    st = have_audio(path)
    if not st:
        sys.exit(f"No audio stream in {path}")

    ln = measure_loudnorm(path, target_i, target_tp)
    ast = measure_astats(path)
    spans, used_thresh = find_quiet_spans(
        path, ast.get("RMS level dB"),
        float(ln["input_thresh"]) if ln else None)
    nf, tone_span = noise_floor_from_silence(path, spans)

    rumble = band_energy(path, 0, 80)
    sibilance = band_energy(path, 5000, 9000)
    body = band_energy(path, 200, 4000)

    rms = ast.get("RMS level dB")
    return {
        "sample_rate": int(st.get("sample_rate", 0)),
        "channels": st.get("channels"),
        "integrated_lufs": float(ln["input_i"]) if ln else None,
        "lra": float(ln["input_lra"]) if ln else None,
        "true_peak_dbtp": float(ln["input_tp"]) if ln else None,
        "measured_thresh": float(ln["input_thresh"]) if ln else None,
        "peak_db": ast.get("Peak level dB"),
        "rms_db": rms,
        "dc_offset": ast.get("DC offset"),
        "flat_factor": ast.get("Flat factor"),
        "peak_count": ast.get("Peak count"),
        "noise_floor_db": nf,
        "snr_db": (rms - nf) if (rms is not None and nf is not None) else None,
        "rumble_db": rumble,
        "sibilance_db": sibilance,
        "body_db": body,
        "sibilance_ratio": (sibilance - body) if (sibilance and body) else None,
        "rumble_ratio": (rumble - body) if (rumble and body) else None,
        "silence_spans": len(spans),
        "silence_threshold_used": used_thresh,
        "room_tone_span": tone_span,
        "target_i": target_i,
        "target_tp": target_tp,
        "_ln": ln,
    }


def prescribe(m):
    """Emit findings and a chain, in repair-before-enhance order."""
    findings, chain, notes = [], [], []

    # --- 1. repair -----------------------------------------------------
    tp = m.get("true_peak_dbtp")
    pk = m.get("peak_db")
    pc = m.get("peak_count")
    # The reliable clipping indicator is Peak count -- how many samples sit
    # exactly at the maximum. An unclipped signal touches its peak once or twice;
    # a clipped one pins there for hundreds of samples. Flat factor reads 0.00 on
    # definitively clipped audio, so it is not usable for this. Verified against
    # a hard-clipped file: peak -0.0008 dB, flat factor 0.00, peak count 240.
    hot = (tp is not None and tp > -0.5) or (pk is not None and pk > -0.2)
    if hot and pc is not None and pc > 20:
        findings.append(
            f"CLIPPING confirmed — {int(pc)} samples pinned at full scale "
            f"(peak {pk} dB, true peak {tp} dBTP). Repair first; a compressor "
            "cannot rebuild a flat-topped wave.")
        chain.append("adeclip")
    elif hot:
        findings.append(
            f"Peak is hot ({tp} dBTP) with only {int(pc) if pc else 0} samples at "
            "the ceiling — loud but not clipped. The limiter and loudnorm at the "
            "end will bring it down.")
    dc = m.get("dc_offset")
    if dc is not None and abs(dc) > 0.002:
        findings.append(f"DC offset {dc:+.4f} — wastes headroom and can thump at "
                        "cuts.")
        chain.append("highpass=f=20")
    chain.append("adeclick")           # mouth clicks; cheap and near-transparent

    # --- 2. subtractive tone -------------------------------------------
    rr = m.get("rumble_ratio")
    if rr is not None and rr > -28:
        findings.append(
            f"RUMBLE: sub-80Hz sits {rr:+.1f} dB relative to speech body. Room "
            "noise, desk thumps or HVAC. This eats headroom that compression "
            "then amplifies.")
        chain.append("highpass=f=85:poles=2")
    else:
        chain.append("highpass=f=75:poles=2")
        notes.append("High-pass at 75Hz regardless: nothing useful for a male "
                     "speaking voice lives below it, and it buys headroom.")

    # --- 3. noise -------------------------------------------------------
    snr = m.get("snr_db")
    nf = m.get("noise_floor_db")
    if snr is not None:
        if snr < 25:
            findings.append(
                f"NOISE FLOOR high: SNR {snr:.1f} dB (floor {nf:.1f} dB). Below "
                "25 dB the noise becomes audible once you compress. Denoise "
                "BEFORE compression, not after.")
            chain.append(f"afftdn=nr=12:nf={max(-80, min(-20, (nf or -50))):.0f}:tn=1")
        elif snr < 40:
            findings.append(f"SNR {snr:.1f} dB — acceptable. Light denoise only; "
                            "over-denoising produces the underwater artefact.")
            chain.append(f"afftdn=nr=6:nf={max(-80, min(-20, (nf or -55))):.0f}:tn=1")
        else:
            findings.append(f"SNR {snr:.1f} dB — clean. No denoise needed.")
            notes.append("Skipping denoise. Applying it anyway costs presence and "
                         "adds artefacts for no gain.")
    else:
        notes.append("Could not estimate a noise floor — no quiet span found at "
                     "any threshold. Either the track is gated/gap-free, or noise "
                     "is continuous at speech level. Record 5s of room tone next "
                     "time; it makes this directly measurable.")

    # --- 4. de-ess ------------------------------------------------------
    sr = m.get("sibilance_ratio")
    if sr is not None and sr > -14:
        findings.append(
            f"SIBILANCE: 5-9kHz sits {sr:+.1f} dB relative to body. De-ess BEFORE "
            "compression, or the compressor pumps on every 's'.")
        chain.append("deesser=i=0.4:m=0.5:f=0.5")
    # --- 5. dynamics ----------------------------------------------------
    lra = m.get("lra")
    if lra is not None and lra > 12:
        findings.append(f"LOUDNESS RANGE {lra:.1f} LU — wide. Levels swing between "
                        "sections. Gentle compression will even it out.")
        chain.append("acompressor=threshold=-20dB:ratio=3:attack=8:release=180:makeup=2")
    elif lra is not None and lra < 4:
        findings.append(f"LOUDNESS RANGE {lra:.1f} LU — already very flat. Further "
                        "compression will make it lifeless.")
        notes.append("Skipping compression; the source is already controlled.")
    else:
        chain.append("acompressor=threshold=-18dB:ratio=2.5:attack=10:release=200:makeup=1.5")

    # --- 6. presence + limit + loudness ---------------------------------
    chain.append("equalizer=f=3000:t=q:w=1.2:g=1.5")   # intelligibility, gentle
    chain.append(f"alimiter=limit={10 ** (m['target_tp'] / 20):.4f}:level=disabled")

    ln = m.get("_ln")
    if ln:
        chain.append(
            f"loudnorm=I={m['target_i']}:TP={m['target_tp']}:LRA=11:"
            f"measured_I={ln['input_i']}:measured_LRA={ln['input_lra']}:"
            f"measured_TP={ln['input_tp']}:measured_thresh={ln['input_thresh']}:"
            f"offset={ln.get('target_offset', 0)}:linear=true")
    else:
        chain.append(f"loudnorm=I={m['target_i']}:TP={m['target_tp']}:LRA=11")

    li = m.get("integrated_lufs")
    if li is not None:
        delta = m["target_i"] - li
        findings.append(f"Integrated loudness {li:.1f} LUFS -> target "
                        f"{m['target_i']:.0f} ({delta:+.1f} LU).")
    return findings, chain, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--platform", choices=sorted(TARGETS), default="youtube")
    ap.add_argument("--target", type=float, help="override LUFS target")
    ap.add_argument("--true-peak", type=float, help="override dBTP ceiling")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--emit-chain", action="store_true",
                    help="print only the -af chain")
    args = ap.parse_args()

    ti, ttp = TARGETS[args.platform]
    if args.target is not None:
        ti = args.target
    if args.true_peak is not None:
        ttp = args.true_peak

    m = analyse(args.input, ti, ttp)
    findings, chain, notes = prescribe(m)

    if args.emit_chain:
        print(",".join(chain))
        return
    if args.json:
        m.pop("_ln", None)
        print(json.dumps({**m, "chain": chain, "findings": findings}, indent=2))
        return

    print(f"{args.input}  —  {m['sample_rate']} Hz, {m['channels']} ch, "
          f"target {args.platform} ({ti} LUFS / {ttp} dBTP)\n")
    print("MEASURED")
    for k, lbl, unit in [("integrated_lufs", "integrated loudness", "LUFS"),
                         ("lra", "loudness range", "LU"),
                         ("true_peak_dbtp", "true peak", "dBTP"),
                         ("noise_floor_db", "noise floor", "dB"),
                         ("snr_db", "signal-to-noise", "dB"),
                         ("rumble_ratio", "rumble vs body", "dB"),
                         ("sibilance_ratio", "sibilance vs body", "dB")]:
        v = m.get(k)
        print(f"  {lbl:<22} {v if v is None else f'{v:8.1f}'} {unit}")
    if m.get("room_tone_span"):
        s, e = m["room_tone_span"]
        print(f"  {'room tone candidate':<22} {s:.2f}-{e:.2f}s ({e-s:.2f}s)")

    print("\nFINDINGS")
    for f in findings:
        print(f"  - {f}")
    if notes:
        print("\nNOTES")
        for n in notes:
            print(f"  - {n}")

    print("\nCHAIN (order matters — repair, then tone, then dynamics, then level)")
    for i, c in enumerate(chain, 1):
        print(f"  {i:>2}. {c}")
    print("\nffmpeg -i IN -af \"\\\n      " +
          ",\\\n      ".join(chain) + "\" \\\n  -c:v copy OUT")
    print("\nNoise floor and SNR are ESTIMATES from the quietest passage found; "
          "they are\nless reliable than the loudness figures, which come from a "
          "proper R128 pass.\nTreat SNR as a rough band (clean / marginal / "
          "noisy), not a precise number.")
    print("\nListen before you ship it. These are starting values, not a master.")


if __name__ == "__main__":
    main()
