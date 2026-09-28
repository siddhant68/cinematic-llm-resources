#!/usr/bin/env python3
"""Render a thumbnail spec to a 1280x720 image via headless Chrome.

The thumbnail is HTML, so it is text: diffable, versionable, and regenerable.
Variants are a parameter change rather than a new prompt.

    render_thumbnail.py spec.json -o thumb.png
    render_thumbnail.py spec.json -o thumb.jpg --jpeg     # under the 2 MB cap
    render_thumbnail.py --list-templates

Chrome is used directly rather than Playwright: it is already installed on this
machine, it renders at an exact device pixel size, and it adds no dependency.
"""

import argparse
import base64
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(os.path.dirname(HERE), "templates")

WIDTH, HEIGHT = 1280, 720
MAX_BYTES = 2 * 1024 * 1024

BLANK_PIXEL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

# The channel palette. Amber is the caption-highlight colour already burned into
# every frame of every video, so reusing it here is free brand recognition.
DEFAULTS = {
    "template": "face-artifact",
    "accent": "#F5A524",
    "hot": "#FF6B35",
    "ground": "#2A2E33",
    "deep": "#10141A",
    "text_color": "#FFFFFF",
    "eyebrow": "",
    "text": [],
    "images": {},
    "font": "'Avenir Next Condensed', 'Helvetica Neue', Impact, sans-serif",
    "font_weight": "800",
    "tilt": "0",
    "subject_pos": "center top",
    "artifact_pos": "center center",
    "max_font": 210,
}

# Width in px the text block gets in each template. Type is fitted to this, so
# two short words render huge and four words render small — which is the honest
# feedback loop: if the type came out small, there are too many words.
TEXT_WIDTH = {
    "evidence": 1150,
    "face-artifact": 720,
    "contrast-pair": 540,
    "statement": 1120,
}
# Height the whole text stack may occupy, so type never buries the image.
BLOCK_HEIGHT = {
    "evidence": 430,
    "face-artifact": 540,
    "contrast-pair": 300,
    "statement": 560,
}
# Below this the type stops being readable in a 120px feed thumbnail.
MIN_READABLE = 140

# Fitting is done in the browser rather than estimated from character counts:
# glyph widths vary per face and a bad estimate wraps a line silently, which
# buries the image under type without reporting anything.
FIT_JS = """
<script>
(function () {
  var MAXF = {{MAXFONT}}, W = {{FITWIDTH}}, H = {{FITHEIGHT}}, MIN = 40, STACKED = {{STACKED}};
  var lines = [].slice.call(document.querySelectorAll('.type'))
                .filter(function (e) { return getComputedStyle(e).display !== 'none'
                                          && e.textContent.trim(); });
  if (!lines.length) return;

  // Measure the glyphs, not the box. A block element with a fixed width
  // reports that width as scrollWidth forever, so measuring the element
  // shrinks the type to the floor and reports nothing.
  var inners = lines.map(function (e) {
    var s = document.createElement('span');
    s.style.display = 'inline-block';
    s.style.whiteSpace = 'nowrap';
    s.textContent = e.textContent;
    e.textContent = '';
    e.appendChild(s);
    return s;
  });

  function fits(size) {
    var wide = 0, tall = 0;
    lines.forEach(function (e, i) {
      e.style.fontSize = size + 'px';
      wide = Math.max(wide, inners[i].offsetWidth);
      tall = STACKED ? tall + e.getBoundingClientRect().height
                     : Math.max(tall, e.getBoundingClientRect().height);
    });
    return wide <= W && tall <= H;
  }

  var size = MAXF;
  while (size > MIN && !fits(size)) size -= 2;
  lines.forEach(function (e) { e.style.fontSize = size + 'px'; });

  var m = document.createElement('meta');
  m.name = 'fitted-size'; m.content = size; document.head.appendChild(m);
})();
</script>
"""


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c and os.path.exists(c):
            return c
    sys.exit(
        "error: no Chrome/Chromium found.\n"
        "  Install Google Chrome, or pass --chrome /path/to/binary."
    )


def list_templates():
    if not os.path.isdir(TEMPLATE_DIR):
        return []
    return sorted(
        f[:-5] for f in os.listdir(TEMPLATE_DIR) if f.endswith(".html")
    )


def data_uri(path):
    """Embed an image so the rendered page has no external file dependencies."""
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        sys.exit(f"error: image not found: {path}")
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode("ascii")


def build_html(spec):
    name = spec["template"]
    tpl_path = os.path.join(TEMPLATE_DIR, name + ".html")
    if not os.path.exists(tpl_path):
        sys.exit(
            f"error: no template {name!r}.\n"
            f"  available: {', '.join(list_templates()) or '(none)'}"
        )
    with open(tpl_path) as fh:
        html = fh.read()

    base_path = os.path.join(TEMPLATE_DIR, "_base.css")
    base = open(base_path).read() if os.path.exists(base_path) else ""
    html = html.replace("{{BASECSS}}", base)

    lines = spec["text"] or []

    avail = TEXT_WIDTH.get(name, 1000)
    max_h = BLOCK_HEIGHT.get(name, 560)

    # Advisory only — the browser does the real fitting. This just flags copy
    # that is obviously too long before you look at the render.
    if lines:
        longest = max(lines, key=len)
        est = int(avail / (max(len(longest), 1) * 0.52))
        if est < MIN_READABLE:
            print(
                f"warning: {longest!r} is {len(longest)} characters; it will fit at "
                f"roughly {est}px, under the {MIN_READABLE}px floor for a 120px feed "
                f"thumbnail.\n  shorten it, or split it across lines.",
                file=sys.stderr,
            )

    tokens = {
        "MAXFONT": spec["max_font"],
        "FITWIDTH": avail,
        "FITHEIGHT": max_h,
        "STACKED": "false" if name == "contrast-pair" else "true",
        "ACCENT": spec["accent"],
        "HOT": spec["hot"],
        "GROUND": spec["ground"],
        "DEEP": spec["deep"],
        "TEXT_COLOR": spec["text_color"],
        "FONT": spec["font"],
        "FONT_WEIGHT": spec["font_weight"],
        "EYEBROW": spec["eyebrow"],
        "TILT": spec["tilt"],
        "SUBJECT_POS": spec["subject_pos"],
        "ARTIFACT_POS": spec["artifact_pos"],
        "LINE1": lines[0] if len(lines) > 0 else "",
        "LINE2": lines[1] if len(lines) > 1 else "",
        "LINE3": lines[2] if len(lines) > 2 else "",
        "LINE2_DISPLAY": "block" if len(lines) > 1 else "none",
        "LINE3_DISPLAY": "block" if len(lines) > 2 else "none",
        "EYEBROW_DISPLAY": "inline-block" if spec["eyebrow"] else "none",
    }
    for key, path in (spec["images"] or {}).items():
        tokens["IMG_" + key.upper()] = data_uri(path)

    # Any image slot the spec did not fill gets a transparent pixel, so the
    # template shows its ground colour instead of a broken-image icon.
    for slot in ("SUBJECT", "ARTIFACT", "LEFT", "RIGHT", "BG"):
        tokens.setdefault("IMG_" + slot, BLANK_PIXEL)

    html = html + FIT_JS

    for key, val in tokens.items():
        html = html.replace("{{" + key + "}}", str(val))

    leftover = [t for t in ("{{",) if t in html]
    if leftover:
        import re
        names = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", html))
        if names:
            sys.exit(f"error: template {name!r} has unfilled tokens: {sorted(names)}")
    return html


def shoot(chrome, html, out_png):
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, "t.html")
        with open(page, "w") as fh:
            fh.write(html)
        if os.path.exists(out_png):
            os.remove(out_png)

        # No --user-data-dir. Pointing Chrome at a fresh profile directory makes
        # it write the screenshot and then never exit, which reads exactly like a
        # render failure. Without the flag it exits on its own in ~2s.
        cmd = [
            chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--no-first-run", "--no-default-browser-check", "--disable-extensions",
            f"--window-size={WIDTH},{HEIGHT}",
            f"--screenshot={out_png}",
            "file://" + page,
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait on the artifact, not on the process: Chrome sometimes lingers after
        # the file is complete, and a hung Chrome is indistinguishable from a slow
        # one. Poll until the size stops changing, then stop waiting.
        deadline, stable, last = time.time() + 60, 0, -1
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            if os.path.exists(out_png):
                size = os.path.getsize(out_png)
                stable = stable + 1 if size == last and size > 0 else 0
                last = size
                if stable >= 3:
                    proc.terminate()
                    break
            time.sleep(0.25)
        else:
            proc.kill()

        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

        if not os.path.exists(out_png) or os.path.getsize(out_png) == 0:
            err = (proc.stderr.read().decode("utf-8", "replace") if proc.stderr else "")
            sys.exit(
                "error: Chrome wrote no screenshot.\n"
                "  Re-run with --dump-html to inspect the composed page.\n"
                + err[-1500:]
            )


def to_jpeg(png_path, jpg_path):
    """Step quality down until it fits. YouTube rejects anything over 2 MB."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("error: --jpeg needs Pillow (pip install pillow)")
    img = Image.open(png_path).convert("RGB")
    for q in (92, 88, 84, 80, 74, 68):
        img.save(jpg_path, "JPEG", quality=q, optimize=True, progressive=True)
        if os.path.getsize(jpg_path) <= MAX_BYTES:
            return q
    return q


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?", help="thumbnail spec JSON")
    ap.add_argument("-o", "--out", help="output .png or .jpg")
    ap.add_argument("--template", help="override spec.template")
    ap.add_argument("--text", nargs="*", help="override spec.text lines")
    ap.add_argument("--accent", help="override spec.accent")
    ap.add_argument("--jpeg", action="store_true", help="also write a JPEG under 2 MB")
    ap.add_argument("--chrome", help="path to a Chrome/Chromium binary")
    ap.add_argument("--dump-html", help="write the composed HTML here for debugging")
    ap.add_argument("--list-templates", action="store_true")
    args = ap.parse_args()

    if args.list_templates:
        for t in list_templates():
            print(t)
        return

    if not args.spec or not args.out:
        ap.error("spec and -o/--out are required")

    with open(args.spec) as fh:
        user = json.load(fh)
    spec = dict(DEFAULTS)
    spec.update(user)
    if args.template:
        spec["template"] = args.template
    if args.text is not None:
        spec["text"] = args.text
    if args.accent:
        spec["accent"] = args.accent

    if len(spec["text"]) > 3:
        print(f"warning: {len(spec['text'])} text lines. Three is the ceiling — "
              "each extra line shrinks the type at 120px.", file=sys.stderr)

    html = build_html(spec)
    if args.dump_html:
        with open(args.dump_html, "w") as fh:
            fh.write(html)

    chrome = args.chrome or find_chrome()
    out = os.path.abspath(os.path.expanduser(args.out))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    png = out if out.lower().endswith(".png") else out.rsplit(".", 1)[0] + ".png"
    shoot(chrome, html, png)
    print(f"  {png}  ({os.path.getsize(png) / 1024:.0f} KB)")

    if args.jpeg or out.lower().endswith((".jpg", ".jpeg")):
        jpg = out if out.lower().endswith((".jpg", ".jpeg")) else png[:-4] + ".jpg"
        q = to_jpeg(png, jpg)
        size = os.path.getsize(jpg)
        flag = "" if size <= MAX_BYTES else "  OVER 2 MB — will be rejected"
        print(f"  {jpg}  ({size / 1024:.0f} KB, q={q}){flag}")


if __name__ == "__main__":
    main()
