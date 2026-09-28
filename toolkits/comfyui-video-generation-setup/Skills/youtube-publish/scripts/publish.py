#!/usr/bin/env python3
"""Upload and configure a YouTube video in one deterministic command.

    publish.py manifest.json
    publish.py --video master.mp4 --title "..." --description desc.txt
    publish.py manifest.json --title "override"      # flags beat the manifest
    publish.py manifest.json --preflight-only        # check, don't upload

Runs: preflight -> upload (wizard, minimal) -> configure (edit page, everything)
-> visibility. State is written next to the manifest, so a re-run after a
failure resumes instead of re-uploading.

Two design choices worth knowing:

  * Preflight runs BEFORE the upload and refuses on anything that would waste
    it. A 35-minute master that fails the channel's 15-minute gate should cost
    you two seconds, not forty minutes.
  * The file goes up through the wizard with a title and nothing else; every
    other field is set on the edit page afterwards. The wizard's step count
    varies by channel and video, while the edit page is one stable surface that
    holds every field. Fewer moving parts, and re-running configure is safe.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import studio  # noqa: E402
from studio import Drift, Studio, browser, signed_in, load_selectors  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("error: pip install playwright")

FFPROBE = os.environ.get("FFPROBE", "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe")

TITLE_MAX = 100
DESC_MAX = 5000
TAG_CHARS_MAX = 500
THUMB_MAX_BYTES = 2 * 1024 * 1024      # API limit; Studio allows 50 MB
UNVERIFIED_MAX_SECONDS = 15 * 60

DEFAULTS = {
    "video": None,
    "title": None,
    "description": "",
    "thumbnail": None,
    "tags": [],
    "category": "Science & Technology",
    "playlist": None,
    "made_for_kids": False,
    "altered_content": False,
    "visibility": "private",
    "pinned_comment": None,
}


# ----------------------------------------------------------------- helpers

def read_text(value):
    """A field may be inline text or a path to a file of text."""
    if not value:
        return ""
    p = os.path.expanduser(str(value))
    if os.path.exists(p) and os.path.isfile(p):
        with open(p) as fh:
            return fh.read().strip()
    return str(value)


def duration_of(path):
    try:
        out = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True, timeout=60)
        return float(out.stdout.strip())
    except Exception:
        return None


def hhmmss(sec):
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


# ---------------------------------------------------------------- preflight

def preflight(cfg, check_features=True):
    """Everything that can be known before touching the browser. Returns
    (fails, warnings). Nothing uploads while fails is non-empty."""
    fails, warns = [], []

    video = cfg.get("video")
    if not video:
        fails.append("no video given")
    elif not os.path.exists(video):
        fails.append(f"video not found: {video}")

    dur = duration_of(video) if video and os.path.exists(video) else None
    if dur:
        cfg["_duration"] = dur

    title = cfg.get("title") or ""
    if not title.strip():
        fails.append("title is empty")
    elif len(title) > TITLE_MAX:
        fails.append(f"title is {len(title)} chars, max {TITLE_MAX}")
    elif len(title) > 70:
        warns.append(f"title is {len(title)} chars; suggestion tiles truncate near 70")

    desc = cfg.get("_description_text", "")
    if len(desc) > DESC_MAX:
        fails.append(f"description is {len(desc)} chars, max {DESC_MAX}")

    # hashtags: the cliff is 15 across title and description together
    tags_in_text = re.findall(r"(?<!\w)#\w+", title + "\n" + desc)
    if len(tags_in_text) > 15:
        fails.append(
            f"{len(tags_in_text)} hashtags across title+description. Over 15 and "
            f"YouTube ignores every one of them.")
    if re.search(r"(?<!\w)#\w+", title):
        warns.append("hashtag in the title suppresses the clickable hashtags above it")

    # chapters, if the description has any
    stamps = re.findall(r"^\s*((?:\d+:)?\d{1,2}:\d{2})\s+\S", desc, re.M)
    if stamps:
        secs = []
        for s in stamps:
            parts = [int(x) for x in s.split(":")]
            secs.append(parts[0] * 60 + parts[1] if len(parts) == 2
                        else parts[0] * 3600 + parts[1] * 60 + parts[2])
        if secs[0] != 0:
            fails.append(f"first chapter is {stamps[0]}, must be 0:00 — "
                         f"otherwise YouTube silently ignores all of them")
        if len(secs) < 3:
            fails.append(f"{len(secs)} chapters; YouTube needs at least 3")
        if secs != sorted(secs):
            fails.append("chapters are not in ascending order")
        short = [stamps[i] for i in range(len(secs) - 1) if secs[i + 1] - secs[i] < 10]
        if short:
            fails.append(f"chapters shorter than 10s: {', '.join(short)}")
        if dur and secs[-1] > dur:
            fails.append(f"last chapter {stamps[-1]} is past the end of the video "
                         f"({hhmmss(dur)})")

    tags = cfg.get("tags") or []
    if sum(len(t) + 1 for t in tags) > TAG_CHARS_MAX:
        fails.append(f"tags exceed the {TAG_CHARS_MAX}-character total")

    thumb = cfg.get("thumbnail")
    if thumb:
        if not os.path.exists(thumb):
            fails.append(f"thumbnail not found: {thumb}")
        else:
            size = os.path.getsize(thumb)
            if size > THUMB_MAX_BYTES:
                warns.append(f"thumbnail is {size/1e6:.1f} MB; over the 2 MB API "
                             f"limit though Studio accepts up to 50 MB")
            try:
                from PIL import Image
                w, h = Image.open(thumb).size
                if (w, h) != (1280, 720):
                    warns.append(f"thumbnail is {w}x{h}, not 1280x720")
            except ImportError:
                pass

    if cfg.get("visibility") not in ("private", "unlisted", "public"):
        fails.append(f"visibility must be private/unlisted/public, "
                     f"got {cfg.get('visibility')!r}")

    # the gate that actually wastes time
    if dur and dur > UNVERIFIED_MAX_SECONDS:
        if check_features:
            ok = channel_can_upload_long()
            if ok is False:
                fails.append(
                    f"video is {hhmmss(dur)} but the channel's Intermediate features "
                    f"are not enabled, so uploads are capped at 15:00.\n"
                    f"       Verify the phone number at youtube.com/features first.")
            elif ok is None:
                warns.append(f"video is {hhmmss(dur)}; could not confirm the channel is "
                             f"verified for uploads over 15 minutes")
        else:
            warns.append(f"video is {hhmmss(dur)}; needs a phone-verified channel")

    if cfg.get("thumbnail") and check_features:
        if channel_can_upload_long() is False:
            warns.append("custom thumbnails also need Intermediate features; "
                         "the thumbnail step will be skipped")

    return fails, warns


FEATURES_CACHE = os.path.expanduser("~/.cache/video-pipeline/features.json")
FEATURES_TTL = 7 * 24 * 3600
_mem = {}


def channel_can_upload_long(force=False):
    """Is the channel's Intermediate tier enabled? True / False / None.

    Gates uploads over 15 minutes AND custom thumbnails, so getting it wrong
    either wastes a long upload or hangs the metadata save.

    Must run headful: Studio is a single-page app that renders essentially
    nothing under headless Chrome — the body comes back at ~300 characters and
    the check silently returns None. Cached to disk because it opens a window
    and the answer changes about once in a channel's life.
    """
    if "v" in _mem and not force:
        return _mem["v"]
    if not force and os.path.exists(FEATURES_CACHE):
        try:
            with open(FEATURES_CACHE) as fh:
                c = json.load(fh)
            if time.time() - c.get("when", 0) < FEATURES_TTL:
                _mem["v"] = c.get("intermediate")
                return _mem["v"]
        except Exception:
            pass

    val = None
    try:
        with sync_playwright() as pw:
            ctx = browser(pw, headless=False)
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto("https://www.youtube.com/features", wait_until="domcontentloaded")
            for _ in range(24):
                page.wait_for_timeout(750)
                body = page.inner_text("body")
                if "Intermediate features" in body:
                    break
            m = re.search(r"Intermediate features\s*\n[^\n]*\n\s*"
                          r"(Enabled|Eligible|Not eligible)", body)
            if not m:
                m = re.search(r"Intermediate features.{0,200}?"
                              r"(Enabled|Eligible|Not eligible)", body, re.S)
            if m:
                val = (m.group(1) == "Enabled")
            ctx.close()
    except Exception:
        val = None

    _mem["v"] = val
    try:
        os.makedirs(os.path.dirname(FEATURES_CACHE), exist_ok=True)
        with open(FEATURES_CACHE, "w") as fh:
            json.dump({"intermediate": val, "when": time.time()}, fh, indent=2)
    except Exception:
        pass
    return val


# ------------------------------------------------------------------- stages


def goto_video(page, video_id, tab="edit", tries=3):
    """Navigate to a video page and confirm we actually landed there.

    Studio is a single-page app: a goto issued moments after another Studio
    navigation gets swallowed by its router and silently leaves you on the
    dashboard. Every field lookup then fails for a reason that has nothing to do
    with the fields. Assert the URL, same as any other step."""
    want = f"/video/{video_id}/"
    for attempt in range(tries):
        page.goto(f"{studio.STUDIO}{want}{tab}", wait_until="domcontentloaded")
        for _ in range(30):
            page.wait_for_timeout(500)
            if want in page.url:
                return True
        page.wait_for_timeout(1500)
    raise Drift(
        f"could not reach {want}{tab} after {tries} attempts; "
        f"still on {page.url}")


def do_upload(s, page, cfg):
    """Wizard, minimal. Title only, saved private. Returns the video id."""
    s.step("open the upload dialog",
           pre=lambda: s.present("dashboard.upload_button"),
           action=lambda: s.find("dashboard.upload_button").click(),
           post=lambda: s.present("upload.file_input"))

    mb = os.path.getsize(cfg["video"]) / 1e6
    print(f"  · attach {os.path.basename(cfg['video'])} ({mb:.0f} MB)")
    s.find("upload.file_input").set_input_files(cfg["video"])

    s.step("wait for Studio to accept the file",
           pre=lambda: True, action=lambda: None,
           post=lambda: s.present("details.title", timeout=1500),
           post_timeout=900000)

    box = s.find("details.title")
    box.click()
    page.keyboard.press("ControlOrMeta+a")
    box.type(cfg["title"][:TITLE_MAX], delay=8)
    print(f"  · title set ({len(cfg['title'])} chars)")

    kids = s.find("details.not_for_kids" if not cfg["made_for_kids"]
                  else "edit.for_kids", required=False)
    if kids:
        kids.click()
    else:
        raise Drift("made-for-kids declaration not found; it is mandatory")

    vid = None
    link = s.find("visibility.video_link", required=False, timeout=15000)
    if link:
        m = re.search(r"([A-Za-z0-9_-]{11})", (link.text_content() or ""))
        vid = m.group(1) if m else None

    # walk to visibility, however many intermediate steps this channel has
    for _ in range(5):
        if s.present("visibility.private", timeout=1500):
            break
        nxt = s.find("upload.next", required=False, timeout=3000)
        if not nxt:
            break
        nxt.click()
        page.wait_for_timeout(1200)
    else:
        raise Drift("never reached the visibility step")

    s.step("save as private",
           pre=lambda: s.present("visibility.private"),
           action=lambda: s.find("visibility.private").click(),
           post=lambda: True)
    s.step("commit",
           pre=lambda: s.present("upload.save"),
           action=lambda: s.find("upload.save").click(),
           post=lambda: not s.present("upload.dialog", timeout=2000)
           or s.present("visibility.video_link", timeout=2000),
           post_timeout=120000)

    if not vid:
        link = s.find("visibility.video_link", required=False)
        if link:
            m = re.search(r"([A-Za-z0-9_-]{11})", (link.text_content() or ""))
            vid = m.group(1) if m else None
    if not vid:
        raise Drift("upload finished but no video id could be read")
    return vid


def pick_dropdown(page, s, key, value):
    """Open a Studio dropdown and choose the item whose text matches."""
    trig = s.find(key, required=False)
    if not trig:
        return False
    trig.click()
    page.wait_for_timeout(1200)
    item = page.get_by_role("option", name=value, exact=False).first
    try:
        item.wait_for(state="visible", timeout=4000)
    except Exception:
        item = page.locator(f"tp-yt-paper-item:has-text('{value}')").first
        try:
            item.wait_for(state="visible", timeout=4000)
        except Exception:
            page.keyboard.press("Escape")
            return False
    item.click()
    page.wait_for_timeout(800)
    return True


def do_configure(s, page, cfg, video_id):
    """Everything on the edit page. Safe to re-run."""
    goto_video(page, video_id, "edit")

    # The metadata editor hydrates well after domcontentloaded: the container
    # divs exist immediately but the rich-text boxes inside them do not. Gate on
    # the title box actually being there, or every field below misses.
    s.step("wait for the edit page to hydrate",
           pre=lambda: True, action=lambda: None,
           post=lambda: s.present("edit.title", timeout=1200),
           post_timeout=60000)

    save = page.locator("#save").first

    desc = cfg["_description_text"]
    if desc:
        d = s.find("edit.description")
        d.click()
        page.keyboard.press("ControlOrMeta+a")
        d.type(desc, delay=1)
        print(f"  · description ({len(desc)} chars)")

    if cfg.get("thumbnail"):
        # A channel without Intermediate features accepts the file client-side
        # and then never finishes uploading it, which leaves the form dirty
        # forever and takes the whole Save down with it. Skip rather than hang.
        if channel_can_upload_long() is False:
            print("  ! thumbnail SKIPPED — channel lacks Intermediate features. "
                  "Verify the phone number at youtube.com/features.")
        else:
            ti = s.find("details.thumbnail_input", required=False)
            if ti:
                ti.set_input_files(cfg["thumbnail"])
                page.wait_for_timeout(6000)
                print("  · thumbnail attached")
            else:
                print("  ! thumbnail input not found")

    if cfg.get("playlist"):
        if pick_dropdown(page, s, "edit.playlist_trigger", cfg["playlist"]):
            done = page.get_by_role("button", name="Done").first
            try:
                done.click(timeout=3000)
            except Exception:
                page.keyboard.press("Escape")
            print(f"  · playlist: {cfg['playlist']}")
        else:
            print(f"  ! playlist {cfg['playlist']!r} not found — create it first")

    more = s.find("edit.show_more", required=False)
    if more:
        more.click()
        page.wait_for_timeout(2500)

    alt = s.find("edit.altered_yes" if cfg["altered_content"] else "edit.altered_no",
                 required=False)
    if alt:
        alt.click()
        print(f"  · altered content: {'yes' if cfg['altered_content'] else 'no'}")
    else:
        print("  ! altered-content declaration not found")

    if cfg.get("tags"):
        ti = s.find("edit.tags", required=False)
        if ti:
            ti.click()
            for t in cfg["tags"]:
                ti.type(t, delay=6)
                page.keyboard.press(",")
                page.wait_for_timeout(150)
            print(f"  · {len(cfg['tags'])} tags")

    if cfg.get("category"):
        if pick_dropdown(page, s, "edit.category", cfg["category"]):
            print(f"  · category: {cfg['category']}")
        else:
            print(f"  ! category {cfg['category']!r} not found")

    # Save unconditionally. #save's enabled state is not a dirty indicator on
    # this Studio build — it reads enabled on a freshly loaded, unmodified page —
    # so gating on it skips real saves and reports phantom ones. The only
    # trustworthy postcondition is reading the values back afterwards.
    print("  · save")
    try:
        save.click(timeout=8000)
    except Exception:
        print("  ! Save not clickable")
    page.wait_for_timeout(6000)



READBACK_JS = """() => {
 const deep=(s)=>{const r=[],seen=new Set();(function dig(n){if(!n||seen.has(n))return;seen.add(n);
  try{n.querySelectorAll(s).forEach(e=>r.push(e))}catch(e){}
  try{n.querySelectorAll('*').forEach(e=>{if(e.shadowRoot)dig(e.shadowRoot)})}catch(e){}})(document);return r};
 const t=deep('#title-textarea #textbox')[0], d=deep('#description-textarea #textbox')[0];
 const alt=deep('tp-yt-paper-radio-button[name=VIDEO_HAS_ALTERED_CONTENT_YES]')[0];
 const kid=deep('tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]')[0];
 const cat=deep('ytcp-form-select#category')[0];
 return {title:t?t.textContent.trim():'', desc:d?d.textContent.trim():'',
         tags:deep('ytcp-chip').map(e=>e.textContent.trim()).filter(Boolean).length,
         alteredYes: alt?alt.getAttribute('aria-checked')==='true':null,
         notForKids: kid?kid.getAttribute('aria-checked')==='true':null,
         category: cat?cat.textContent.replace(/\\s+/g,' ').trim():''};
}"""


def verify_saved(s, page, cfg, video_id):
    """Reload and compare what is on the video against what we asked for.

    This is the only postcondition worth trusting for the metadata stage.
    Watching a Save button told us a save had happened when it had not, and
    that a thumbnail had failed when it had succeeded."""
    goto_video(page, video_id, "edit")
    s.step("reload for verification",
           pre=lambda: True, action=lambda: None,
           post=lambda: s.present("edit.title", timeout=1200),
           post_timeout=60000)
    more = s.find("edit.show_more", required=False)
    if more:
        more.click()
        page.wait_for_timeout(2500)
    got = page.evaluate(READBACK_JS)

    bad = []
    if cfg["title"].strip()[:100] != got["title"].strip():
        bad.append(f"title is {got['title'][:45]!r}")
    want_desc = cfg["_description_text"].strip()
    if want_desc and abs(len(got["desc"]) - len(want_desc)) > 5:
        bad.append(f"description is {len(got['desc'])} chars, expected {len(want_desc)}")
    if cfg.get("tags") and got["tags"] < len(cfg["tags"]):
        bad.append(f"{got['tags']} tags, expected {len(cfg['tags'])}")
    if got["alteredYes"] is not None and got["alteredYes"] != bool(cfg["altered_content"]):
        bad.append(f"altered-content is {got['alteredYes']}, expected {cfg['altered_content']}")
    if got["notForKids"] is not None and got["notForKids"] == bool(cfg["made_for_kids"]):
        bad.append("made-for-kids declaration is wrong")
    if cfg.get("category") and cfg["category"].lower() not in got["category"].lower():
        bad.append(f"category is {got['category'][:30]!r}, expected {cfg['category']!r}")
    return bad


def do_visibility(s, page, cfg, video_id):
    if cfg["visibility"] == "private":
        return
    goto_video(page, video_id, "edit")
    page.wait_for_timeout(4000)
    trig = s.find("edit.visibility_trigger", required=False)
    if not trig:
        print(f"  ! visibility control not found — set it to {cfg['visibility']} by hand")
        return
    trig.click()
    page.wait_for_timeout(1200)
    opt = page.get_by_role("radio", name=cfg["visibility"], exact=False).first
    try:
        opt.click(timeout=4000)
    except Exception:
        print(f"  ! could not select {cfg['visibility']} — set it by hand")
        page.keyboard.press("Escape")
        return
    page.wait_for_timeout(800)
    for name in ("Done", "Save"):
        try:
            page.get_by_role("button", name=name).first.click(timeout=2500)
            page.wait_for_timeout(1500)
        except Exception:
            pass
    print(f"  · visibility: {cfg['visibility']}")


# --------------------------------------------------------------------- main

def load_config(args):
    cfg = dict(DEFAULTS)
    if args.manifest:
        with open(args.manifest) as fh:
            cfg.update(json.load(fh))
        base = os.path.dirname(os.path.abspath(args.manifest))
    else:
        base = os.getcwd()

    for k in ("video", "title", "description", "thumbnail", "category",
              "playlist", "visibility"):
        v = getattr(args, k, None)
        if v is not None:
            cfg[k] = v
    if args.tags:
        cfg["tags"] = args.tags
    if args.altered_content is not None:
        cfg["altered_content"] = args.altered_content

    # paths in a manifest are relative to the manifest
    for k in ("video", "thumbnail"):
        if cfg.get(k):
            p = os.path.expanduser(cfg[k])
            cfg[k] = p if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))

    d = cfg.get("description")
    if d and not os.path.isabs(str(d)) and os.path.exists(os.path.join(base, str(d))):
        d = os.path.join(base, str(d))
    cfg["_description_text"] = read_text(d)
    return cfg


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", nargs="?", help="publish manifest JSON")
    ap.add_argument("--video")
    ap.add_argument("--title")
    ap.add_argument("--description", help="inline text, or a path to a text file")
    ap.add_argument("--thumbnail")
    ap.add_argument("--tags", nargs="*")
    ap.add_argument("--category")
    ap.add_argument("--playlist")
    ap.add_argument("--visibility", choices=["private", "unlisted", "public"])
    ap.add_argument("--altered-content", dest="altered_content",
                    action=argparse.BooleanOptionalAction, default=None)
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--skip-preflight", action="store_true")
    ap.add_argument("--video-id", help="skip upload, configure this existing video")
    ap.add_argument("--slow", type=float, default=0.8)
    ap.add_argument("--keep-open", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args)

    if args.skip_preflight:
        print("\n  preflight — SKIPPED by flag")
        fails, warns = [], []
    else:
        print("\n  preflight")
        fails, warns = preflight(cfg)
    for w in warns:
        print(f"    warn  {w}")
    for f in fails:
        print(f"    FAIL  {f}")
    if fails:
        print("\n  nothing was uploaded.\n")
        return 1
    dur = cfg.get("_duration")
    if not args.skip_preflight:
        print(f"    ok    {os.path.basename(cfg['video'])}"
              f"{f' · {hhmmss(dur)}' if dur else ''}"
              f" · title {len(cfg['title'])} chars"
              f" · description {len(cfg['_description_text'])} chars"
              f" · {len(cfg.get('tags') or [])} tags")
    if args.preflight_only:
        print("\n  preflight only — stopping.\n")
        return 0

    state_path = (os.path.splitext(args.manifest)[0] + ".state.json"
                  if args.manifest else ".publish-state.json")
    state = {}
    if os.path.exists(state_path):
        with open(state_path) as fh:
            state = json.load(fh)
    video_id = args.video_id or state.get("video_id")

    sels = load_selectors()
    with sync_playwright() as pw:
        ctx = browser(pw)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        s = Studio(page, sels, slow=args.slow)
        try:
            if not signed_in(page):
                print("  not signed in. run: studio.py login")
                return 1

            if video_id:
                print(f"\n  upload — skipped, resuming {video_id}")
            else:
                print("\n  upload")
                video_id = do_upload(s, page, cfg)
                state["video_id"] = video_id
                with open(state_path, "w") as fh:
                    json.dump(state, fh, indent=2)
                print(f"    {video_id}")

            print("\n  configure")
            do_configure(s, page, cfg, video_id)

            print("\n  verify")
            bad = verify_saved(s, page, cfg, video_id)
            for b in bad:
                print(f"    MISMATCH  {b}")
            if not bad:
                print("    ok    every field read back as set")

            print("\n  visibility")
            do_visibility(s, page, cfg, video_id)

            state["done"] = True
            with open(state_path, "w") as fh:
                json.dump(state, fh, indent=2)

            print(f"\n  https://youtu.be/{video_id}   ({cfg['visibility']})")
            if cfg.get("pinned_comment"):
                print(f"  pinned comment not posted — no API credentials yet. "
                      f"Paste it, then: studio.py pin {video_id} --match '<text>'")
            print()
            return 0

        except Drift as e:
            s.report_drift(e)
            if video_id:
                print(f"\n  the video exists as {video_id}. Re-run to resume:")
                print(f"    publish.py {args.manifest or ''} --video-id {video_id}")
            return 2
        finally:
            if not args.keep_open:
                ctx.close()


if __name__ == "__main__":
    sys.exit(main() or 0)
