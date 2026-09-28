# Shorts Distribution and Format

How Shorts get distributed, the gates a Short has to clear, the format
constraints that silently kill one, and how to diagnose a failure. Figures are
directional — they come from published creator-analytics studies and shift as
the platform changes. Where two credible sources disagree, both are noted rather
than averaged into a false precision.

## Contents

- [How a Short gets distributed](#how-a-short-gets-distributed)
- [The signals that matter](#the-signals-that-matter)
- [Retention gates by length](#retention-gates-by-length)
- [Format specs that silently kill a Short](#format-specs-that-silently-kill-a-short)
- [Views versus engaged views](#views-versus-engaged-views)
- [Hook archetypes](#hook-archetypes)
- [Cutting Shorts from long-form](#cutting-shorts-from-long-form)
- [The diagnostic tree](#the-diagnostic-tree)

---

## How a Short gets distributed

Shorts are seeded to a small test audience, then scaled if early engagement
holds. This is why channel size barely matters on any individual Short: each one
is judged largely on its own performance, which is good news for a small channel
and means a single Short cannot coast on the channel's reputation.

Two timing facts change how you should behave:

- **A Short can start moving several days after upload**, sometimes as late as
  the fourth day. Judging one at 24 hours is premature.
- **Algorithmic push decays after roughly a month.** Shorts are a flow, not a
  library. This makes consistency more valuable than any individual upload, and
  it means an old Short is not a renewable source of clicks.

Click-through rate, the currency of long-form, is essentially irrelevant here.
Shorts autoplay, so there is no thumbnail decision. The equivalent signal is
whether people swipe away.

---

## The signals that matter

Roughly in order of weight:

| Signal | What it measures | Rough gate |
|---|---|---|
| **Viewed vs swiped away (VVSA)** | Did they stay past the opening | Below ~60% tends to stall. 70-90% tends to widen. |
| **Completion / percentage viewed** | Did they watch it through | ~70%+ associated with aggressive promotion |
| **Loop / replay rate** | Did it replay | Heavily weighted; above 100% percentage viewed means loops are firing |
| **Comments and shares** | Did it provoke | Weighted more than likes |
| **Likes** | Weak signal | Do not diagnose from this |

Sources differ slightly on the VVSA floor — one puts the breakage point below
50%, another around 60%. Treat anything under 60% as a failed opening and
rewrite the first three seconds rather than tuning the body.

Note the ordering implication: the opening decides VVSA, VVSA decides whether
anything else gets measured. Effort spent anywhere else while the opening is
weak is wasted.

---

## Retention gates by length

Percentage-viewed thresholds where distribution tends to widen:

| Length | Target average percentage viewed |
|---|---|
| Under 30s | ~65%+ |
| 30-60s | ~50%+ |
| 60s+ | ~40-45%+ |

**On length.** Sources disagree: one puts the sweet spot at 15-60 seconds with
peaks around 13s and 60s, another at 30-45 seconds. They agree on the failure
mode at the bottom: very short Shorts, under about 15 seconds, can fail to clear
absolute watch-time bars even at perfect retention.

For a Short that has to teach something and then send the viewer somewhere,
**30-45 seconds is the working default.** Long enough to deliver a real idea and
a bridge, short enough to hold retention. Going toward the three-minute ceiling
is rarely right and adds a licensing complication (see specs below).

---

## Format specs that silently kill a Short

These fail quietly. Nothing errors; the Short just underperforms or never enters
the feed.

| Spec | Requirement | Failure mode |
|---|---|---|
| **Aspect ratio** | 9:16 vertical, 1080x1920 | 16:9 with letterbox bars gets classified as long-form and never enters the Shorts feed at all |
| **Caption safe zone** | Middle third of frame | Top ~20% and bottom ~25% are platform UI; text there is covered |
| **Burned-in captions** | Yes | A large share of viewing is muted; uncaptioned Shorts lose the hook entirely |
| **Watermarks** | None | TikTok watermarks are demoted |
| **Title** | 4-6 words, front-loaded | Around 40 characters visible before truncation |
| **Music** | Original audio preferred | Each licensed track takes a large slice of the revenue share; Content ID licensing also restricts longer Shorts |
| **Visual change** | Frequent | One source suggests every ~3 seconds; see note below |

**On visual change cadence.** The every-three-seconds guidance comes from
high-velocity entertainment formats. For a technical Short where someone is
following an explanation, cutting that aggressively works against comprehension.
Change the frame often enough to prevent a static talking head — a reframe, a
cut to the screen, a diagram — but let an idea land before cutting away from it.
The underlying principle is avoiding visual monotony, not hitting a stopwatch.

---

## Views versus engaged views

A view now registers on essentially any playback, and loops add more. This
inflates raw view counts substantially relative to older reporting.

**Engaged views** is the metric that reflects retained attention, and it is the
one that counts toward the Shorts monetization path. When reading analytics or
reporting performance, use engaged views. Raw views flatter and mislead.

---

## Hook archetypes

Pick by what the material offers, not by preference. Each has to land inside
about 1.5 seconds of speech plus three to five words of on-screen text.

| Archetype | Shape | Best when |
|---|---|---|
| **Contradiction** | State the thing the audience believes, then deny it | You have a genuinely counter-intuitive finding |
| **Direct callout** | Name the audience and their exact problem | The problem is specific and widely felt |
| **Cold result** | Open on the finished thing, no setup | There is a visually striking output |
| **Number** | Lead with a specific, surprising figure | You have a real measurement |
| **In media res** | Start mid-action, no framing | Something is visibly happening |
| **Stake** | Name what it costs to get this wrong | The consequence is concrete |
| **Withhold** | Name a thing you are about to reveal | Use sparingly; it borrows against the payoff |

For technical content, contradiction and direct callout tend to be strongest,
because the audience arrives with existing beliefs and specific frustrations.
Withhold is the weakest, since it is the one that most easily becomes a tease
the Short does not honor.

---

## Cutting Shorts from long-form

A long-form episode typically yields ten to twenty candidate Shorts. Two things
determine whether they work:

**Restructure, do not clip.** A continuous excerpt performs substantially worse
than the same material rebuilt as hook, value, bridge. The long-form version of
a section is paced for someone who has already committed; the Short version has
to earn attention from zero in three seconds. Same content, different
architecture.

**Pick ideas that stand alone, not sections that open on a claim.** The
long-form script is written as one continuous conversation, so its sections
connect to each other on purpose and most of them open mid-thought. That is
correct for the long video and irrelevant here: you are taking the idea, not the
paragraph. The `► SHORT SEED` blocks name the ideas that survive without context.
An idea that only lands because of something said earlier in the episode is not a
candidate, no matter how well it plays in place.

The strongest candidates share a shape: a counter-intuitive claim, a short
demonstration, and a natural gap that the full episode fills.

---

## The diagnostic tree

When a Short underperforms, find which gate it failed before changing anything.

```
Low reach / few views
  └─ VVSA below ~60%
       → the opening failed
       → rewrite the first 3 seconds only
       → check: logo or intro? slow first line? no on-screen text?
                text outside the safe zone? 16:9 bars?

Decent reach, low completion
  └─ retention curve bleeds through the middle
       → no escalation; the body is one flat note
       → add a turn around 5-8s
  └─ retention holds then drops late
       → payoff buried or absent
       → move it earlier

Good reach, good completion, no long-form clicks
  └─ FUNNEL problem, not a retention problem
       → the bridge is missing, generic, or loop-trapped
       → name the destination and the withheld thing
       → add the pinned comment
       → check whether the loop is competing with the click
```

That last branch is the one most often misdiagnosed, because every visible
metric looks healthy. Against a long-form watch-hours goal, a Short with strong
views and no clicks has failed at its only job.

Re-upload rather than re-edit when fixing a Short. Grading happens from upload.
