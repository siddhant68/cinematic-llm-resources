#!/usr/bin/env python3
"""
build_captions.py — Word-level transcript -> ASS burn-in + SRT/VTT sidecar.

Exists because three caption bugs are easy to make by hand and invisible until
someone watches the whole video:

  1. ASS alpha is INVERTED. 00 = opaque, FF = transparent. Writing &HB3... for
     "70% opaque" actually gives 30%. This script takes opacity as 0..1 and
     converts correctly.
  2. ASS colour bytes are &HAABBGGRR -- alpha first, then BLUE GREEN RED.
     Hand-writing an RGB hex silently swaps red and blue.
  3. FontSize is meaningless without PlayResX/PlayResY. Without them libass
     guesses, and captions change size when the render resolution changes.

It also enforces reading speed, which is the difference between captions that
help and captions that stress the viewer.

USAGE
  python build_captions.py --transcript words.json --out-ass captions.ass \\
      --out-srt captions.srt --theme-color '#241A14' --play-res 1920x1080
  python build_captions.py ... --hero-lines heroes.txt
  python build_captions.py ... --check-only      # validate, write nothing
"""

import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------- ASS colour

def ass_colour(hex_rgb: str, opacity: float = 1.0) -> str:
    """'#RRGGBB' + opacity 0..1  ->  &HAABBGGRR.

    Alpha is inverted (00 opaque, FF transparent) and channel order is BGR.
    Both are common hand-written mistakes.
    """
    h = hex_rgb.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"expected #RRGGBB, got {hex_rgb!r}")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    opacity = max(0.0, min(1.0, opacity))
    a = int(round((1.0 - opacity) * 255))       # <-- the inversion
    return f"&H{a:02X}{b:02X}{g:02X}{r:02X}"


def ass_time(t: float) -> str:
    if t < 0:
        t = 0.0
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def srt_time(t: float) -> str:
    if t < 0:
        t = 0.0
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ---------------------------------------------------------------- input

def iter_words(node, depth=0):
    if depth > 6:
        return
    if isinstance(node, dict):
        for k in ("words", "word_timestamps"):
            if isinstance(node.get(k), list) and node[k]:
                for w in node[k]:
                    yield from iter_words(w, depth + 1)
                return
        if isinstance(node.get("segments"), list):
            for s in node["segments"]:
                yield from iter_words(s, depth + 1)
            return
        if ("word" in node or "text" in node) and "start" in node:
            yield node
        return
    if isinstance(node, list):
        for i in node:
            yield from iter_words(i, depth + 1)


def load_words(path):
    data = json.load(open(path))
    out = []
    for it in iter_words(data):
        if it.get("type") in ("audio_event", "spacing"):
            continue
        txt = (it.get("word") or it.get("text") or "").strip()
        if not txt:
            continue
        try:
            out.append((txt, float(it["start"]), float(it.get("end", it["start"]))))
        except (TypeError, ValueError):
            continue
    out.sort(key=lambda w: w[1])
    return out


# ---------------------------------------------------------------- grouping

SENTENCE_END = re.compile(r"[.!?]$")
CLAUSE_END = re.compile(r"[,;:]$")


def group_cues(words, max_chars, max_words, max_gap, min_dur, max_dur,
               hold=0.0, hold_gap=0.08, duration=None):
    """Break on sentence end, then clause end, then length, then silence.
    Breaking on a fixed word count alone splits phrases mid-thought."""
    cues, cur = [], []

    def flush():
        if cur:
            cues.append(list(cur))
            cur.clear()

    for i, (txt, st, en) in enumerate(words):
        prospective = " ".join(w[0] for w in cur + [(txt, st, en)])
        gap = st - cur[-1][2] if cur else 0.0
        if cur and (len(prospective) > max_chars or len(cur) >= max_words
                    or gap > max_gap):
            flush()
        cur.append((txt, st, en))
        if SENTENCE_END.search(txt):
            flush()
        elif CLAUSE_END.search(txt) and len(cur) >= max(3, max_words // 2):
            flush()
    flush()

    out = []
    for c in cues:
        st, en = c[0][1], c[-1][2]
        dur = en - st
        if dur < min_dur:
            en = st + min_dur
        elif dur > max_dur:
            en = st + max_dur
        out.append({"words": c, "start": st, "end": en,
                    "text": " ".join(w[0] for w in c)})
    # Hold each cue toward the next one, using the silence that follows it.
    #
    # Without this a cue disappears the instant the last word ends, so every
    # pause blanks the captions and the reading rate is computed over the
    # speaking time alone. On this footage that put 20 of 26 cues over the 17
    # chars/sec limit while the text was in fact on screen long enough — the
    # reader simply was not being given the pause. Holding is the standard fix
    # and it changes no text, only the out-time.
    if hold > 0:
        for i, c in enumerate(out):
            nxt = out[i + 1]["start"] if i + 1 < len(out) else None
            ceiling = c["start"] + max_dur
            if nxt is not None:
                ceiling = min(ceiling, nxt - hold_gap)
            elif duration is not None:
                # The last cue has no successor to bound it, so without the
                # output duration the hold runs off the end of the video and
                # the cue is simply never fully shown.
                ceiling = min(ceiling, duration - hold_gap)
            c["end"] = max(c["end"], min(c["end"] + hold, ceiling))
    if duration is not None:
        for c in out:
            c["end"] = min(c["end"], duration - 0.01)
        out[:] = [c for c in out if c["end"] > c["start"]]

    # prevent overlap after duration clamping
    for a, b in zip(out, out[1:]):
        if a["end"] > b["start"]:
            a["end"] = max(a["start"] + 0.4, b["start"] - 0.02)
    return out


def wrap_two_lines(text, max_chars):
    """Balanced two-line wrap, preferring a break at a clause boundary."""
    if len(text) <= max_chars:
        return text
    words = text.split()
    best, best_cost = None, None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) > max_chars or len(b) > max_chars:
            continue
        cost = abs(len(a) - len(b))
        if CLAUSE_END.search(words[i - 1]):
            cost -= 12                      # reward semantic breaks
        if best_cost is None or cost < best_cost:
            best, best_cost = (a, b), cost
    return "\\N".join(best) if best else text


# ---------------------------------------------------------------- validation

def validate(cues, max_cps, max_chars):
    issues = []
    for i, c in enumerate(cues):
        dur = c["end"] - c["start"]
        chars = len(c["text"])
        cps = chars / dur if dur > 0 else 999
        if cps > max_cps:
            issues.append(f"cue {i} @{c['start']:.2f}s: {cps:.1f} chars/sec "
                          f"(limit {max_cps}) — too fast to read: {c['text'][:44]!r}")
        for line in c["text"].split("\\N"):
            if len(line) > max_chars:
                issues.append(f"cue {i} @{c['start']:.2f}s: line {len(line)} chars "
                              f"(limit {max_chars})")
        if dur < 0.4:
            issues.append(f"cue {i} @{c['start']:.2f}s: {dur:.2f}s on screen — "
                          "below the 0.4s floor")
    return issues


# ---------------------------------------------------------------- output

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {px}
PlayResY: {py}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Body,{font},{size},{primary},{primary},{outline},{back},1,0,0,0,100,100,0,0,{border_style},{outline_w},0,2,{ml},{mr},{mv},1
Style: Hero,{hero_font},{hero_size},{hero_primary},{hero_primary},{outline},{hero_back},1,0,0,0,100,100,0,0,1,{hero_outline_w},0,{hero_align},{ml},{mr},{hero_mv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--out-ass")
    ap.add_argument("--out-srt")
    ap.add_argument("--out-vtt")
    ap.add_argument("--check-only", action="store_true")

    ap.add_argument("--play-res", default="1920x1080")
    ap.add_argument("--font", default="Inter")
    ap.add_argument("--font-size", type=int, default=54)
    ap.add_argument("--text-color", default="#FFFFFF")
    ap.add_argument("--theme-color", default="#241A14",
                    help="box colour sampled from the graded video")
    ap.add_argument("--box-opacity", type=float, default=0.70,
                    help="0..1 — converted to inverted ASS alpha correctly")
    ap.add_argument("--outline-color", default="#000000")
    ap.add_argument("--outline-width", type=float, default=0)
    ap.add_argument("--border-style", type=int, choices=[1, 3, 4], default=3,
                    help="1=outline 3=opaque box 4=per-line box (libass only)")
    ap.add_argument("--margin-v", type=int, default=140)
    ap.add_argument("--margin-h", type=int, default=180)

    ap.add_argument("--hero-lines", help="file of hero lines, one per line")
    ap.add_argument("--hero-font", default="Inter")
    ap.add_argument("--hero-size", type=int, default=84)
    ap.add_argument("--hero-color", default="#FFC15E")
    ap.add_argument("--hero-align", type=int, default=5, help="ASS \\an alignment")
    ap.add_argument("--hero-margin-v", type=int, default=0)

    ap.add_argument("--max-chars", type=int, default=42, help="per line")
    ap.add_argument("--max-words", type=int, default=9, help="per cue")
    ap.add_argument("--max-cps", type=float, default=17.0, help="chars/sec")
    ap.add_argument("--hold", type=float, default=1.2,
                    help="seconds a cue may be held into the following pause, "
                         "capped by --max-dur and the next cue. 0 disables.")
    ap.add_argument("--duration", type=float,
                    help="output duration in seconds. Supply it: without it the "
                         "final cue can be held past the end of the video.")
    ap.add_argument("--hold-gap", type=float, default=0.08,
                    help="minimum blank between consecutive cues")
    ap.add_argument("--max-gap", type=float, default=0.7)
    ap.add_argument("--min-dur", type=float, default=1.0)
    ap.add_argument("--max-dur", type=float, default=6.0)
    args = ap.parse_args()

    px, py = (int(v) for v in args.play_res.lower().split("x"))

    # BorderStyle 3/4 draw a BOX and reuse the Outline value as the box padding.
    # Outline=0 with BorderStyle=3 renders no box at all -- the caption appears
    # as bare text and the failure is silent. Enforce a usable padding.
    if args.border_style in (3, 4) and args.outline_width <= 0:
        args.outline_width = 8
        print("note: BorderStyle=%d uses Outline as box padding; "
              "raised Outline to 8 (0 would render no box)" % args.border_style)

    # Verified empirically against libass 0.17: under BorderStyle 3/4 the BOX is
    # painted from OutlineColour. BackColour is the shadow, and setting the theme
    # colour there renders nothing visible. Route the theme colour accordingly.
    if args.border_style in (3, 4):
        box_colour = ass_colour(args.theme_color, args.box_opacity)
        shadow_colour = ass_colour("#000000", 0.0)
    else:
        box_colour = ass_colour(args.outline_color, 1.0)
        shadow_colour = ass_colour(args.theme_color, args.box_opacity)
    words = load_words(args.transcript)
    if not words:
        sys.exit("No words parsed from transcript.")

    cues = group_cues(words, args.max_chars * 2, args.max_words,
                      args.max_gap, args.min_dur, args.max_dur,
                      args.hold, args.hold_gap, args.duration)
    for c in cues:
        c["text"] = wrap_two_lines(c["text"], args.max_chars)

    heroes = set()
    if args.hero_lines and os.path.exists(args.hero_lines):
        for ln in open(args.hero_lines):
            ln = re.sub(r"[^\w\s]", "", ln.lower()).strip()
            if ln:
                heroes.add(re.sub(r"\s+", " ", ln))

    def is_hero(c):
        t = re.sub(r"[^\w\s]", "", c["text"].replace("\\N", " ").lower())
        t = re.sub(r"\s+", " ", t).strip()
        return any(h in t or t in h for h in heroes)

    issues = validate(cues, args.max_cps, args.max_chars)
    n_hero = sum(1 for c in cues if is_hero(c))

    print(f"{len(words)} words -> {len(cues)} cues  ({n_hero} hero)")
    print(f"PlayRes {px}x{py}, font {args.font} {args.font_size}")
    print(f"box {args.theme_color} @ {args.box_opacity:.0%} -> "
          f"{ass_colour(args.theme_color, args.box_opacity)} "
          f"in {'OutlineColour' if args.border_style in (3,4) else 'BackColour'} "
          f"(BorderStyle={args.border_style})")
    if issues:
        print(f"\n{len(issues)} readability issue(s):")
        for i in issues[:20]:
            print("  " + i)
        if len(issues) > 20:
            print(f"  ... and {len(issues)-20} more")
    else:
        print("readability: OK")
    if heroes and n_hero == 0:
        print("\nWARNING: hero lines supplied but none matched a cue. Check that "
              "the hero text matches the spoken words, not the written script.")
    if n_hero > 8:
        print(f"\nWARNING: {n_hero} hero cues. Emphasis stops signalling above "
              "~6 in a long video.")

    if args.check_only:
        return

    if args.out_ass:
        header = ASS_HEADER.format(
            px=px, py=py, font=args.font, size=args.font_size,
            primary=ass_colour(args.text_color, 1.0),
            outline=box_colour,
            back=shadow_colour,
            border_style=args.border_style, outline_w=args.outline_width,
            ml=args.margin_h, mr=args.margin_h, mv=args.margin_v,
            hero_font=args.hero_font, hero_size=args.hero_size,
            hero_primary=ass_colour(args.hero_color, 1.0),
            hero_back=ass_colour("#000000", 0.0),
            hero_outline_w=3, hero_align=args.hero_align,
            hero_mv=args.hero_margin_v)
        lines = [header]
        for c in cues:
            style = "Hero" if is_hero(c) else "Body"
            lines.append(f"Dialogue: 0,{ass_time(c['start'])},{ass_time(c['end'])},"
                         f"{style},,0,0,0,,{c['text']}")
        open(args.out_ass, "w").write("\n".join(lines) + "\n")
        print(f"wrote {args.out_ass}")

    if args.out_srt:
        buf = []
        for i, c in enumerate(cues, 1):
            buf.append(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n"
                       f"{c['text'].replace(chr(92)+'N', chr(10))}\n")
        open(args.out_srt, "w").write("\n".join(buf))
        print(f"wrote {args.out_srt}  (accessibility sidecar — upload separately)")

    if args.out_vtt:
        buf = ["WEBVTT", ""]
        for c in cues:
            buf.append(f"{srt_time(c['start']).replace(',', '.')} --> "
                       f"{srt_time(c['end']).replace(',', '.')}")
            buf.append(c["text"].replace("\\N", "\n"))
            buf.append("")
        open(args.out_vtt, "w").write("\n".join(buf))
        print(f"wrote {args.out_vtt}")


if __name__ == "__main__":
    main()
