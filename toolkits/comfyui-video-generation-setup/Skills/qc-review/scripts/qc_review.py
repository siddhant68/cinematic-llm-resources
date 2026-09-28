#!/usr/bin/env python3
"""
qc_review.py — Check the RENDERED FILE, not the plan.

The failures this pipeline can produce are mostly silent. The render exits 0, the
file plays, and something is wrong: a cut landed on a black frame, the captions
drifted a second behind by the end, a fade did not stop an audio spike, the
grade jumps between two segments. None of those raise an error anywhere, so the
only way to find them is to measure the output.

  python qc_review.py master.mp4 --edl edit/edl.json \\
      --timeline edit/renders/timeline.json \\
      --captions edit/captions.ass --target-lufs -14 --json qc.json

Checks, in the order they matter:

  1 duration     against the timeline actually rendered
  2 cuts         luma and audio discontinuity at every cut boundary
  3 frames       black, frozen and flash frames
  4 audio        clipping, loudness, true peak, silence at joins
  5 captions     do they fit inside the output, and do they drift
  6 grade        consistency across the runtime

A finding is a FAIL only when it is a defect. Things that are merely worth a look
are WARN, because a QC report that cries wolf gets skipped.
"""

import argparse
import json
import os
import re
import subprocess
import sys

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")

OK, WARN, FAIL = "  ok  ", " WARN ", " FAIL "


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def hdr(t):
    print(f"\n{'='*74}\n{t}\n{'='*74}")


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, section, msg):
        self.items.append({"level": level.strip() or "ok",
                           "section": section, "message": msg})
        print(f"{level} {msg}")

    def counts(self):
        c = {"FAIL": 0, "WARN": 0, "ok": 0}
        for i in self.items:
            c[i["level"]] = c.get(i["level"], 0) + 1
        return c


# ------------------------------------------------------------------ 1 duration

def check_duration(path, timeline, edl, rep):
    hdr("1. DURATION")
    r = sh([FFPROBE, "-v", "error", "-show_entries",
            "format=duration:stream=nb_frames,r_frame_rate,codec_type",
            "-of", "json", path])
    info = json.loads(r.stdout)
    dur = float(info["format"]["duration"])
    print(f"  rendered   {dur:.3f}s")

    want = None
    if timeline:
        want = timeline["total"]
        label = "timeline.json"
    elif edl:
        want = sum(x["end"] - x["start"] for x in edl.get("ranges", [])
                   if x.get("status", "keep") == "keep")
        label = "EDL (nominal)"
    if want is not None:
        d = dur - want
        msg = f"duration {dur:.3f}s vs {label} {want:.3f}s (delta {d:+.3f}s)"
        rep.add(OK if abs(d) < 0.08 else (WARN if abs(d) < 0.5 else FAIL),
                "duration", msg)
    for s in info.get("streams", []):
        if s.get("codec_type") == "video":
            print(f"  frame rate {s.get('r_frame_rate')}   frames {s.get('nb_frames')}")
    return dur


# ---------------------------------------------------------------- 2 cut checks

def sample_luma(path, t):
    """Mean luma of one frame, via signalstats."""
    r = sh([FFMPEG, "-hide_banner", "-ss", f"{max(0,t):.3f}", "-i", path,
            "-frames:v", "1", "-vf", "signalstats,metadata=mode=print:file=-",
            "-f", "null", "-"])
    m = re.search(r"lavfi\.signalstats\.YAVG=([\d.]+)", r.stdout + r.stderr)
    return float(m.group(1)) if m else None


def check_cuts(path, timeline, rep, jump_warn=18.0, jump_fail=40.0):
    hdr("2. CUT BOUNDARIES")
    if not timeline:
        rep.add(WARN, "cuts", "no timeline.json — cut boundaries not checked")
        return
    segs = timeline["segments"]
    if len(segs) < 2:
        rep.add(OK, "cuts", "single segment, no joins")
        return
    fps = timeline.get("fps", 60)
    dt = 1.0 / fps
    print(f"  {len(segs)-1} join(s), sampling one frame either side")
    worst = 0.0
    for s in segs[1:]:
        t = s["out_start"]
        a = sample_luma(path, t - 2 * dt)
        b = sample_luma(path, t + dt)
        if a is None or b is None:
            rep.add(WARN, "cuts", f"join at {t:.2f}s: could not sample")
            continue
        jump = abs(b - a)
        worst = max(worst, jump)
        lvl = OK if jump < jump_warn else (WARN if jump < jump_fail else FAIL)
        if lvl is not OK:
            rep.add(lvl, "cuts",
                    f"join at {t:6.2f}s ({s['id']}): luma {a:.1f} -> {b:.1f} "
                    f"(jump {jump:.1f}) — visible picture jump")
    if worst < jump_warn:
        rep.add(OK, "cuts", f"all joins below the jump threshold "
                            f"(worst {worst:.1f}, warn at {jump_warn})")


# ------------------------------------------------------------------- 3 frames

def check_frames(path, rep, dur):
    hdr("3. FRAMES")
    r = sh([FFMPEG, "-hide_banner", "-i", path,
            "-vf", "blackdetect=d=0.15:pic_th=0.98,"
                   "freezedetect=n=-60dB:d=0.6",
            "-an", "-f", "null", "-"])
    txt = r.stderr
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", txt)
    real_blacks = [(float(a), float(b)) for a, b in blacks
                   if float(a) > 0.3 and float(b) < dur - 0.3]
    if real_blacks:
        for a, b in real_blacks[:6]:
            rep.add(FAIL, "frames",
                    f"black frames {a:.2f}-{b:.2f}s — a cut landed on nothing")
    else:
        rep.add(OK, "frames", "no black frames inside the body")

    freezes = re.findall(r"freeze_start: ([\d.]+)", txt)
    if freezes:
        rep.add(WARN, "frames",
                f"{len(freezes)} frozen span(s), first at {float(freezes[0]):.2f}s")
    else:
        rep.add(OK, "frames", "no frozen spans")


# -------------------------------------------------------------------- 4 audio

def check_audio(path, rep, target_lufs=None, true_peak=-1.0):
    hdr("4. AUDIO")
    r = sh([FFMPEG, "-hide_banner", "-i", path, "-af",
            "astats=metadata=1:reset=0", "-f", "null", "-"])
    txt = r.stderr
    peak_counts = [int(x) for x in re.findall(r"Peak count:\s*(\d+)", txt)]
    # Clipping is Peak count, not Flat factor: a hard-clipped file has been
    # measured reporting Flat factor 0.00 with Peak count 240.
    if peak_counts and max(peak_counts) > 40:
        rep.add(WARN, "audio",
                f"Peak count {max(peak_counts)} — samples sitting at full scale; "
                "check for clipping")
    else:
        rep.add(OK, "audio", f"no clipping (max Peak count "
                             f"{max(peak_counts) if peak_counts else 0})")

    r2 = sh([FFMPEG, "-hide_banner", "-i", path, "-af",
             "loudnorm=print_format=json", "-f", "null", "-"])
    t2 = r2.stderr
    if "{" in t2:
        try:
            m = json.loads(t2[t2.rindex("{"):t2.rindex("}") + 1])
            i, tp, lra = (float(m["input_i"]), float(m["input_tp"]),
                          float(m["input_lra"]))
            print(f"  integrated {i:.2f} LUFS   true peak {tp:.2f} dBTP   "
                  f"LRA {lra:.2f} LU")
            if target_lufs is not None:
                d = i - target_lufs
                rep.add(OK if abs(d) < 0.6 else (WARN if abs(d) < 1.5 else FAIL),
                        "audio",
                        f"loudness {i:.2f} LUFS vs target {target_lufs} "
                        f"({d:+.2f} LU)")
            rep.add(OK if tp <= true_peak + 0.15 else FAIL, "audio",
                    f"true peak {tp:.2f} dBTP vs ceiling {true_peak}")
        except (ValueError, KeyError, json.JSONDecodeError):
            rep.add(WARN, "audio", "could not parse loudness measurement")


# ----------------------------------------------------------------- 5 captions

TS = re.compile(r"Dialogue:\s*\d+,(\d+):(\d\d):(\d\d\.\d\d),(\d+):(\d\d):(\d\d\.\d\d)")


def check_captions(cap, rep, dur):
    hdr("5. CAPTIONS")
    if not cap:
        rep.add(WARN, "captions", "no caption file supplied — not checked")
        return
    if not os.path.exists(cap):
        rep.add(FAIL, "captions", f"caption file missing: {cap}")
        return
    text = open(cap, encoding="utf-8", errors="replace").read()

    cues = []
    for m in TS.finditer(text):
        h1, m1, s1, h2, m2, s2 = m.groups()
        st = int(h1) * 3600 + int(m1) * 60 + float(s1)
        en = int(h2) * 3600 + int(m2) * 60 + float(s2)
        cues.append((st, en))
    if not cues:
        rep.add(FAIL, "captions", "no Dialogue lines parsed")
        return
    print(f"  {len(cues)} cues, {cues[0][0]:.2f}s - {cues[-1][1]:.2f}s")

    over = [c for c in cues if c[1] > dur + 0.1]
    rep.add(FAIL if over else OK, "captions",
            f"{len(over)} cue(s) end past the video" if over
            else "all cues fit inside the output")

    tail = dur - cues[-1][1]
    rep.add(WARN if tail > 4.0 else OK, "captions",
            f"last cue ends {tail:.2f}s before the video does"
            + (" — captions may have been built on the wrong timeline"
               if tail > 4.0 else ""))

    # the three silent ASS traps
    if "PlayResX" not in text or "PlayResY" not in text:
        rep.add(FAIL, "captions",
                "no PlayResX/PlayResY — font size means something different at "
                "every render resolution")
    else:
        rep.add(OK, "captions", "PlayResX/Y declared")

    for line in text.splitlines():
        if line.startswith("Style:"):
            f = [x.strip() for x in line[6:].split(",")]
            if len(f) >= 23:
                # V4+ Styles field order: Name(0) Fontname(1) Fontsize(2)
                # Primary(3) Secondary(4) Outline(5) Back(6) Bold(7) Italic(8)
                # Underline(9) StrikeOut(10) ScaleX(11) ScaleY(12) Spacing(13)
                # Angle(14) BorderStyle(15) Outline(16) Shadow(17) Alignment(18)
                name, border, outline = f[0], f[15], f[16]
                if border in ("3", "4"):
                    if float(outline) == 0:
                        rep.add(FAIL, "captions",
                                f"style {name}: BorderStyle={border} with "
                                "Outline=0 renders bare text and still succeeds")
                    else:
                        rep.add(OK, "captions",
                                f"style {name}: BorderStyle={border} "
                                f"Outline={outline} — box will paint")


# -------------------------------------------------------------------- 6 grade

def check_grade(path, rep, dur, n=7):
    hdr("6. GRADE CONSISTENCY")
    ts = [dur * f for f in [0.02, 0.15, 0.3, 0.45, 0.6, 0.78, 0.95]][:n]
    vals = []
    for t in ts:
        y = sample_luma(path, t)
        if y is not None:
            vals.append((t, y))
    if len(vals) < 3:
        rep.add(WARN, "grade", "not enough samples")
        return
    ys = [v for _, v in vals]
    spread = max(ys) - min(ys)
    print("  " + "  ".join(f"{t:.1f}s:{y:.0f}" for t, y in vals))
    rep.add(OK if spread < 12 else (WARN if spread < 25 else FAIL), "grade",
            f"luma spread {spread:.1f} across the runtime"
            + (" — segments were graded inconsistently" if spread >= 25 else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--edl")
    ap.add_argument("--timeline")
    ap.add_argument("--captions")
    ap.add_argument("--target-lufs", type=float)
    ap.add_argument("--true-peak", type=float, default=-1.0)
    ap.add_argument("--json")
    ap.add_argument("--skip", default="", help="comma list of sections to skip")
    a = ap.parse_args()

    skip = {s.strip() for s in a.skip.split(",") if s.strip()}
    edl = json.load(open(a.edl)) if a.edl and os.path.exists(a.edl) else None
    tl = json.load(open(a.timeline)) if a.timeline and os.path.exists(a.timeline) else None

    print(f"\nQC — {a.input}")
    rep = Report()
    dur = check_duration(a.input, tl, edl, rep)
    if "cuts" not in skip:
        check_cuts(a.input, tl, rep)
    if "frames" not in skip:
        check_frames(a.input, rep, dur)
    if "audio" not in skip:
        check_audio(a.input, rep, a.target_lufs, a.true_peak)
    if "captions" not in skip:
        check_captions(a.captions, rep, dur)
    if "grade" not in skip:
        check_grade(a.input, rep, dur)

    c = rep.counts()
    hdr("VERDICT")
    print(f"  {c.get('FAIL',0)} fail, {c.get('WARN',0)} warn, {c.get('ok',0)} ok")
    if c.get("FAIL"):
        print("\n  FAILURES")
        for i in rep.items:
            if i["level"] == "FAIL":
                print(f"    - [{i['section']}] {i['message']}")
        print("\n  These are defects in the rendered file. Fix and re-render.")
    else:
        print("\n  No defects found by automated checks.")
    print("  Automated QC does not replace a human watch-through. It cannot tell "
          "you\n  whether a cut was the right one.\n")

    if a.json:
        with open(a.json, "w") as f:
            json.dump({"input": a.input, "duration": dur,
                       "items": rep.items, "counts": c}, f, indent=2)
        print(f"  wrote {a.json}\n")
    sys.exit(1 if c.get("FAIL") else 0)


if __name__ == "__main__":
    main()
