---
name: youtube-episode
description: Take a finished video plus its long-form script and publish it end to end — transcript, chapters from the script's own sections, title and thumbnail, description, tags, upload and verification. Use whenever a user hands over a video file and a script and wants it published, says "upload this episode", "publish this video", "put this on YouTube", or provides a video with a generation budget for B-roll. This is the orchestrator; it calls youtube-publish, youtube-channel, youtube-shorts-funnel and the craft skills as needed.
---

# Publishing an episode, end to end

The user hands over three things: **a video file, the script it was made from,
and a generation budget.** Everything else comes from this setup.

The script is a `youtube-longform-script` output, so it already contains the
section structure — IDs, titles, planned run times, the spoken VO, and which
sections lift out as Shorts. **That is the segmentation. Do not re-derive it.**

## The rule that governs everything here

Two kinds of work, and confusing them is the main failure mode:

| Deterministic — a script decides | Creative — you decide |
|---|---|
| Chapter **timestamps** | Chapter **titles** |
| Section boundaries | Which sections become chapters |
| Every character/count limit | Title, thumbnail, description copy |
| Upload sequence and field setting | Thumbnail concept and frame choice |
| Verification | The pinned comment's question |
| Factual declarations | B-roll choices, within budget |

**Never invent a timestamp, a duration or a limit.** Run the script that
computes it. **Never let a script write the copy.** That is the part that
decides whether anyone clicks.

If a tool refuses, it found a real problem. Fix the input, don't route around it.

## Setup check, once

```bash
cd ~/Developer/video-pipeline/skills/youtube-publish/scripts
PY=~/Developer/video-pipeline/.venv/bin/python
$PY studio.py canary          # selectors still resolve?
```

If not signed in: `$PY studio.py login`, and the **user** signs in — never type
a credential, a phone number or a verification code.

## Order

### 1. Establish the facts

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 VIDEO
$PY ~/Developer/video-pipeline/transcribe.py VIDEO --out-dir edit/cache
```

Duration decides a lot: over 15 minutes needs the channel's Intermediate
features, and vertical + under 3 minutes means it is a Short, not a long-form.

Read the script's locked structure table. Note which sections are marked as
Shorts — that is the follow-up queue, not this video's problem.

### 2. Chapters — deterministic

```bash
$PY chapters.py --script SCRIPT.md --transcript edit/cache/words_*.json \
                --duration DUR -o publish/chapters.txt
```

It locates each section by its first spoken line, so the timestamps come from
the video rather than the script's intentions. It validates all five rules and
**refuses to write** if any fails.

If it refuses because two chapters are under 10s apart, **drop or merge chapters
— never move a timestamp to make it fit.** The section structure stays; only the
chapter list changes.

Then rewrite the titles. The script's headings are working titles: `Memory: the
answer nobody expects` is a script heading, `Why 4.5× the pixels costs 2 GB` is
a chapter. Name what a viewer gets by jumping there. **This is creative work.**

### 3. Packaging — creative

Load `youtube-publish` and read `references/packaging.md` and
`references/thumbnail-craft.md`.

- **Write three titles, pick one.** Front-load the subject, 40–65 characters.
- **The thumbnail shows, the title says.** Cover either; the other must still
  add something.
- Pull thumbnail material **from the footage** — the evidence in the video is
  the strongest asset available and no generated image can borrow its
  credibility.

```bash
ffmpeg -ss T -i VIDEO -frames:v 1 -vf "crop=1280:556:0:0" assets/shot.png
$PY render_thumbnail.py spec.json -o publish/thumb.png
$PY thumb_qc.py publish/thumb.png --proof publish/thumb_120.png
```

**Look at the 120px proof.** That is the size the click gets decided at, and it
is where three-word copy beats four-word copy. If `render_thumbnail.py` warns
that the type fits below 140px, the copy is too long — shorten it rather than
shipping it.

Generative models (Higgsfield MCP) are for **backgrounds and plates only** —
never faces, never text. `thumbnail-craft.md` has the tells to check.

### 4. Description — creative, then mechanical

`references/description-anatomy.md`. Short and specific: ~600 characters is
normal. The first 150 do nearly all the work, for the viewer and the classifier
both. Paste `chapters.txt` in. Three to five hashtags, none in the title.

### 5. Manifest and preflight

```json
{
  "video": "master.mp4",
  "title": "...",
  "description": "description.txt",
  "thumbnail": "thumb.jpg",
  "tags": ["..."],
  "category": "Science & Technology",
  "made_for_kids": false,
  "altered_content": true,
  "visibility": "private"
}
```

`altered_content` is a **factual declaration, not a judgement call**: true for
any generated photoreal scene, room or character; false for screen recordings
and real footage of a person.

```bash
$PY publish.py publish.json --preflight-only
```

Two seconds, and it refuses on anything that would waste the upload.

### 6. Publish

```bash
$PY publish.py publish.json
```

preflight → upload → configure → **verify** → visibility. The verify stage
reloads and reads every field back. Trust that, not the button states.

**Upload as `private` unless the user asked to go public.** Publishing is the
one irreversible step; show them the URL and let them flip it.

### 7. Post-publish

- Pinned comment: post it on the watch page, then
  `$PY studio.py pin VIDEO_ID --match "first words"`. Read
  `references/pinned-comment.md` first — a link-only pin suppresses replies.
- End screen and cards: manual, no API. The end screen needs a spoken CTA in
  the script to match.
- Shorts: the script's structure table already names which sections lift out.
  That is `youtube-shorts-funnel`, a separate job.

## B-roll, when a budget is given

Read `broll-direction` first — it exists to check whether a free clip or a frame
you already have does the job before spending anything.

Order of preference: **footage you already have → free stock → generated.**
State the cost before spending, keep a running total against the budget, and
stop when it is reached rather than asking for more.

## When something breaks

Everything stops rather than guessing, and writes a report to
`~/.cache/video-pipeline/drift/<timestamp>/` with a screenshot, the
accessibility tree and the failed step. Read it, patch `selectors.json`, re-run
`studio.py canary`.

**The upload is never lost** — the video id is saved beside the manifest, so
`publish.py publish.json --video-id ID` resumes from configure.

## Where to actually be creative

Worth stating plainly, because the temptation is to be creative about the wrong
things:

**Be creative about:** the title's angle. Which frame carries the idea. The
three words on the thumbnail. What each chapter promises. The first sentence of
the description. The question in the pinned comment. Which section deserves a
Short first.

**Do not be creative about:** timestamps, durations, character limits, the
15-hashtag cliff, the 10-second chapter floor, whether content needs the altered
declaration, or whether a check that failed can be skipped. Those have answers,
and the scripts already know them.

The channel's material is genuinely surprising on its own and its tone is calm.
Packaging louder than the video is a promise the first thirty seconds breaks —
which shows up as a retention cliff, not a CTR problem, and is therefore very
easy to misdiagnose.
