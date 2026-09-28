# Description

A description is not an SEO artefact and not an essay. It has two readers and
one job for each:

- **A viewer** deciding whether this is worth their next thirty minutes
- **The classifier** deciding which audience to test it on

Both are served by the same thing: **a plain, specific sentence about what the
video actually contains.** Not keywords, not a summary, not a pitch. Specificity
is the whole technique — it is simultaneously the most useful thing for a human
and the clearest signal for a machine.

Keyword stuffing now actively triggers spam classification. The era where a wall
of terms helped is over.

## Shape

```
[1]  ~150 chars   what this video is, in plain words     ← does almost all the work
─── fold ───
[2]  chapters     from timeline.json, first line 0:00
[3]  one line     what this is part of, and what's next
[4]  one link     the thing promised on camera
[5]  hashtags     3-5
```

That's it. Five thousand characters are available; using six hundred is normal
and correct. Length is not a ranking factor, and a long description is a worse
experience for the only person who reads it.

## [1] The first 150 characters

The only part most viewers see, and the part weighted most heavily by the
classifier. Search results show roughly the first 100–125 characters; mobile
truncates around 157.

- **Say the subject in the first line**, naturally. Not "in this video I'll be
  discussing…" — just the thing.
- **Name the specific failure or result.** `Light in AI video keeps changing
  direction between shots` does more work than any keyword list, for both
  readers.
- **Don't repeat the title verbatim.** Extend it.
- One sentence, maybe two.

Worked example:

> Light in AI video keeps changing direction between shots. The fix isn't a
> better prompt — it's giving the light somewhere to come from.

That names the topic, the symptom and the shape of the answer in 134 characters,
without a single keyword shoved in.

## [2] Chapters

Generated from `renders/timeline.json`, never from the script's planned times.

**All of these, or YouTube silently ignores the entire block** — no error, the
timestamps just render as plain text:

- first timestamp is `0:00`
- at least three, ascending
- each at least 10 seconds
- `M:SS` under an hour, `H:MM:SS` over
- colons, not periods or commas

Chapter titles name **what the viewer gets by jumping there**, not what the
section is called in the script. `Why 4.5× the pixels costs 2 GB`, not
`Memory: the answer nobody expects`.

## [3] Context, one line

What series this belongs to and what comes next. This is the line that tells a
viewer they have found a body of work rather than one video, and tells the
classifier how to group your catalogue.

## [4] One link

The thing you promised on camera, worded the way you said it. Extra links go
further down or nowhere — every additional link dilutes the one that matters.
The full resource list, if there is one, belongs here rather than in the pinned
comment; see `pinned-comment.md` for why.

## [5] Hashtags

**Over 15 across title and description together and YouTube ignores all of
them.** A cliff, not a taper, and nothing tells you it happened.

The first three in the description render as clickable links above the title —
but only if the title itself has none. Three to five total.

```
#AIFilmmaking + the episode's own (#ComfyUI #LTX2 #Cinematography)
#Shorts replaces one on vertical uploads
```

## Tags (the separate field)

Nearly worthless for ranking. One job left: catching misspellings and casing
variants of proper nouns — `ComfyUI`, `comfy ui`, `LTX-2.5`, `LTX 2.5`. Ten to
fifteen, no stuffing.

## Checks

- First 150 characters stand alone and name something specific
- Reads like a person wrote it for another person
- Chapters satisfy all five rules
- Hashtags ≤ 15 across title and description together, none in the title
- Every on-camera promise is honoured somewhere in here
