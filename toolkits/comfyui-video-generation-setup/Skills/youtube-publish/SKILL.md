---
name: youtube-publish
description: Package and publish a finished video to YouTube — title, thumbnail, description, hashtags, chapters, captions, playlist and pinned comment. Use whenever a master is ready to go out, whenever a user asks for a title, a thumbnail, a description, tags, hashtags, chapters or timestamps for a video, whenever they ask how to package or upload something, and whenever a Short needs its own metadata. Also use when a published video is underperforming on click-through and the packaging needs rewriting. Produces a reviewable publish manifest, a rendered 1280x720 thumbnail checked at feed size, and the exact copy to paste or push.
---

# Publishing to YouTube

The edit is done. This is everything between a finished master and a video that
people actually click.

Publishing is the one genuinely irreversible step in the pipeline, so it works
the way the rest of it works: **a manifest is the source of truth, a human reads
it before anything goes live, and every stage is resumable.**

## Read first

`references/components.md` — every surface a video has, ranked by leverage, and
what actually separates professional packaging from AI-level packaging. Start
here if you are not sure which of these is worth the effort.

`references/api-surface.md` — what the API can and cannot do, and the
verification lock that decides how the upload actually happens. Read it before
touching credentials or writing any upload code; it will change what you build.

Channel-level assets — name, About, banner, trailer, sections, playlists — are
the `youtube-channel` skill, not this one.

## Publishing is one command

`RUNBOOK.md` is the operational guide — read that to run a publish, not this
file. In short:

```bash
publish.py manifest.json --preflight-only   # ~2s, catches what would waste an upload
publish.py manifest.json                    # preflight -> upload -> configure -> visibility
```

The manifest is the parameterisation: video, title, description, thumbnail,
tags, category, playlist, made-for-kids, altered-content, visibility. Flags
override it. State is saved beside the manifest, so a failure resumes with
`--video-id` instead of re-uploading.

**The file uploads through the wizard with a title only; every other field is
set on the edit page afterwards.** The wizard's step count varies by channel and
video; the edit page is one stable surface holding every field, and re-running
configure is safe.

**Assert navigation, not just fields.** Studio is a single-page app and a `goto`
issued soon after another Studio navigation gets swallowed by its router,
leaving you on the dashboard while every field lookup fails for reasons that
have nothing to do with the fields.

## Order

Packaging comes **before** the final edit is locked, not after. If the video
cannot be packaged, its idea is not sharp enough yet, and that is far cheaper to
find out now.

```
1  packaging      title + thumbnail, written together as one unit
2  manifest       build publish.json from the script and the render
3  assets         thumbnail rendered and QC'd, captions serialised to SRT
4  review         a human reads the manifest. this gate is not optional
5  upload         the file
6  metadata       title, description, chapters, tags, thumbnail, playlist
7  post-publish   comment posted, then pinned; end screen; cards
```

Stages 5–7 are covered in `references/api-surface.md`. Stages 1–4 are here.

## 1. Packaging

Full craft in `references/packaging.md` and `references/thumbnail-craft.md`.
The two rules that matter most:

- **The thumbnail shows, the title says.** If they carry the same information,
  one of them is wasted. Cover either and the other should still add something.
- **Judge at 120px.** That is how wide a thumbnail renders in a phone feed, and
  it is where the decision is made. Everything else is downstream of it.

Write three titles and pick, rather than writing one and defending it.

## 2. The manifest

`publish.json` holds the whole publish. Build it, read it, then act on it.

```bash
scripts/build_manifest.py \
  --master edit/master.mp4 \
  --script script/EP-LTX25-on-a-mac.md \
  --timeline edit/renders/timeline.json \
  -o publish/publish.json
```

Never hand-edit a published field afterwards — patch the manifest and re-run the
metadata stage, so the file and the live video cannot drift apart.

## 3. Sections and chapters

The long-form script already contains a **locked structure table** with section
IDs, run times and Short assignments. That table is simultaneously the chapter
list, the Shorts queue and the description skeleton. Parse it. Do not re-segment
a script that was segmented deliberately.

**Chapters come from `renders/timeline.json`, never from the script's planned
times.** The script's `0:00-1:00` is an intention; the render is what exists.
This is the same rule captions already follow.

```bash
scripts/chapters.py --timeline edit/renders/timeline.json \
                    --script script/EP-*.md -o publish/chapters.txt
```

YouTube fails chapters **silently** — a bad timestamp renders as plain text with
no error. All of these or nothing:

- first timestamp is `0:00`
- at least three, ascending
- each at least 10 seconds
- `M:SS` under an hour, `H:MM:SS` over

## 4. Thumbnail

The thumbnail is HTML rendered by headless Chrome at exactly 1280×720. That
makes it text — diffable, versionable, and variants cost a parameter change
rather than a new prompt.

```bash
scripts/render_thumbnail.py spec.json -o publish/thumb.png
scripts/thumb_qc.py publish/thumb.png --proof publish/thumb_120.png
```

A spec is small:

```json
{
  "template": "face-artifact",
  "eyebrow": "AI FILMMAKING",
  "text": ["LIGHT", "NEEDS A", "SOURCE"],
  "subject_pos": "center center",
  "images": { "subject": "assets/face.png", "artifact": "assets/doorway.png" }
}
```

Four templates — `evidence`, `face-artifact`, `contrast-pair`, `statement`.
`--list-templates` enumerates them; `references/thumbnail-craft.md` says when
each one is the right shape.

**Type is fitted in the browser, not estimated.** Short copy renders huge and
long copy renders small, which is the honest feedback loop: if the type came out
small, there are too many words. The renderer warns before you look at it.

Source images come from the footage itself — the evidence in the video is the
strongest asset available, and no generated image can borrow its credibility:

```bash
ffmpeg -ss 37.9 -i master.mp4 -frames:v 1 -vf "crop=1280:556:0:0" assets/lamp.png
```

Crop the caption band off (`crop=1280:556:0:0` on a 720-tall frame), and match
the crop aspect to the template slot so `cover` does not eat the subject.

## 5. Description

Full anatomy in `references/description-anatomy.md`. Short and specific beats
long and thorough — six hundred characters is normal and correct.

```
~150 chars   what this video is, in plain words. all most viewers see.
─── fold ───
chapters     from timeline.json, first line 0:00
one line     what this is part of, and what's next
one link     the thing promised on camera
hashtags     3-5
```

Not a keyword dump: stuffing now triggers spam classification. A plain, specific
sentence serves the viewer and the classifier equally well.

**Past 15 hashtags YouTube ignores every one of them.** Title and description
count together, and it is a cliff rather than a taper. The first three in the
description render as clickable links above the title — but only if the title
itself carries no hashtag.

## Altered-content disclosure — mandatory here

YouTube requires disclosure when realistic content could be mistaken for a real
person, place or event and was made with generative AI. Enforcement is active,
and YouTube labels some synthetic media itself whether or not you declare it.

For this channel: **generated photoreal scenes, rooms and characters need the
disclosure.** Screen recordings, terminal output, real footage of you, and
clearly stylised or animated output do not. AI used for editing assistance,
colour or upscaling does not.

Declaring it does **not** reduce reach, ranking, recommendations or
monetisation — YouTube has stated this explicitly. Set it per-video in the
Details step. On a channel whose subject is AI filmmaking, disclosing is also
just consistent with the content.

## End screen — script it, don't bolt it on

The strongest next-click surface there is, and browser-only forever.

The layout that performs is **one full-size video element plus a subscribe
button** — two choices, no decision paralysis. That roughly doubles the video
element's click-through against a four-element grid. For a series, pick the
specific next episode rather than "best for viewer".

The part most people miss: **say it out loud in the ten seconds before it
appears.** A spoken CTA matched to the on-screen element converts markedly
better than the visual alone — which makes the end screen a scripting decision.
The script has to leave room for it, and needs ≥25s of video to place one.

Cards are a different tool: teaser click-through is 1–3%, so use them for
context links mid-video, never to promote the next video.

## Fields that bite

| Field | Why |
|---|---|
| `madeForKids` | Mandatory. True by accident and the video loses comments, end screens, cards and notifications. Nothing warns you. |
| `notifySubscribers` | Defaults to true. Set false on a re-upload. |
| `defaultAudioLanguage` | Unset means no auto-translation reach. |
| `categoryId` | `28` Science & Technology, `27` Education. |
| `publishAt` | Requires `privacyStatus: private` at insert. |

## Captions are nearly free

The edit pipeline already produces forced-aligned word timings on the output
timeline. Serialise them rather than letting YouTube guess — auto-captions
reliably mangle `vmmap`, `int8`, `MPS`, `safetensors`, and the uploaded track is
what the translation layer reads. Burned-in captions do not do this job.

```bash
scripts/captions_srt.py --words edit/cache/words_*.json \
                        --timeline edit/renders/timeline.json -o publish/captions.srt
```

## Before anything goes live

- `thumb_qc.py` passes, **and** you have looked at the 120px proof
- The title says something the thumbnail does not
- The gap the title opens closes on camera
- Chapters start at `0:00` and every one is ≥10s
- Hashtag count ≤ 15 across title and description together
- `madeForKids` is false
- The pinned comment text exists and the resource links in it resolve

A clean report is a precondition for publishing, not a substitute for reading
the manifest.

## Taste

The failure mode of automated packaging is a channel that looks like every other
channel: the same shocked face, the same three-word shout, the same arrow. This
channel's material is genuinely surprising on its own and its stated tone is
calm — packaging louder than the video is a promise the first thirty seconds
breaks, and that shows up as a retention cliff rather than a CTR problem, which
makes it very easy to misdiagnose.

On a channel about composition, framing and light, the packaging is a live
demonstration of whether you can do the thing you are teaching. Apply the
video's own lessons to it.
