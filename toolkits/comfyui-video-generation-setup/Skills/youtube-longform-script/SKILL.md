---
name: youtube-longform-script
description: Write a complete long-form YouTube tutorial script (25-45 min) for a technical or teaching channel, written as one person talking to one person. Use this whenever the user wants a video script, a YouTube script, an episode script, a script for a tutorial or explainer video, a video outline turned into a script, or wants to turn research/code/a technical system into a video. Also use it when they ask to restructure or rewrite an existing script, plan an episode, write a video hook or cold open, plan Shorts cutdowns from a long video, or say things like "script this", "write EP02", "turn this into a video", or "how should this video be structured". Produces a locked section structure, full spoken VO with a conversational cadence, retention annotations, a claim ledger, Short seeds for the youtube-shorts-funnel skill, and a voice-scrubbed final pass.
---

# Long-Form YouTube Tutorial Script

This skill writes teaching-video scripts for a technical channel: 25-45 minutes,
one topic taught properly, then demonstrated in a real system. The output is a
shooting script, not an outline.

Three things make this format different from generic YouTube advice, and all
three drive the decisions below:

1. **Length inverts the usual retention math.** Most YouTube scripting guidance is
   calibrated for 7-15 minute videos where the goal is completion. At 30+ minutes
   nobody expects 100% completion, and that is fine: long videos capture a
   disproportionate share of total watch time even at lower completion rates. You
   are optimizing for *depth of engagement over time*, not for everyone reaching
   the end. That changes where effort goes.
2. **The script is a conversation, not a lecture.** A 40-minute video is someone
   choosing to sit with you. If the script reads as a stack of aphorisms, the
   performance reads as a teleprompter, and the viewer feels talked *at*. This is
   the most common failure in a technically correct script, and Step 4 exists
   entirely to prevent it.
3. **Shorts come from the script, but never shape it.** Sections are annotated
   with Short *seeds*, not cut points. The long video is optimized for the long
   video. See "The Shorts boundary" below, which is a hard rule.

## The Shorts boundary

**Read this before writing anything. It overrides any instinct to make sections
liftable.**

An earlier version of this skill required every section to open cold on a
standalone claim so it could be clipped straight into a Short. That rule is
withdrawn. It caused three measurable failures in production scripts:

- Every section opened with the same contrarian shape ("X isn't Y, it's Z"),
  which made an episode of eight sections feel like the same argument eight
  times.
- Sections could not reference each other, so each one re-established context.
  The same list of concepts got read aloud three times in one episode.
- The connective tissue that makes a script feel like talking to a person
  is exactly what a cold open forbids.

The replacement rule:

> **Write the long video as one continuous conversation. Annotate where a Short
> could later be built. Never bend a sentence, an opening, or a section boundary
> to serve a Short.**

A Short is *rebuilt* from a seed by the `youtube-shorts-funnel` skill, in a
separate pass, with its own hook, escalation and bridge. That skill's own rule is
"restructure, do not clip" — so a clip boundary was always the wrong artifact to
hand it.

**Not every section yields a Short, and that is the correct outcome.** A section
that is genuinely load-bearing for the episode and makes no sense alone gets no
seed. Forcing one produces a Short that fails and a section that got worse to
make it. Three to six good seeds per episode beats one per section.

## Workflow

### Step 1 — Intake

Before writing, get these. Ask only for what is genuinely missing; infer the rest
from files or conversation, and state what you inferred so it can be corrected.

| Need | Why it matters |
|---|---|
| **The topic and the one thing viewers walk away with** | The whole script is a promise and its payoff. If this is fuzzy, everything downstream is padding. |
| **Source material** (code, research, transcripts, notes) | Read it fully before structuring. Specifics are what make a teaching video credible. |
| **What gets demoed, and does it work today** | Demo sections are screen-driven and written differently from teaching sections. |
| **Target runtime** | Drives section count and word budget. |
| **Series context** | What came before, what comes next, what the viewer is assumed to know. |
| **Known failures worth showing** | The single highest-credibility material available. See "The wrong-first beat". |

If the user has an existing script or structure for this episode, read it first and
treat it as the spine to improve rather than replacing it wholesale.

### Step 2 — Lock the structure before writing prose

Write the section table first and confirm it. Structure churn after prose exists is
expensive and demoralizing; structure churn before it is free.

The canonical five-part shape:

| Part | Share of runtime | Job |
|---|---|---|
| **1. Open** | ~8% | Hook, then why this problem matters |
| **2. Concept** | ~30% | The mental model, taught tool-agnostically |
| **3. Failures and fixes** | ~20% | What goes wrong, why, and the correction |
| **4. Implementation** | ~30% | The system, the live demo, and it failing honestly |
| **5. Close** | ~12% | The counter-intuitive payoff, recap, next episode |

Two structural notes that matter more than the percentages:

**Failures usually work better distributed than blocked.** A failure attached to
the concept it breaks teaches better than a "common mistakes" segment quarantined
in the middle. Default to weaving each failure into its own concept section, and
reserve Part 3 as a dedicated block only when the failures are systemic rather
than per-concept.

**Part 3 should end on a turn.** The strongest long-form teaching videos have a
hinge: a section where the craft you just taught is shown to stop scaling, which
is what earns the implementation half. Without it, Part 4 reads as an unearned
product pitch. With it, Part 4 reads as the necessary consequence. Write the turn
as arithmetic or evidence, never as an assertion that the manual way is bad.

For each section record: ID, title, runtime, what it assumes, and whether it is a
Short seed candidate.

**The table is a contract.** Every row in it gets written, or the row gets removed
from the table before delivery. A script that promises thirteen sections and
delivers eleven has silently dropped runtime, and the gap is invisible in a long
file. `scriptcheck.py` verifies this; do not rely on remembering it.

Present the table and get sign-off before writing VO.

### Step 3 — Write the sections

Section anatomy. Every section, without exception:

```
[arrives from the previous section, then makes a claim]
  ↓
[teaches or demonstrates one idea]
  ↓
[micro-payoff: the viewer now knows something they did not]
  ↓
[forward hook into the next section]
```

Sections are allowed — encouraged — to connect. "That was the easy half." "This
is the one I got wrong." "Same idea, but now there are two people in the frame."
Connective tissue is what makes forty minutes feel like a conversation instead of
forty flashcards.

What a section opening must still avoid is *throat-clearing*: recapping what was
just said, announcing what is about to be said, or restating the thesis before
starting. Arrive, then claim.

Format each section with visual and spoken content separated, since they are
executed by different people (or by the same person at different times):

```
`[V]` what is on screen
`[VO]` what is spoken
`[B-ROLL]` capture needed before this can be edited
```

Mark Short seeds with a `► SHORT SEED` block at the end of the relevant sections
only. The format is in Step 6.

### Step 4 — The conversation pass

Read `references/conversation-and-cadence.md` before this step. This is the pass
that decides whether the video sounds like a person or a teleprompter, and it is
the one most often skipped because the script already "reads fine" on the page.
It reads fine because prose and speech fail differently.

The four checks, in order of how audible they are:

1. **Vary the beat length.** The dominant failure is uniformity: every line six
   words long with a blank line around it, so the performer pauses every two
   seconds and every sentence carries the weight of a punchline. Target a median
   of 12-18 words per spoken beat, with fewer than 35% of beats under 8 words.
   Short beats are for landing something. If everything is short, nothing lands.
2. **Address one person.** "You", not "we", unless the "we" is genuinely shared.
   Instructional "we" ("now we need to decide where the camera goes") is the
   register of a textbook read aloud.
3. **Leave some questions open.** A rhetorical question that gets answered two
   lines later is lecture cadence. At least once per section, ask something and
   let it sit, or answer it against expectation. Count them: if nearly every
   question in the script is self-answered inside two beats, rewrite half.
4. **React, do not only assert.** Real speech contains asides, corrections and
   admissions mid-thought. "I spent a week on this before I noticed." "That
   sounds obvious. It was not obvious to me." These are not filler; they are the
   difference between a person and a document.

Run the cadence report and fix what it flags:

```bash
python3 ~/.claude/skills/youtube-longform-script/scripts/scriptcheck.py <script-path> --cadence
```

### Step 5 — The crispness pass

Repetition in a long script is almost never verbatim. It is the same *idea* or the
same *rhetorical move* arriving in fresh words, which is harder to see while
writing and just as tiring to watch.

**Build a claim ledger.** List every distinct claim the episode makes and assign
each exactly one home section. Then check:

- **One home per idea.** If a claim appears in three sections, two of them are
  padding. Keep the one where it is best demonstrated and cut the others to a
  half-sentence callback at most.
- **Recaps re-phrase, never re-list.** A named set (eight concepts, five passes,
  four checks) gets read aloud in full **once** per episode. Anchoring the thesis
  every few minutes means a one-line callback in new words, not the list again.
  Two full re-reads of the same list in the final five minutes is the most common
  form of this.
- **Budget the rhetorical moves.** Any single sentence shape — the antithesis
  ("X isn't Y, it's Z"), the concession ("beautiful, but useless"), the triad —
  is strong once or twice per episode and invisible by the fifth use. If more
  than about a fifth of sections open with the same shape, vary them.
- **One argument, not eight costumes.** If every section is fundamentally saying
  "this looks good and still fails", the episode has one idea and the sections
  are illustrations of it. That is fine, but say it once at full strength and let
  the sections show different *consequences*, not restate the premise.

The linter reports antithesis density, repeated concept lists and section-opener
similarity. It cannot judge whether a repeat is earned; you can.

### Step 6 — Layer in retention mechanics

Read `references/retention-mechanics.md` before this step. It has the hook
structures, the interrupt cadence, the open-loop technique, and the CTA placement
math, along with the reasoning behind each so you can adapt rather than follow
blindly.

The short version, in order of leverage:

1. **Open loops** are the highest-return technique available and are
   under-used in technical content. Pose a question early, answer it late.
2. **The first 30 seconds** decide most of the outcome. Grab, then promise, then
   stakes.
3. **Pattern interrupts** every 60-90 seconds. In a teaching video the interrupt
   is usually a genuine format shift (talking head to screen capture to diagram),
   not a sound effect.
4. **Two CTAs, placed early and mid**, because very few viewers reach the end of a
   long video and a terminal-only CTA is seen by almost nobody.
5. **Anchor the thesis** every few minutes. Long teaching videos lose people to
   drift, not boredom. An anchor is one line in new words. See Step 5.

Annotate retention risks inline as you write, where you can feel the energy sag.
Marking them is more useful than silently hoping.

### Step 7 — Mark Short seeds

Only after the script is finished, and only where a section genuinely contains a
standalone idea. Re-read "The Shorts boundary" before this step if any part of you
wants to edit the script to make a seed work.

A seed is raw material for the `youtube-shorts-funnel` skill, not a Short:

```
► SHORT SEED
CLAIM:     the one idea, in a sentence that survives with no prior context
PROOF:     the specific footage, number, or failure that demonstrates it
WITHHELD:  what stays in the long video that the Short will point at
WHY IT LIFTS: one line on why this works cold, or why it is a weak candidate
```

Rules:

- **Three to six per episode**, not one per section. Mark the strongest.
- **A seed names an idea, not a line range.** Do not mark spans. The Short gets
  rebuilt with its own hook and bridge; a lifted excerpt has no bridge, and a
  Short with no bridge is the failure mode that looks like a success.
- **A seed must survive with no prior context.** If the claim only lands because
  of something said eight minutes earlier, it is not a seed. Say so in
  WHY IT LIFTS and leave it as a weak candidate rather than deleting it.
- **WITHHELD is the load-bearing field.** It is what the eventual bridge promises.
  A seed without a clear withheld thing produces a generic CTA.

### Step 8 — Hand off to the Shorts skill

Shorts are produced in a **separate pass, after the script is locked**, by
invoking the `youtube-shorts-funnel` skill with the seeds. Do not write Shorts
inside this skill, and do not treat the seeds as drafts of them.

Offer the handoff; do not assume it. The user may want the script alone, may want
Shorts later, or may want Shorts built from footage that does not exist yet.

When it runs, that skill needs: the seed block, the destination episode title, and
whether the footage for the PROOF actually exists. It handles hooks, timing,
on-screen text, the bridge, the pinned comment and the loop-or-click decision.

### Step 9 — Voice pass

Read `references/voice-and-style.md`, then run the checker:

```bash
python3 ~/.claude/skills/youtube-longform-script/scripts/scriptcheck.py <script-path>
```

It flags AI-tell vocabulary, em dashes (which read badly off a teleprompter),
banned openers, cadence problems, repetition, structure gaps, and reports runtime
against word count. Fix what it finds. It is a linter, not an oracle: a flagged
word that is genuinely the right word stays.

**Check that it actually read the script.** The report prints how many spoken
lines it found and the estimated runtime. If a 30-minute script reports two
minutes, the VO markers are in a format it did not parse, and every "OK" in that
report is meaningless. This has happened; do not trust a clean report without
checking the scope line first.

### Step 10 — Deliverables

A finished script file contains:

1. The locked structure table, matching the sections actually written
2. Full VO with visual cues
3. Short seeds, on the sections that earned them
4. Production notes: what must be captured, and what must not be faked

Shorts scripts themselves are a separate deliverable from a separate skill.

## Principles that carry the format

**Teach the craft tool-agnostically before showing your system.** A viewer who
learns something transferable trusts the demo that follows. A viewer who only sees
a product demo has learned nothing they can use and has no reason to stay
subscribed. Concept before implementation is not just structure, it is the
argument for why the channel is worth watching.

**Anchor every abstraction to something on screen.** Three abstract claims in a
row ("empty space isolates, a doorway frames, a corridor leads") teach less than
one claim tied to a specific shot the viewer is looking at. When a concept can be
attached to the episode's own footage, attach it. Returning to the same one or two
examples across sections beats eight unrelated illustrations, because the viewer
watches one thing get better instead of meeting eight strangers.

**The wrong-first beat.** The most valuable material in a technical video is
usually a real mistake: something built the obvious way, that failed, and the
non-obvious correction. It is the hardest content to fake, the most useful to
viewers, and the most differentiated, because everyone else ships the happy path.
Actively hunt for these in the source material and give them their own sections.
A counter-intuitive fix that contradicts advice given earlier in the same video is
not a flaw in the script, it is the best section in it.

**Under-claim.** State plainly what is built, what is partial, and what is
designed but not working. Overclaiming is the fastest way to lose a technical
audience, and the correction always arrives in the comments. An honest limitation
stated by the creator reads as confidence; the same limitation discovered by a
viewer reads as a cover-up.

**Show failure handling, not just success.** A demo where everything works proves
less than a demo where something breaks and the system responds. Never stage this.
A real failure with a real recovery is worth more than a flawless take.

**Specifics over adjectives.** "Four candidates, scored one to five, floor at
three" teaches. "A sophisticated quality system" does not.

**Assert, then qualify once.** Hedged teaching ("this can sometimes make the shot
feel a little more dynamic") is hard to follow and sounds unsure. Say what is
true, then add the exception if there is one. Stacked modals are the written
symptom of an unmade decision.

## What to avoid

These are failure modes specific to long technical videos, not general YouTube
advice:

- **Writing the long video for the Shorts.** The top of this file covers it. It is
  the highest-cost mistake available here because the damage is spread evenly
  across every section and reads as "vaguely repetitive" rather than as a bug.
- **The uniform beat.** Every line the same length, alone on its own line. Produces
  a performance that pauses every two seconds. See Step 4.
- **Front-loading architecture.** Do not open with a system diagram. Show a result
  or a problem first; the diagram means nothing until the viewer wants it.
- **Demo without stakes.** A screen recording with narration is not a section. The
  viewer needs to know what would go wrong before they care that it went right.
- **Teaching in the demo.** If a concept has to be explained during a screen
  capture, it belonged in Part 2. Demos should confirm understanding, not build it.
- **Sponsored-read cadence in a teaching section.** Energy that fits a 10-minute
  entertainment video reads as manic across 40 minutes. Sustained, curious and
  specific beats high-energy.
- **Padding to a runtime target.** Retention loss from padding costs more than the
  extra minutes gain. If the material is 28 minutes, ship 28 minutes.
- **Closing with two recaps.** A checklist recap followed by a list recap is the
  same content twice at the point where the most engaged viewers are still
  watching. Pick one.

## Reference files

- `references/conversation-and-cadence.md` — beat-length budgets, how to write
  connective tissue, question handling, and the repetition patterns that survive a
  vocabulary check. Read before Steps 4 and 5.
- `references/retention-mechanics.md` — hook structures, interrupt cadence, open
  loops, CTA placement, and the retention data behind each. Read before Step 6.
- `references/voice-and-style.md` — voice rules, the AI-tell vocabulary list, and
  how to write spoken versus written English. Read before Step 9.
- `scripts/scriptcheck.py` — automated cadence, repetition, structure and voice
  linter.

## Related skills

- `youtube-shorts-funnel` — builds the actual Shorts from seeds, in a separate
  pass. Never write Shorts inside this skill.
