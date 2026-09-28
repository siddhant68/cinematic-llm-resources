#!/usr/bin/env python3
"""Check a thumbnail against the things that can be measured.

    thumb_qc.py thumb.png
    thumb_qc.py thumb.png --json report.json
    thumb_qc.py thumb.png --proof proof.png    # writes the 120px view

A clean report means shippable, not good. The 120px proof image is the part
worth actually looking at: that is the size where the click gets decided.
"""

import argparse
import json
import os
import sys

try:
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit("error: needs pillow and numpy")

W, H = 1280, 720
MAX_BYTES = 2 * 1024 * 1024
FEED_W = 120                      # a thumbnail in a phone feed
BADGE = (190, 60)                 # bottom-right duration badge, in 1280x720 px
EDGE_FRAC = 0.04                  # outer band that different surfaces may crop


def luma(img):
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def check(path, proof_path=None):
    res, fails, warns = {}, [], []
    img = Image.open(path)
    size_bytes = os.path.getsize(path)

    # --- hard API constraints -------------------------------------------
    res["dimensions"] = f"{img.width}x{img.height}"
    if (img.width, img.height) != (W, H):
        fails.append(f"dimensions {img.width}x{img.height}, must be {W}x{H}")

    res["bytes"] = size_bytes
    res["mb"] = round(size_bytes / 1024 / 1024, 2)
    if size_bytes > MAX_BYTES:
        fails.append(f"{res['mb']} MB exceeds the 2 MB upload limit")

    if img.format not in ("PNG", "JPEG", "GIF", "BMP"):
        fails.append(f"format {img.format} not accepted by YouTube")
    res["format"] = img.format

    full = luma(img)

    # --- global contrast -------------------------------------------------
    std = float(full.std())
    res["contrast_std"] = round(std, 1)
    if std < 45:
        fails.append(f"luma std {std:.1f} < 45 — too flat, will disappear in a feed")
    elif std < 55:
        warns.append(f"luma std {std:.1f} is low; consider more separation")

    # --- the 120px test --------------------------------------------------
    feed_h = round(FEED_W * H / W)
    feed = img.convert("RGB").resize((FEED_W, feed_h), Image.LANCZOS)
    fl = luma(feed)
    feed_std = float(fl.std())
    res["feed_contrast_std"] = round(feed_std, 1)
    if feed_std < 38:
        fails.append(
            f"at {FEED_W}px the image flattens to std {feed_std:.1f} — "
            "detail is not surviving downscale"
        )

    # Bright text on a dark ground (or the reverse) leaves high-frequency edges
    # after downscaling. If almost none survive, the type is unreadable there.
    gx = np.abs(np.diff(fl, axis=1)).mean()
    gy = np.abs(np.diff(fl, axis=0)).mean()
    edge = float((gx + gy) / 2)
    res["feed_edge_energy"] = round(edge, 2)
    if edge < 4.0:
        warns.append(
            f"low edge energy at {FEED_W}px ({edge:.1f}) — text or subject may be mush"
        )

    # --- focal dominance -------------------------------------------------
    # How much of the frame is meaningfully brighter than the median? A single
    # subject should own a chunk of the frame without filling it.
    med = float(np.median(full))
    bright = float((full > med + 28).mean())
    res["bright_fraction"] = round(bright, 3)
    if bright < 0.08:
        warns.append(f"only {bright:.0%} of the frame carries emphasis — no clear subject")
    elif bright > 0.62:
        warns.append(f"{bright:.0%} of the frame is emphasised — nothing dominates")

    # --- duration-badge safe zone ----------------------------------------
    badge = full[H - BADGE[1]:, W - BADGE[0]:]
    badge_var = float(badge.std())
    res["badge_zone_std"] = round(badge_var, 1)
    if badge_var > 30:
        warns.append(
            "content in the bottom-right duration-badge zone "
            f"(std {badge_var:.0f}); the badge will cover it"
        )

    # --- edge safety -----------------------------------------------------
    ex, ey = int(W * EDGE_FRAC), int(H * EDGE_FRAC)
    inner = np.zeros_like(full, dtype=bool)
    inner[ey:H - ey, ex:W - ex] = True
    outer_energy = float(np.abs(np.diff(full, axis=1))[~inner[:, 1:]].mean())
    res["edge_band_energy"] = round(outer_energy, 2)
    if outer_energy > 18:
        warns.append(
            f"busy outer {EDGE_FRAC:.0%} band (energy {outer_energy:.0f}) — "
            "may be cropped on some surfaces"
        )

    if proof_path:
        # A strip: the real size, then a 3x nearest-neighbour blow-up of it,
        # so the mush is visible without squinting at a 120px image.
        big = feed.resize((FEED_W * 3, feed_h * 3), Image.NEAREST)
        sheet = Image.new("RGB", (FEED_W * 4 + 24, feed_h * 3), (16, 20, 26))
        sheet.paste(feed, (8, (feed_h * 3 - feed_h) // 2))
        sheet.paste(big, (FEED_W + 16, 0))
        sheet.save(proof_path)
        res["proof"] = proof_path

    return res, fails, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--json", help="write the report here")
    ap.add_argument("--proof", help="write a 120px proof image here")
    args = ap.parse_args()

    res, fails, warns = check(args.image, args.proof)

    print(f"\n  {os.path.basename(args.image)}")
    for k, v in res.items():
        print(f"    {k:22s} {v}")
    for w in warns:
        print(f"    warn   {w}")
    for f in fails:
        print(f"    FAIL   {f}")
    verdict = "FAIL" if fails else ("ok, with warnings" if warns else "ok")
    print(f"    {'verdict':22s} {verdict}\n")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"metrics": res, "fails": fails, "warnings": warns}, fh, indent=2)

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
