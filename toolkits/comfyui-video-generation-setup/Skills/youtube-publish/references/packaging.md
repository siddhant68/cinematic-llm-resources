# Packaging — titles, and the title/thumbnail pair

Packaging is decided **before the edit is finished**, not after. If the video
cannot be packaged, its idea is not sharp enough yet, and that is far cheaper to
discover before the edit than after it.

## The two jobs a title does, in order

1. **Tell YouTube what the video is.** The classifier reads the title first and
   uses it to decide which audience to test the video on. A title that is pure
   intrigue with no subject gets shown to nobody in particular and dies of
   irrelevance, not of low CTR.
2. **Make a person click.** Same string, opposite pressure.

Most bad titles fail because they only do one. `The One Rule Nobody Tells You`
does job two and nothing at all for job one. `LTX-2.5 Installation Tutorial Part
3` does job one and nothing for job two.

Doing both in one line is the whole craft:

> **AI light that changes direction between shots — and the one rule that fixes it**

Subject in the first four words (`AI light`), a concrete failure a viewer
recognises, and a promised resolution.

## Structure

**Front-load the subject.** The first four or five words carry
disproportionate weight — for the classifier, and for a viewer scanning a feed,
and because suggestion tiles and notifications truncate around **70 characters**
on most viewports. The 100-character cap is real but almost never the binding
constraint; 40–65 characters is the working range.

**Be specific.** Specific numbers beat round ones because they read as measured
rather than estimated — `16 of 37 renders came out black` lands where `most of my
renders failed` does not. This channel's material is full of real numbers; use
them.

**Open a gap the video closes.** The gap must actually close, on camera, in a
way a viewer would agree was the answer. YouTube now measures satisfaction
directly, so an overpromise buys one click and costs the next ten
recommendations.

**Write in your own register.** The scripts here are calm and precise. A title
in all-caps hype voice is a promise the video breaks in its first thirty seconds,
and the mismatch shows up as a retention cliff rather than as a CTR problem —
which makes it very easy to misdiagnose.

## Formulas that fit this channel

Not a menu to pick from at random — each suits a different kind of episode.

| Shape | When | Example from this material |
|---|---|---|
| **Confession** | You were wrong in a way the viewer might also be wrong | *I benchmarked black videos. Twice.* |
| **Specific absurdity** | A real number that sounds impossible | *My GPU was doing nothing. 500% CPU.* |
| **Reversal** | The obvious move made it worse | *I moved it to the GPU and it got 4× slower* |
| **The named rule** | One transferable principle | *Your AI light has no source. That's why it breaks.* |
| **Constraint** | The setup is itself the hook | *A 22B video model on a MacBook* |
| **Silent failure** | Something that breaks without telling you | *The render said success. The file was black.* |

The last one is close to this channel's signature, and it is worth noticing why
it works: it states a contradiction in seven words and the contradiction *is* the
video.

## Things that do not work here

- **`How to …` and `… Tutorial`** unless the video really is search-intent
  material. They index fine and click badly.
- **`You won't believe`, `SHOCKING`, `INSANE`** — wrong register, and technical
  audiences read them as a tell.
- **Repeating the thumbnail.** If the thumbnail shows a wall of black frames, the
  title should not say "black frames". See below.
- **Numbered lists** (`7 Tips For…`) — they work on a different kind of channel
  and they flatten material that has a real narrative.

## The pair

The single most common waste is a title and thumbnail that say the same thing.
They have complementary jobs:

```
THUMBNAIL   shows the evidence          →  what is this?
TITLE       says what it means          →  why should I care?
                        ↓
              one promise, with a gap
```

Worked example, same video, three packagings:

| Thumbnail | Title | Verdict |
|---|---|---|
| Grid of black video frames | `16 black renders` | ✗ Title repeats the image. No new information. |
| Grid of black video frames | `The log said success` | ✓ Image shows the symptom, title supplies the contradiction. |
| Big text `SUCCESS?` | `The log said success` | ✗ Both carry text, neither carries evidence. |

Test it by covering one and asking whether the other still adds something. If
not, rewrite the title — never the evidence.

## Tags

Nearly worthless for ranking now. The one job they still do is catching
**misspellings and casing variants of proper nouns** the classifier might miss:
`ComfyUI`, `comfy ui`, `LTX-2.5`, `LTX 2.5`, `ltx2`. Ten to fifteen is plenty.
Do not stuff.

## Checks before shipping

- Subject identifiable in the first four words
- 40–65 characters, hard stop at 100
- Reads correctly when truncated at 70
- No hashtag in the title (it suppresses the clickable hashtags above the title)
- Says something the thumbnail does not
- The gap it opens closes on camera
- Sounds like the person in the video
