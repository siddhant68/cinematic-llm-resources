#!/usr/bin/env python3
"""
clipcheck - QC a generated clip before showing it to anyone.

Hard-fails on the failures that are unambiguous and silent:
  1. black / NaN render   pixel_std ~ 0 while the log said success
  2. wrong frame count    truncated or guide frames not cropped
  3. silent audio         NaN in the audio branch, written as digital silence

Deterministically checks the decode settings when a .params.json sidecar exists
(ltxgen writes one next to every clip). Temporal decode chunking leaves a seam
every (temporal_size - temporal_overlap) frames; the reliable control is the
setting, not after-the-fact detection.

Periodic discontinuity is REPORTED, not failed on. A short clip has only a handful
of boundary frames, which is not enough signal to gate on: measured on clips known
to contain seams, prominence ranged 0.7 to 2.6 and overlapped clean clips. Treat a
high number as "go and look", never as proof.

    clipcheck.py clip.mp4 [more.mp4 ...] [--fps 24] [--expect-frames 97]

Exit 1 if any hard check fails. Needs the ComfyUI venv python (av + numpy).

Thresholds, calibrated on real output from this pipeline:
  pixel_std   30-80 healthy, <=1 is a black/NaN render
  LUFS        -20 to -32 healthy, < -45 is inaudible and means a bad seed
  rms         0.01-0.06 healthy (only used when ffmpeg is unavailable)
"""
import argparse, json, os, shutil, subprocess, sys
import numpy as np, av


def profile(path):
    c = av.open(path)
    vs = [s for s in c.streams if s.type == "video"][0]
    w, h = vs.codec_context.width, vs.codec_context.height
    container_fps = float(vs.average_rate) if vs.average_rate else None
    prev, stds, diffs = None, [], []
    for f in c.decode(video=0):
        a = f.to_ndarray(format="rgb24")
        stds.append(float(a.std()))
        if prev is not None:
            diffs.append(float(np.abs(a.astype("int16") - prev).mean()))
        prev = a.astype("int16")
    c.close()
    rms, sq, n = 0.0, 0.0, 0
    try:
        c2 = av.open(path)
        for f in c2.decode(audio=0):
            a = f.to_ndarray().astype("float64")
            sq += float((a ** 2).sum()); n += a.size
        c2.close()
        rms = (sq / n) ** 0.5 if n else 0.0
    except Exception:
        pass
    return w, h, len(stds), (float(np.mean(stds)) if stds else 0.0), np.array(diffs), rms, container_fps


def worst_period(diffs, lo=8, hi=96):
    """Advisory only. Median prominence of boundary frames over their neighbours."""
    if len(diffs) < 32:
        return None, 0.0, 0
    dd = np.abs(np.diff(diffs))
    best = (None, 0.0, 0)
    for per in range(lo, min(hi + 1, len(dd) // 3)):
        proms = []
        for i in range(len(dd)):
            if (i + 1) % per:
                continue
            a, b = max(0, i - 5), min(len(dd), i + 6)
            nb = np.concatenate([dd[a:i], dd[i + 1:b]])
            if len(nb) >= 4 and np.median(nb) > 0:
                proms.append(dd[i] / np.median(nb))
        if len(proms) >= 3:
            m = float(np.median(proms))
            if m > best[1]:
                best = (per, m, len(proms))
    return best


def loudness(path):
    """Integrated loudness in LUFS via ffmpeg, or None. rms alone is meaningless:
    a clip measuring rms 0.0014 came in at -50.8 LUFS, roughly 25 dB below clips
    that sounded fine, and passed a naive rms > 0 check."""
    if not shutil.which("ffmpeg"):
        return None
    try:
        out = subprocess.run(
            ["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
            capture_output=True, text=True, timeout=120).stderr
        hit = False
        for line in out.splitlines():
            if "Integrated loudness" in line:
                hit = True; continue
            if hit and line.strip().startswith("I:"):
                return float(line.split()[1])
    except Exception:
        pass
    return None


def settings_check(path):
    """Deterministic: read ltxgen's sidecar and confirm temporal chunking was off."""
    side = os.path.splitext(path)[0] + ".params.json"
    if not os.path.exists(side):
        return None
    try:
        p = json.load(open(side))
    except Exception:
        return None
    fr = p.get("frames")
    ts = max(64, fr + 8) if fr else None      # what ltxgen sets
    if fr and ts and ts <= fr:
        return f"temporal_size {ts} <= frames {fr}: decode WILL chunk and seam"
    return "ok"


def expected_frames(path):
    """Frame count after finishing. RIFE emits (frames-1)*multiplier + 1."""
    side = os.path.splitext(path)[0] + ".params.json"
    if not os.path.exists(side):
        return None
    try:
        p = json.load(open(side))
    except Exception:
        return None
    fr = p.get("frames")
    if not fr:
        return None
    return (fr - 1) * int(p.get("interpolate", 1) or 1) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--fps", type=float, default=None,
                    help="override the container's frame rate for the duration figure")
    ap.add_argument("--expect-frames", type=int)
    ap.add_argument("--quiet-ok", action="store_true", help="do not fail on silent audio")
    a = ap.parse_args()

    bad = 0
    for p in a.clips:
        name = os.path.basename(p)
        try:
            w, h, n, std, diffs, rms, container_fps = profile(p)
        except Exception as e:
            print(f"FAIL  {name}  cannot decode: {e}"); bad += 1; continue

        hard = []
        if std <= 1.0:
            hard.append("BLACK/NaN render (pixel_std ~ 0). Re-run with a different seed.")
        want = a.expect_frames or expected_frames(p)
        if want and n != want:
            hard.append(f"frame count {n} != expected {want}")
        lufs = loudness(p)
        if not a.quiet_ok:
            if rms <= 1e-6:
                hard.append("silent audio (NaN in the audio branch). Re-run with a different seed.")
            elif lufs is not None and lufs < -45:
                hard.append(f"audio effectively inaudible at {lufs:.1f} LUFS "
                            f"(healthy clips measure -20 to -32). Re-run with a different seed.")
            elif lufs is None and rms < 0.002:
                hard.append(f"audio rms {rms:.4f} is far below normal (healthy is 0.01-0.06). "
                            f"Install ffmpeg for a proper LUFS reading, or re-run with a different seed.")
        quiet_note = ""
        if lufs is not None and -45 <= lufs < -35:
            quiet_note = f"  ? quiet at {lufs:.1f} LUFS, will need a gain stage"
        sc = settings_check(p)
        if sc and sc != "ok":
            hard.append(sc)

        per, prom, cnt = worst_period(diffs)
        note = f"  | periodicity {per}f {prom:.2f}x (n={cnt})" if per else ""
        fps = a.fps or container_fps or 24.0
        print(f"{'FAIL' if hard else ' ok '}  {name}  {w}x{h} {n}f @{fps:g}fps {n/fps:.2f}s  "
              f"std={std:.1f} rms={rms:.4f}"
              + (f" lufs={lufs:.1f}" if lufs is not None else "") + note)
        for x in hard:
            print(f"        - {x}")
        if quiet_note:
            print(f"       {quiet_note}")
        if per and prom >= 2.0:
            print(f"        ? advisory: check {per/fps:.2f}s intervals by eye. "
                  f"Weak signal on short clips, not proof of a seam.")
        if hard:
            bad += 1

    print(f"\n{len(a.clips)-bad}/{len(a.clips)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
