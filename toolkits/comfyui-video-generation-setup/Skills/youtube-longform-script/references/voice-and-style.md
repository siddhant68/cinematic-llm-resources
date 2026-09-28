# Voice and Style

How the spoken lines should sound, and the specific patterns that make a script
read as machine-written. Applied as a final pass, then verified with
`scripts/scriptcheck.py`.

## Contents

- [Spoken English is not written English](#spoken-english-is-not-written-english)
- [Punctuation for a teleprompter](#punctuation-for-a-teleprompter)
- [The AI-tell vocabulary](#the-ai-tell-vocabulary)
- [Structural tells](#structural-tells)
- [Openers and closers to avoid](#openers-and-closers-to-avoid)
- [Specificity](#specificity)
- [Voice for a technical teaching channel](#voice-for-a-technical-teaching-channel)
- [Title and thumbnail](#title-and-thumbnail)

---

## Spoken English is not written English

The most common failure in AI-drafted scripts is prose that is perfectly correct
and impossible to say. Read every line out loud. If you run out of breath, or
stumble, or it sounds like an essay, rewrite it.

What changes when writing for speech:

- **Sentences get shorter.** A written sentence can hold three clauses. A spoken
  one holds one, sometimes two.
- **Fragments are fine.** "Not because it is hard. Because it is boring." That is
  two fragments and it is better speech than one correct sentence.
- **But shortness is a floor, not a target.** This is the rule most often taken
  too far. Applied uniformly it produces a script where every line is six words
  long and sits alone, the performer pauses after every one, and forty minutes
  becomes a litany of pronouncements. Real speech runs a couple of connected
  clauses, then drops a short one to land the point. If every line is short,
  nothing lands. Beat-length targets are in
  `conversation-and-cadence.md`.
- **Contractions always.** "You are not going to" is written English. "You're not
  going to" is speech.
- **Repetition is a feature.** In writing, repeating a phrase looks careless. In
  speech it lands the point. A listener cannot scroll back.
- **One person to one person.** "You", not "you guys" or "everyone". "I", not
  "we", unless it is genuinely a team.

---

## Punctuation for a teleprompter

**Avoid em dashes and en dashes in spoken lines.** Two reasons. They are the most
recognizable signature of machine-written text in current usage, and they give a
performer no information: a dash could be a pause, a shift in tone, or nothing.

Use instead:
- `..` for a natural pause where you would reach for a dash
- A full stop, if the clauses can stand alone. Usually they can.
- A comma, if the pause is short

This applies to spoken lines. Dashes in the structure tables, production notes and
headers of a script document are fine, since nobody performs those.

---

## The AI-tell vocabulary

These words are rare in natural speech and common in generated text. A script
carrying several reads as machine-written even to viewers who could not say why.

**Verbs:** leverage, utilize, facilitate, streamline, harness, foster, cultivate,
delve, navigate (figuratively), unlock (figuratively), empower, elevate

**Adverbs:** fundamentally, essentially, ultimately, crucially, notably,
significantly, arguably

**Nouns:** landscape, ecosystem, paradigm, realm, tapestry, journey (figuratively),
game-changer, deep dive, treasure trove

**Adjectives:** robust, seamless, cutting-edge, powerful (as filler), comprehensive

**Phrases:** "in today's fast-paced world", "at the end of the day", "it's not just
X, it's Y", "the world of", "when it comes to", "let's dive in", "without further
ado", "needle-mover"

The replacement is almost always the plain word. Use instead of utilize. Use
instead of leverage. Strong instead of robust. Field or area instead of landscape.
If deleting the word costs nothing, delete it.

This is a list of *smells*, not banned tokens. "Navigate" is correct when talking
about navigation. "Journey" is correct when there is travel. Judgment applies.

---

## Structural tells

Harder to spot than vocabulary and just as recognizable.

**The rule of three.** "Faster, cheaper, and easier." Generated text reaches for
triads constantly. Real speech uses one item, or two, or four. Break up triads
unless three is genuinely the count.

**Symmetrical parallelism.** Three sentences with identical shape in a row reads
as generated. Vary sentence length deliberately; a short one after two long ones
lands hard.

**The summarizing close.** Ending every section with "so as you can see..." or
"and that is why...". A section can end on the thing itself.

**Hedging stacks.** "It is worth noting that it may potentially be the case that."
Say the thing.

**Over-signposting.** "First, I will explain X. Then, I will cover Y. Finally, Z."
One forward hook is enough; a table of contents in speech is dead air.

---

## Openers and closers to avoid

**Never open a video or a section with:**
- "Hey guys, welcome back to the channel"
- "Before we get started"
- "In this video, we will..."
- "So, what is X? Let us find out."
- Any greeting at all in the first line

**Never close with:**
- "Thanks for watching"
- "Don't forget to like and subscribe"
- "That's all for today"
- "In conclusion"

The end of a video is the highest-intent moment available: everyone still there is
maximally engaged. Spending it on a wind-down wastes it. End on a reason to do the
next thing, whether that is watching the next episode or acting on what they just
learned.

---

## Specificity

One real number beats any adjective. This matters more in technical content than
anywhere else, because specificity is the signal that separates someone who built
the thing from someone summarizing it.

| Weak | Strong |
|---|---|
| "significantly faster" | "cut it from 40 seconds to 6" |
| "a sophisticated verification system" | "four checks derived per view, plus one identity check" |
| "it often fails" | "roughly one in five runs" |
| "a lot of manual work" | "about six hundred copy-paste operations" |

If a number is not known, say so plainly rather than reaching for an adjective.
"I have not measured this properly, but it felt like about half" is more credible
than "dramatically better".

---

## Voice for a technical teaching channel

The register that works: **calm, specific, and willing to be wrong.**

Concretely:

**Admit the mistake first.** "I got this wrong for months" earns more trust than
any credential. It also makes the correction memorable, since the viewer now has a
story to hang it on.

**State limits without apologizing.** "This part works. This part is half-built.
This part is designed and not started." No hedging, no overselling, no defensive
justification. Flat statements of status read as confidence.

**Do not sell.** The system being demonstrated is evidence for the teaching, not a
product. If a section starts sounding like a pitch, it has drifted; move the claim
into a demonstration or cut it.

**Respect prior knowledge without assuming it.** Explain the thing, but do not
explain that you are about to explain it, and do not apologize for covering
basics.

**Let the material be interesting.** Technical content does not need manufactured
enthusiasm. Stating a genuinely surprising fact plainly is more effective than
performing excitement about a mundane one. If a section needs hype to be
interesting, the problem is the section.

---

## Title and thumbnail

Not the script's job, but the script has to honor them, so they are decided
together.

- **The title is a promise, not a summary.** It says what the viewer walks away
  with, or names the tension that gets resolved.
- **Title and thumbnail are read together in under a second.** They should not
  repeat the same words. The title says what the thumbnail cannot show, and the
  reverse.
- **Front-load the words that earn the click.** Mobile and sidebar truncate around
  sixty characters.
- **The opening thirty seconds must pay off the title in the viewer's own terms.**
  A title that overpromises spikes click-through and craters retention, which
  performs worse than a modest title that delivers.
- **Never clickbait a payoff the video does not contain.** Beyond the ethics, the
  retention cost is severe and the comments become unusable.
