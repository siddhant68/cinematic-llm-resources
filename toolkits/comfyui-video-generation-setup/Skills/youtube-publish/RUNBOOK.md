# Publishing — runbook

One command per video. No Claude required.

```bash
cd ~/Developer/video-pipeline/skills/youtube-publish/scripts
PY=~/Developer/video-pipeline/.venv/bin/python
```

## Once, ever

```bash
$PY studio.py login
```

Opens a Chrome window on a dedicated profile (`~/.cache/video-pipeline/chrome-profile`).
Sign in by hand — the script never types a credential. It waits as long as you
need and the session persists across runs.

## Every video

**1. Write a manifest** — copy `templates/publish.manifest.json` next to your
master and edit it. Paths inside it are relative to the manifest.

```json
{
  "video": "master.mp4",
  "title": "Your AI light has no source. That's why it breaks.",
  "description": "description.txt",
  "thumbnail": "thumb.jpg",
  "tags": ["AI filmmaking", "ComfyUI", "comfy ui", "LTX-2.5"],
  "category": "Science & Technology",
  "playlist": null,
  "made_for_kids": false,
  "altered_content": true,
  "visibility": "private"
}
```

`description` and `title` accept inline text or a path to a text file.
`altered_content` is **true** for any generated photoreal scene, room or
character; false for screen recordings and real footage of you.

**2. Check before spending the upload**

```bash
$PY publish.py publish.json --preflight-only
```

Catches, in about two seconds: missing file, title over 100 chars, chapters that
don't start at 0:00 or run under 10s or sit out of order, over 15 hashtags,
thumbnail wrong size, bad visibility value, and **a video longer than the
channel's 15-minute cap**. Nothing uploads while anything fails.

**3. Publish**

```bash
$PY publish.py publish.json
```

Runs preflight → upload → configure → **verify** → visibility, then prints the
video id and URL.

The verify stage reloads the page and reads every field back, comparing it to
the manifest:

```
  verify
    ok    every field read back as set
```

That read-back is the only postcondition worth trusting here. Studio's `#save`
button reads *enabled* even on a freshly loaded, unmodified page, so gating on
it both skipped real saves and reported phantom ones.

**4. Pin the comment** (after pasting it on the watch page)

```bash
$PY studio.py pin VIDEO_ID --match "first few words of the comment"
```

## Flags instead of a manifest

```bash
$PY publish.py --video master.mp4 --title "..." --description desc.txt \
               --thumbnail thumb.jpg --tags "ComfyUI" "LTX-2.5" \
               --altered-content --visibility private
```

Flags override manifest values, so `publish.py publish.json --title "..."` works.

## When something fails

It stops rather than guessing, and writes a report to
`~/.cache/video-pipeline/drift/<timestamp>/` with a screenshot, the
accessibility tree, the page HTML and the failed step.

**The upload is not lost.** The video id is saved next to the manifest as
`publish.state.json`. Re-run to resume from configure:

```bash
$PY publish.py publish.json --video-id VIDEO_ID
```

Configure is idempotent — re-running it is safe.

To check whether YouTube changed its UI, without touching a video:

```bash
$PY studio.py canary
```

## Channel feature gates

**Verified 2026-09-04 — Intermediate features are Enabled.** Uploads over 15
minutes, custom thumbnails and A/B thumbnail testing all work.

Preflight still checks, because the gate is silent when it bites: without it,
uploads cap at 15 minutes and a custom thumbnail accepts the file then hangs on
"Uploading…" forever with no error. Status is cached 7 days at
`~/.cache/video-pipeline/features.json`; delete it to force a re-check.

`studio.py verify` opens the phone-verification screen if it is ever needed
again. It never types a number.

## What is still manual

End screens, cards, and pinning a comment's *first* posting — no API exists for
any of them, and end screens are worth doing by hand anyway because they need a
spoken CTA in the script to match.
