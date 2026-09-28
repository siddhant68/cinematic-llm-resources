# The pinned comment

## The tension, stated up front

The obvious use for a pinned comment is resource links — it is the one placement
where a link never competes with the description fold, and viewers genuinely look
there for the thing you promised on camera.

But across channels that have been measured, **a pin that is mostly a link reads
as promotional and suppresses replies, while a pinned question reliably raises
them.** Well-written pins have been measured lifting comment replies by up to
about 30% against an empty or generic pin — and that lift comes from questions,
not from links.

Both things are true, and they pull in opposite directions. Comments are a
ranking signal and the first hour is when they matter most; links are what you
promised and what actually converts. So the pin has to do both without reading
like an ad.

## The resolution

**Question first, link second, and never more than one link.**

```
The rule in one line: if you can't say where the light is coming from, the
model can't keep it consistent between shots.

Which of these breaks your generations most — light, continuity, or blocking?

Skill file that adds this reasoning to a written scene → <link>
```

Three moves in that: a one-line restatement of the video's payoff (rewards the
person who scrolled down), a question that is genuinely answerable in four words
(low cost to reply), and exactly one link, last.

The full resource list belongs in the **description**, where nobody has to feel
sold to. The pin carries the single most valuable link and nothing else.

## Rules

**Post it before the video is public.** The pin should already be at the top when
the first viewer arrives, not appear an hour later. If it lands after the first
wave, it missed the window it exists for.

**One or two lines.** A pinned paragraph does not get read.

**Ask something answerable in a few words.** "What's your take on cinematic AI
workflows?" is work. "Light, continuity, or blocking — which breaks yours?" is a
one-word reply. The formats that consistently earn replies: a constrained choice,
a timestamp challenge ("what happens at 4:12 — did you catch it?"), a micro-poll,
or a direct question tied to one specific moment.

**Tie it to the video, not the channel.** A generic "what should I make next?"
gets generic answers.

**Never ask for the subscribe in the pin.** It converts worse than a question and
it costs you the reply.

**Block half an hour after publishing** to answer the first replies. Early
replies set what the comment section becomes, and this is the part no automation
can do for you.

## The mechanic you already use

The opening script ends with `comment CINEMATIC and I'll share it along` — a
keyword-reply mechanic. That is a strong pin because it is a *question with a
one-word answer* and a promise, which is exactly the shape that works. Keep it,
but pair it with the payoff line so the pin still gives something to the person
who never comments.

Be ready to honour it. A keyword mechanic that goes unanswered is worse than not
running one.

## Automation boundary

The Data API can **post** a comment (`commentThreads.insert`, 50 units). It
**cannot pin** one — no method exists. So:

1. API posts it, as the channel owner, immediately after publish
2. Browser pins it — `studio.py pin VIDEO_ID --match "<text>"`

Replying to early comments stays manual. It should.
