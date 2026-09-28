---
name: youtube-shorts-funnel
description: Write YouTube Shorts whose job is routing viewers into a long-form video, not earning Shorts views for their own sake. Use whenever the user wants a Short, a Shorts script, a vertical/9:16 video, a clip cut from a long-form video, a hook for a Short, a batch of Shorts from one episode, a pinned comment or CTA for a Short, or wants to plan a Shorts posting schedule. Also use when a Short is getting views but no long-form clicks, when diagnosing why a Short flopped, or when the user says things like "cut Shorts from this", "make this a Short", "shorts for EP01", or asks how to drive Shorts traffic to long-form. Produces a timed hook/value/bridge script with on-screen text, loop-or-click decision, the four bridge surfaces, and a spec check.
---

# YouTube Shorts as a Funnel

Shorts here are a distribution channel for long-form videos, not a content
product. That single constraint decides nearly every choice below, and it is
where this differs from general Shorts advice.

## The constraint that drives everything

YouTube runs two separate paths into the Partner Program, and they never
cross-count:

- 1,000 subscribers plus 4,000 valid public **long-form** watch hours in 12 months
- 1,000 subscribers plus 10 million valid public **Shorts** views in 90 days

Shorts watch time does not contribute to the 4,000 hours. Neither does a
Shorts-acquired subscriber who never watches a long-form video.

So when the goal is long-form watch hours, **the click is the only output that
matters.** Views, likes and completion rate are intermediate signals that buy
distribution; they are not the product. A Short that goes wide and sends nobody
has failed at the only job it had.

This has a sharp practical consequence covered in
`references/the-redirect.md`: several standard Shorts techniques, loop design
most of all, actively work against the click. Read that file before writing.

## Modes

Route by what the user is asking for.

**Extract** — build a Short from an existing long-form script or video. The most
common case when a channel already publishes long-form. The bridge is easy here
because the Short is genuinely drawn from the episode, so "the full breakdown is
on my channel" is concrete and true.

The word is *build*, not *clip*. See "Working from Short seeds" below.

**Native** — write a standalone Short that sets up a long-form. Use when no
suitable long-form section exists but the topic has a long-form to point at.

**Diagnose** — a Short is underperforming. Split the diagnosis in two: is it
failing to earn distribution (a retention problem) or earning distribution and
not converting (a funnel problem)? These have completely different fixes, and
treating a funnel problem as a retention problem is the most common wasted
effort. See the diagnostic tree in `references/shorts-algorithm.md`.

## Working from Short seeds

When the source is a script written by `youtube-longform-script`, the sections
carry `► SHORT SEED` blocks:

```
► SHORT SEED
CLAIM:     the one idea, in a sentence that survives with no prior context
PROOF:     the specific footage, number, or failure that demonstrates it
WITHHELD:  what stays in the long video that the Short will point at
WHY IT LIFTS: why this works cold, or why it is a weak candidate
```

A seed is raw material, not a draft. Map it onto the workflow below:

| Seed field | Where it goes |
|---|---|
| CLAIM | Step 2, the one idea. Rarely survives as the hook verbatim; it is what the hook has to *set up* |
| PROOF | The value section, and the visual column |
| WITHHELD | Step 5, the bridge, and the pinned comment. This is the field that makes the CTA specific |
| WHY IT LIFTS | Whether to build this one at all |

**Write the hook fresh, always.** The long video's version of the idea is paced
for someone who already committed. The Short has three seconds and no goodwill.
Even a strong CLAIM sentence is usually the wrong first line, because it was
written to arrive after a transition.

**A seed does not come with a bridge, and it never will.** The long-form script
deliberately does not contain one, since a bridge inside a teaching section would
be a CTA in the middle of the episode. Writing it is this skill's job, and a Short
shipped without one is the failure that looks like a success.

**Skip the weak seeds.** A seed whose WHY IT LIFTS says it depends on prior
context is telling you the truth. Three strong Shorts beat eight thin ones, and
the long-form script was deliberately not bent to produce more of them.

**Older scripts may carry `► SHORT STARTS` / `► SHORT ENDS` spans instead.** Treat
those as seeds with the boundaries ignored, not as cut points. In production
scripts, none of those spans contained a bridge and one ran to 160 seconds. Read
the span for the idea, then restructure from zero.

## Workflow

### 1. Establish the destination first

Before writing a word of the Short, name the exact long-form video it points to
and the specific thing in that video that is not in the Short.

This ordering is deliberate. A Short written first and given a CTA afterwards
almost always gets a generic one, because there is nothing specific to promise.
Knowing the destination changes what you withhold, which changes the hook.

If no long-form exists on the topic yet, say so and recommend building it first.
A Short pointing at nothing is a Short that cannot do its job.

### 2. Pick the one idea

A Short carries exactly one idea. Not a summary of the episode, not three tips.
One claim, one demonstration, one payoff.

When working from a long-form script, the ideas that work are the ones that
resolve on their own: a claim, a demonstration, and a payoff that does not need
anything said earlier in the episode. That is exactly what a `► SHORT SEED`
records. A section that only lands because of context from eight minutes earlier
is not a candidate, however good it is inside the episode.

### 3. Write the first three seconds first, and separately

The opening decides whether the Short gets distribution at all. Viewed-vs-swiped
below roughly 60% means it stops there regardless of how good the rest is.

Three things happen simultaneously on frame one:

- **A visual that earns the next second.** No logo, no title card, no talking
  head easing in. Something already in motion or already strange.
- **The first spoken line, landing inside about 1.5 seconds.** If the line takes
  longer than two seconds to say, it is too long. Cut it.
- **On-screen text, three to five words, in the middle third of the frame.**
  Most Shorts viewing is muted, so the text is carrying the hook, not decorating
  it. The top ~20% and bottom ~25% of the frame are platform UI; text there is
  covered.

Write three hook options and pick, rather than writing one and defending it.
Hook archetypes and the conditions each suits are in
`references/shorts-algorithm.md`.

### 4. Structure the body

```
0-3s      HOOK          the claim, the tension, or the result
3-8s      ESCALATE      a turn, a stake, or a specific that sharpens it
8-30s     VALUE         one complete, genuinely useful idea
last 5-8s BRIDGE        the click
```

The value section has to be real. A Short that teases without delivering trains
the audience to ignore the next one, and the bridge is asking them to spend ten
times more time with you. Earning it requires giving something first.

Connect beats with "but" and "so", not "and then". A list is not a Short; a
sequence with tension is.

### 5. Write the bridge

The single highest-leverage part of the script, and the part most likely to be
written lazily. Full craft in `references/the-redirect.md`; the essentials:

- Name the destination concretely, by topic. Not "check out my channel".
- Name what is in it that is not in the Short. This specific promise is the
  lever; without it the click does not happen.
- Do not ask for a subscribe instead. It converts worse for this goal, and
  Shorts-acquired subscribers who never click through are close to worthless
  against a long-form watch-hours target.
- Fire on multiple surfaces: in-video spoken line, on-screen text, pinned
  comment, end frame. Bridges land far more reliably when three or more agree.

### 6. Decide: loop or click

These compete for the same final seconds, and the skill's default is the click.
`references/the-redirect.md` covers when a loop is still the right call. Make the
choice explicitly rather than letting it happen by accident, and say which one
you chose and why.

### 7. Spec and voice check

```bash
python3 ~/.claude/skills/youtube-shorts-funnel/scripts/shortscheck.py <script-path>
```

Checks pacing against the target length, hook timing, bridge presence, banned
CTA patterns, and the loop/click conflict. Voice rules carry over from the
long-form skill: no em dashes in spoken lines, no AI-tell vocabulary, no
greeting. See `youtube-longform-script/references/voice-and-style.md`.

## Output format

```
SHORT: [working title]
SOURCE: [long-form episode + section, or "native"]
DESTINATION: [exact long-form title]
THE WITHHELD THING: [what's in the long-form that isn't here]
TARGET LENGTH: [seconds]  LOOP OR CLICK: [which, and why]

TIME     | SPOKEN                    | ON-SCREEN TEXT      | VISUAL
---------|---------------------------|---------------------|------------------
0-3s     |                           | (3-5 words, middle) |
3-8s     |                           |                     |
8-30s    |                           |                     |
last 5-8 |                           |                     |

PINNED COMMENT: [one line + link, naming the specific extra]
END FRAME: [what's on screen]
TITLE: [4-6 words, front-loaded — ~40 chars visible]
```

## Principles

**Distribution is a gate, conversion is the goal.** Retention work buys reach;
reach without a bridge produces nothing. Both are needed, in that order, and
optimizing only the first is the common failure.

**A niche audience converts better than the benchmarks suggest.** Published
Shorts-to-long-form conversion figures are blended across entertainment content
where viewer intent is near zero. A technical Short reaches people actively
trying to solve that exact problem. Expect to beat the averages, but plan with
the conservative number.

**Never fake the excerpt.** If the Short implies the long-form contains
something it does not, the click converts to a bounce and the channel gets a
worse signal than no click at all.

**Shorts decay.** Algorithmic push drops off sharply after about a month, so
Shorts are a flow, not a library. Consistency beats any individual Short. Also
do not judge one too early: they can start moving several days after upload.

## References

- `references/shorts-algorithm.md` — distribution mechanics, retention gates by
  length, format specs, hook archetypes, the diagnostic tree. Read before
  writing or diagnosing.
- `references/the-redirect.md` — the funnel math, the four bridge surfaces, CTA
  craft, and the loop-versus-click tension. Read before writing the bridge.
- `scripts/shortscheck.py` — spec and pacing linter.

## Related skills

- `youtube-longform-script` — writes the destination episode and marks the
  Short seeds. Shorts are always a separate pass after that script locks, and
  the long video is never edited to make a Short work.
