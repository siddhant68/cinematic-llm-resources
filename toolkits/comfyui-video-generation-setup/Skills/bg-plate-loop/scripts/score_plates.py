#!/usr/bin/env python3
"""
score_plates.py — Rank candidate background plates on the properties that
actually decide whether a plate works behind a talking head.

A plate is not chosen for being pretty. It is chosen for being *ignorable*. The
brief from the skill is: no object crossing frame, no rhythmic pulse, nothing the
eye can time, dark enough that the subject is clearly the brightest thing in
frame. Those are all measurable, so measure them rather than scrolling thumbnails.

  python score_plates.py candidates/*.mp4 --subject-luma 96
  python score_plates.py candidates/*.mp4 --json plates.json

Metrics, and why each one is here:

  brightness      mean luma. The subject must be brighter than the plate or the
                  eye goes to the background. Compared against --subject-luma,
                  which you get from the actual matted host clip.
  motion          mean absolute frame-to-frame difference. High motion competes
                  with the speaker.
  motion_peak     the worst single moment. A plate with low average motion and
                  one big event still has the event, and the event is what the
                  viewer notices.
  periodicity     autocorrelation of the motion signal. This is the "rhythmic
                  pulse" test — a plate that throbs on a beat becomes a metronome
                  the viewer starts counting.
  seam            PSNR between the first and last frame. Above ~40 dB the clip
                  loops without a visible cut; below ~25 dB it will jump.
  busyness        mean spatial gradient. A detailed plate fights caption legibility.

The score is a weighted sum, but read the columns rather than the score — the
weighting encodes one opinion about one kind of video.
"""

import argparse
import json
import os
import re
import subprocess
import sys

import numpy as np

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")


def probe(path):
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    v = r.stdout.split()
    if len(v) < 4:
        return None
    num, den = v[2].split("/")
    return int(v[0]), int(v[1]), float(num) / float(den), float(v[3])


def frames(path, n, w=96):
    """n evenly spaced greyscale frames as a (n, h, w) array."""
    info = probe(path)
    if not info:
        return None
    W, H, fps, dur = info
    h = max(2, int(round(w * H / W)))
    r = subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-i", path,
         "-vf", f"fps={max(1, n / max(dur, 0.1)):.6f},scale={w}:{h},format=gray",
         "-frames:v", str(n), "-f", "rawvideo", "-"],
        capture_output=True)
    buf = r.stdout
    got = len(buf) // (w * h)
    if got < 3:
        return None
    return np.frombuffer(buf[:got * w * h], dtype=np.uint8).reshape(got, h, w).astype(np.float32)


def seam_psnr(path):
    """First frame vs last frame. Identical endpoints make a loop *compatible*;
    they do not make it seamless, because velocity can still mismatch. This
    catches the gross case, which is most of them."""
    info = probe(path)
    if not info:
        return None
    d = info[3]
    outs = []
    for args in (["-i", path, "-vf", "select=eq(n\\,0)"],
                 ["-sseof", "-0.05", "-i", path]):
        r = subprocess.run(
            [FFMPEG, "-hide_banner", "-loglevel", "error"] + args
            + ["-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray",
               "-vf" if "-vf" not in args else "-filter:v",
               "scale=192:108,format=gray", "-"],
            capture_output=True)
        outs.append(r.stdout)
    if not all(outs) or len(outs[0]) != len(outs[1]):
        return None
    a = np.frombuffer(outs[0], dtype=np.uint8).astype(np.float32)
    b = np.frombuffer(outs[1], dtype=np.uint8).astype(np.float32)
    mse = float(((a - b) ** 2).mean())
    if mse < 1e-9:
        return 99.0
    return float(10 * np.log10(255.0 ** 2 / mse))


def periodicity(motion):
    """Peak autocorrelation at a non-trivial lag: does the motion repeat on a
    beat? A value near 1 means a strong pulse."""
    m = motion - motion.mean()
    if m.std() < 1e-6 or len(m) < 8:
        return 0.0
    m = m / m.std()
    n = len(m)
    best = 0.0
    for lag in range(2, max(3, n // 2)):
        c = float((m[:-lag] * m[lag:]).mean())
        best = max(best, c)
    return best


def score_one(path, subject_luma, n=64):
    f = frames(path, n)
    if f is None:
        return None
    info = probe(path)
    W, H, fps, dur = info
    bright = float(f.mean())
    diffs = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    motion = float(diffs.mean())
    motion_peak = float(diffs.max())
    # Periodicity is only meaningful when there IS motion. On a near-still plate
    # the autocorrelation is measuring compression noise, and it will happily
    # report a strong "pulse" in a clip nothing is moving in.
    per = periodicity(diffs) if diffs.mean() >= 0.35 else 0.0
    gx = np.abs(np.diff(f, axis=2)).mean()
    gy = np.abs(np.diff(f, axis=1)).mean()
    busy = float((gx + gy) / 2)
    seam = seam_psnr(path)

    # weighted, and deliberately harsh about brightness and events
    head = max(0.0, subject_luma - bright)          # how much darker than subject
    s = 0.0
    s += min(head / 40.0, 1.0) * 30                 # dark enough
    s += max(0.0, 1 - motion / 6.0) * 22            # calm
    s += max(0.0, 1 - motion_peak / 14.0) * 16      # no events
    s += max(0.0, 1 - per) * 12                     # no pulse
    s += max(0.0, 1 - busy / 12.0) * 10             # not busy
    s += (min((seam or 0) / 40.0, 1.0)) * 10        # loops
    return {"file": os.path.basename(path), "path": os.path.abspath(path),
            "w": W, "h": H, "fps": round(fps, 3), "duration": round(dur, 2),
            "brightness": round(bright, 1), "motion": round(motion, 2),
            "motion_peak": round(motion_peak, 2),
            "periodicity": round(per, 2), "busyness": round(busy, 2),
            "seam_psnr": round(seam, 1) if seam else None,
            "score": round(s, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--subject-luma", type=float, default=100.0,
                    help="mean luma of the matted subject. Measure it — the plate "
                         "must be darker than this or the eye goes to the "
                         "background instead of the speaker.")
    ap.add_argument("--json")
    a = ap.parse_args()

    rows = []
    for p in a.inputs:
        r = score_one(p, a.subject_luma)
        if r:
            rows.append(r)
        else:
            print(f"  could not read {p}")
    if not rows:
        sys.exit("nothing scored")
    rows.sort(key=lambda r: -r["score"])

    print(f"\n{'='*100}")
    print(f"PLATE CANDIDATES   (subject luma {a.subject_luma:.0f})")
    print(f"{'='*100}")
    print(f"  {'file':<32}{'score':>6}{'bright':>8}{'motion':>8}{'peak':>7}"
          f"{'pulse':>7}{'busy':>7}{'seam':>7}{'dur':>7}")
    print(f"  {'-'*32}{'-'*6}{'-'*8}{'-'*8}{'-'*7}{'-'*7}{'-'*7}{'-'*7}{'-'*7}")
    for r in rows:
        print(f"  {r['file'][:32]:<32}{r['score']:>6.1f}{r['brightness']:>8.1f}"
              f"{r['motion']:>8.2f}{r['motion_peak']:>7.2f}{r['periodicity']:>7.2f}"
              f"{r['busyness']:>7.2f}"
              f"{(r['seam_psnr'] if r['seam_psnr'] else 0):>7.1f}"
              f"{r['duration']:>7.1f}")

    b = rows[0]
    print(f"\n  BEST BY SCORE: {b['file']}")
    notes = []
    if b["brightness"] > a.subject_luma - 15:
        notes.append("close to the subject in brightness — darken it before use")
    if b["motion"] > 4:
        notes.append("more motion than a plate wants; blur and slow it")
    if b["periodicity"] > 0.55 and b["motion"] >= 0.35:
        notes.append("motion repeats on a beat — the viewer will start timing it")
    if b["seam_psnr"] and b["seam_psnr"] < 25:
        notes.append("does not loop cleanly; cut to a section that does, or "
                     "cross-fade the seam")
    if b["busyness"] > 10:
        notes.append("visually busy — captions will fight it")
    for n_ in notes:
        print(f"    - {n_}")
    if not notes:
        print("    - no flags; still watch three loops before accepting it")

    print("\n  Every plate here still needs the same treatment: blur beyond what "
          "feels\n  necessary, and darken until the subject is clearly the "
          "brightest thing in\n  frame. A plate you notice is a plate that is "
          "too good.")

    if a.json:
        with open(a.json, "w") as f:
            json.dump(rows, f, indent=2)
        print(f"\n  wrote {a.json}")
    print()


if __name__ == "__main__":
    main()
