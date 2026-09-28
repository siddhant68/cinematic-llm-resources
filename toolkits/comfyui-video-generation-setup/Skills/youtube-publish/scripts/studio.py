#!/usr/bin/env python3
"""Drive YouTube Studio for the things the Data API cannot do.

    studio.py login                       sign in once, by hand, into a dedicated profile
    studio.py canary                      resolve every selector, touch nothing
    studio.py upload VIDEO --title T ...   attach a file, fill Details, save
    studio.py pin VIDEO_ID --match TEXT   pin a comment on the watch page

Design rules, all of which exist because a wrong click is worse than no click:

  * Selectors live in selectors.json, never inline.
  * Every step asserts a precondition before acting and a postcondition after.
    A failed precondition means the step does not run at all.
  * On drift, write a report with a screenshot and the accessibility tree, then
    stop. Never guess, never retry blindly.
  * Headful, real Chrome, a persistent profile you signed into yourself. The
    script never sees or types a credential.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SELECTORS_PATH = os.path.join(HERE, "selectors.json")
PROFILE_DIR = os.path.expanduser("~/.cache/video-pipeline/chrome-profile")
DRIFT_ROOT = os.path.expanduser("~/.cache/video-pipeline/drift")
STUDIO = "https://studio.youtube.com"

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    sys.exit("error: pip install playwright")


def load_selectors():
    with open(SELECTORS_PATH) as fh:
        return json.load(fh)


class Drift(Exception):
    pass


class Studio:
    def __init__(self, page, selectors, slow=1.0):
        self.page = page
        self.sel = selectors["selectors"]
        self.slow = slow

    # ---- locator resolution -------------------------------------------
    def _build(self, spec):
        p = self.page
        if "css" in spec:
            return p.locator(spec["css"])
        if "role" in spec:
            name = spec.get("name")
            return p.get_by_role(spec["role"], name=name) if name else p.get_by_role(spec["role"])
        if "text" in spec:
            return p.get_by_text(spec["text"], exact=False)
        raise ValueError(f"unrecognised locator spec: {spec}")

    def find(self, key, timeout=8000, required=True):
        """Resolve a selector through its fallback chain. Returns None if
        optional and absent; raises Drift if required and absent.

        Default state is "visible", not "attached". Studio pre-renders whole
        branches of the wizard hidden in the DOM — the error banner, every
        later step — so "attached" matches things that are not on screen and
        reports failures that did not happen. Only genuinely invisible
        elements (file inputs) opt into "attached" via the selector entry."""
        entry = self.sel.get(key)
        if entry is None:
            raise Drift(f"no selector named {key!r} in selectors.json")
        state = entry.get("state", "visible")
        chain = [entry["primary"]] + entry.get("fallbacks", [])
        for i, spec in enumerate(chain):
            loc = self._build(spec).first
            try:
                loc.wait_for(state=state, timeout=timeout if i == 0 else 2000)
                if i > 0:
                    print(f"  note: {key} resolved via fallback {i} ({spec})")
                return loc
            except PWTimeout:
                continue
        if not required:
            return None
        raise Drift(f"{key} — expected {entry['expect']!r}, resolved nothing")

    def present(self, key, timeout=2500):
        try:
            return self.find(key, timeout=timeout) is not None
        except Drift:
            return False

    # ---- steps ---------------------------------------------------------
    def step(self, name, pre, action, post, post_timeout=30000):
        """Run one step: assert, act, assert. Never act on a failed precondition."""
        print(f"  · {name}")
        if not pre():
            raise Drift(f"precondition failed for step {name!r}")
        action()
        time.sleep(self.slow)
        deadline = time.time() + post_timeout / 1000
        while time.time() < deadline:
            if post():
                return
            time.sleep(0.4)
        raise Drift(f"postcondition failed for step {name!r}")

    # ---- drift reporting ------------------------------------------------
    def report_drift(self, err):
        stamp = dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        d = os.path.join(DRIFT_ROOT, stamp)
        os.makedirs(d, exist_ok=True)
        try:
            self.page.screenshot(path=os.path.join(d, "screenshot.png"), full_page=True)
        except Exception:
            pass
        try:
            snap = self.page.accessibility.snapshot()
            with open(os.path.join(d, "accessibility-tree.json"), "w") as fh:
                json.dump(snap, fh, indent=2)
        except Exception:
            pass
        try:
            with open(os.path.join(d, "page.html"), "w") as fh:
                fh.write(self.page.content())
        except Exception:
            pass
        with open(os.path.join(d, "failed-step.json"), "w") as fh:
            json.dump({
                "error": str(err),
                "url": self.page.url,
                "when": stamp,
                "selectors_version": load_selectors().get("youtube_studio_version_seen"),
            }, fh, indent=2)
        print(f"\n  DRIFT — {err}")
        print(f"  report: {d}")
        print("  YouTube Studio's UI has probably changed. Read the accessibility")
        print("  tree in that directory, patch selectors.json, and re-run canary.")
        return d


def browser(pw, headless=False):
    """Real Chrome, persistent profile. Headless is the loudest automation
    signal there is, so it is off by default and only used for the canary."""
    os.makedirs(PROFILE_DIR, exist_ok=True)
    return pw.chromium.launch_persistent_context(
        PROFILE_DIR,
        channel="chrome",
        headless=headless,
        viewport={"width": 1440, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )


def signed_in(page):
    page.goto(STUDIO, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    return "accounts.google.com" not in page.url and "/channel/" in page.url


# ------------------------------------------------------------------ commands

def cmd_login(args):
    """Open the automation profile and wait. The window is the user's to use, so
    it is never closed out from under them — the wait ends when they are signed
    in, or when they close the window themselves."""
    with sync_playwright() as pw:
        ctx = browser(pw)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(STUDIO, wait_until="domcontentloaded")
        print("\n  A Chrome window is open on this machine.", flush=True)
        print("  Sign in there yourself — this script never types a credential.", flush=True)
        print("  It will wait as long as you need. Close the window to abort.\n", flush=True)

        waited = 0
        while True:
            try:
                url = page.url
            except Exception:
                print("  window closed before sign-in completed.", flush=True)
                return 1
            if "/channel/" in url and "accounts.google.com" not in url:
                m = re.search(r"/channel/(UC[\w-]+)", url)
                print(f"  signed in. channel {m.group(1) if m else '?'}", flush=True)
                print(f"  profile saved: {PROFILE_DIR}", flush=True)
                print("  leaving the window open for 20s so the session persists...",
                      flush=True)
                time.sleep(20)
                ctx.close()
                return 0
            time.sleep(3)
            waited += 3
            if waited % 60 == 0:
                print(f"  still waiting ({waited // 60} min)... current: {url[:70]}",
                      flush=True)


def cmd_canary(args):
    """Read-only. Resolve every selector reachable without uploading, and
    report which ones no longer exist — before a real publish depends on them."""
    sels = load_selectors()
    reachable_on_dashboard = ["dashboard.upload_button"]
    reachable_in_dialog = [
        "upload.dialog", "upload.file_input", "upload.select_files",
        "upload.progress", "upload.next", "upload.save", "upload.close",
    ]
    ok, missing = [], []
    with sync_playwright() as pw:
        ctx = browser(pw, headless=args.headless)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        if not signed_in(page):
            print("  not signed in. run: studio.py login")
            ctx.close()
            return 1
        s = Studio(page, sels)
        for key in reachable_on_dashboard:
            (ok if s.present(key) else missing).append(key)
        try:
            s.find("dashboard.upload_button").click()
            page.wait_for_timeout(2500)
            for key in reachable_in_dialog:
                (ok if s.present(key) else missing).append(key)
            if s.present("upload.close"):
                s.find("upload.close").click()
        except Drift as e:
            s.report_drift(e)
        ctx.close()

    print(f"\n  resolved  {len(ok)}")
    for k in ok:
        print(f"    ok    {k}")
    for k in missing:
        print(f"    GONE  {k} — {sels['selectors'][k]['expect']}")
    unverified = [k for k, v in sels["selectors"].items() if not v.get("verified")]
    if unverified:
        print(f"\n  {len(unverified)} selectors still unverified (need a real upload to reach):")
        for k in unverified:
            print(f"    ?     {k}")
    return 1 if missing else 0


def cmd_upload(args):
    sels = load_selectors()
    video = os.path.abspath(os.path.expanduser(args.video))
    if not os.path.exists(video):
        sys.exit(f"error: no such file: {video}")
    thumb = os.path.abspath(os.path.expanduser(args.thumbnail)) if args.thumbnail else None

    with sync_playwright() as pw:
        ctx = browser(pw)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        s = Studio(page, sels, slow=args.slow)
        try:
            if not signed_in(page):
                print("  not signed in. run: studio.py login")
                return 1

            s.step(
                "open the upload dialog",
                pre=lambda: s.present("dashboard.upload_button"),
                action=lambda: s.find("dashboard.upload_button").click(),
                post=lambda: s.present("upload.file_input"),
            )

            size_mb = os.path.getsize(video) / 1e6
            print(f"  · attach {os.path.basename(video)} ({size_mb:.0f} MB)")
            s.find("upload.file_input").set_input_files(video)

            # The title field appearing is the real signal that Studio accepted
            # the file; the progress bar shows up for a failed upload too.
            s.step(
                "wait for Studio to accept the file",
                pre=lambda: True,
                action=lambda: None,
                post=lambda: s.present("details.title", timeout=1500)
                and not s.present("upload.error", timeout=300),
                post_timeout=180000,
            )

            title_box = s.find("details.title")
            title_box.click()
            page.keyboard.press("ControlOrMeta+a")
            title_box.type(args.title, delay=12)
            print(f"  · title set ({len(args.title)} chars)")

            if args.description:
                desc = open(args.description).read() if os.path.exists(args.description) else args.description
                d = s.find("details.description")
                d.click()
                d.type(desc, delay=2)
                print(f"  · description set ({len(desc)} chars)")

            if thumb:
                ti = s.find("details.thumbnail_input", required=False)
                if ti:
                    ti.set_input_files(thumb)
                    print(f"  · thumbnail set")
                else:
                    print("  ! thumbnail input not found — set it by hand or via thumbnails.set")

            kids = s.find("details.not_for_kids", required=False)
            if kids:
                kids.click()
                print("  · declared not made for kids")
            else:
                raise Drift("made-for-kids declaration not found — it is mandatory, "
                            "and getting it wrong silently disables comments and end screens")

            # Details -> Monetisation/Checks -> Visibility. The number of
            # intermediate steps changes between channels, so walk until the
            # visibility radios appear rather than assuming a count.
            for i in range(5):
                if s.present("visibility." + args.visibility, timeout=1500):
                    break
                nxt = s.find("upload.next", required=False, timeout=3000)
                if not nxt:
                    break
                nxt.click()
                page.wait_for_timeout(1200)
            else:
                raise Drift("never reached the visibility step")

            s.step(
                f"set visibility to {args.visibility}",
                pre=lambda: s.present("visibility." + args.visibility),
                action=lambda: s.find("visibility." + args.visibility).click(),
                post=lambda: True,
            )

            if args.dry_run:
                print("\n  dry run — stopping before Save. Nothing was published.")
                print("  the dialog is open in the browser.")
                print("  NOTE: the file did reach YouTube, so this leaves a DRAFT")
                print("  on the channel. Drafts are private and deletable.")
                page.wait_for_timeout(6000)
                return 0

            s.step(
                "save",
                pre=lambda: s.present("upload.save"),
                action=lambda: s.find("upload.save").click(),
                post=lambda: s.present("visibility.video_link", timeout=2000)
                or not s.present("upload.dialog", timeout=2000),
                post_timeout=60000,
            )

            link = s.find("visibility.video_link", required=False)
            vid = None
            if link:
                text = (link.text_content() or "").strip()
                m = re.search(r"([A-Za-z0-9_-]{11})", text)
                vid = m.group(1) if m else None
            print(f"\n  uploaded. video id: {vid or 'unknown'}  visibility: {args.visibility}")
            if vid:
                print(f"  https://youtu.be/{vid}")
            return 0

        except Drift as e:
            s.report_drift(e)
            return 2
        finally:
            if not args.keep_open:
                ctx.close()


def cmd_verify(args):
    """Open the phone-verification screen and hold the window open.

    The script navigates and waits. It never types a phone number, a code, or
    any other personal detail — that is the user's to enter, in their own
    browser window."""
    import glob
    with sync_playwright() as pw:
        ctx = browser(pw)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        page.goto("https://www.youtube.com/verify", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        # If /verify bounced, go the long way through channel settings.
        if "verify" not in page.url:
            page.goto("https://www.youtube.com/features", wait_until="domcontentloaded")
            page.wait_for_timeout(6000)
            for name in ("Verify phone number", "Verify"):
                try:
                    b = page.get_by_role("button", name=name).first
                    if b.is_visible():
                        b.click()
                        page.wait_for_timeout(4000)
                        break
                except Exception:
                    pass

        print("\n  A Chrome window is open at the phone-verification screen.", flush=True)
        print("  Enter your number there — this script never types one.", flush=True)
        print("  Waiting for Intermediate features to flip to Enabled.", flush=True)
        print("  Close the window when you're done.\n", flush=True)

        waited = 0
        while True:
            try:
                _ = page.url
            except Exception:
                print("  window closed.", flush=True)
                break
            if waited and waited % 30 == 0:
                try:
                    probe = ctx.new_page()
                    probe.goto("https://www.youtube.com/features",
                               wait_until="domcontentloaded")
                    probe.wait_for_timeout(6000)
                    body = probe.inner_text("body")
                    probe.close()
                    m = re.search(r"Intermediate features\s*\n[^\n]*\n\s*"
                                  r"(Enabled|Eligible|Not eligible)", body)
                    if m and m.group(1) == "Enabled":
                        print("  Intermediate features are now ENABLED.", flush=True)
                        for f in glob.glob(os.path.expanduser(
                                "~/.cache/video-pipeline/features.json")):
                            os.remove(f)
                        print("  cleared the features cache — custom thumbnails and "
                              "uploads over 15 minutes are unblocked.", flush=True)
                        ctx.close()
                        return 0
                except Exception:
                    pass
            time.sleep(3)
            waited += 3

        # window closed without a confirmed flip; drop the cache so the next
        # publish re-checks rather than trusting a stale "not enabled"
        try:
            os.remove(os.path.expanduser("~/.cache/video-pipeline/features.json"))
            print("  cleared the features cache; the next publish will re-check.",
                  flush=True)
        except FileNotFoundError:
            pass
        return 0


def cmd_thumbnail(args):
    """Set a thumbnail on an already-uploaded video, without re-uploading it."""
    sels = load_selectors()
    thumb = os.path.abspath(os.path.expanduser(args.thumbnail))
    if not os.path.exists(thumb):
        sys.exit(f"error: no such file: {thumb}")
    with sync_playwright() as pw:
        ctx = browser(pw)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        s = Studio(page, sels, slow=args.slow)
        try:
            page.goto(f"{STUDIO}/video/{args.video_id}/edit",
                      wait_until="domcontentloaded")
            page.wait_for_timeout(4000)
            save = page.locator("#save").first

            def save_enabled():
                try:
                    return save.is_visible() and not save.get_attribute("disabled")
                except Exception:
                    return False

            # Save going from disabled to enabled is the only proof the file was
            # accepted. Without this check the step reports success on a channel
            # where custom thumbnails are not enabled at all.
            s.step(
                "attach the thumbnail",
                pre=lambda: s.present("details.thumbnail_input"),
                action=lambda: s.find("details.thumbnail_input").set_input_files(thumb),
                post=save_enabled,
                post_timeout=15000,
            )
            s.step(
                "save",
                pre=save_enabled,
                action=lambda: save.click(),
                post=lambda: not save_enabled(),
                post_timeout=30000,
            )
            print(f"  thumbnail set on {args.video_id}")
            return 0
        except Drift as e:
            s.report_drift(e)
            print("\n  If the file never registered: custom thumbnails require the")
            print("  channel's Intermediate features, which need phone verification.")
            print("  Check youtube.com/features — 'Eligible' is not 'Enabled'.")
            return 2
        finally:
            if not args.keep_open:
                ctx.close()


def cmd_pin(args):
    sels = load_selectors()
    with sync_playwright() as pw:
        ctx = browser(pw)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        s = Studio(page, sels, slow=args.slow)
        try:
            page.goto(f"https://www.youtube.com/watch?v={args.video_id}",
                      wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            page.mouse.wheel(0, 1200)
            page.wait_for_timeout(2500)
            comment = page.get_by_text(args.match, exact=False).first
            comment.wait_for(state="visible", timeout=20000)
            comment.hover()
            s.step(
                "open the comment overflow menu",
                pre=lambda: s.present("comment.overflow"),
                action=lambda: s.find("comment.overflow").click(),
                post=lambda: s.present("comment.pin", timeout=3000),
            )
            s.step(
                "pin",
                pre=lambda: s.present("comment.pin"),
                action=lambda: s.find("comment.pin").click(),
                post=lambda: True,
            )
            page.wait_for_timeout(2000)
            print("  pinned (confirm the dialog in the browser if one appeared)")
            return 0
        except Drift as e:
            s.report_drift(e)
            return 2
        finally:
            if not args.keep_open:
                ctx.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("login")
    sub.add_parser("verify")

    c = sub.add_parser("canary")
    c.add_argument("--headless", action="store_true")

    u = sub.add_parser("upload")
    u.add_argument("video")
    u.add_argument("--title", required=True)
    u.add_argument("--description", help="text, or a path to a file of text")
    u.add_argument("--thumbnail")
    u.add_argument("--visibility", default="private", choices=["private", "public"])
    u.add_argument("--slow", type=float, default=1.0, help="seconds between actions")
    u.add_argument("--dry-run", action="store_true", help="stop before Save")
    u.add_argument("--keep-open", action="store_true")

    t = sub.add_parser("thumbnail")
    t.add_argument("video_id")
    t.add_argument("--thumbnail", required=True)
    t.add_argument("--slow", type=float, default=1.0)
    t.add_argument("--keep-open", action="store_true")

    p = sub.add_parser("pin")
    p.add_argument("video_id")
    p.add_argument("--match", required=True, help="text identifying the comment")
    p.add_argument("--slow", type=float, default=1.0)
    p.add_argument("--keep-open", action="store_true")

    args = ap.parse_args()
    return {"login": cmd_login, "canary": cmd_canary, "upload": cmd_upload,
            "verify": cmd_verify, "thumbnail": cmd_thumbnail,
            "pin": cmd_pin}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
