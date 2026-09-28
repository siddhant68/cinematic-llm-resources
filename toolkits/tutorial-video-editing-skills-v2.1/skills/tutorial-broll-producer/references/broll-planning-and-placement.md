# B-roll planning and placement

## Plan at the claim level

For each spoken beat, write one sentence for the information job before naming a visual. Useful jobs:

- `evidence`: show the actual output, failure, data, or result
- `demonstration`: show how to perform the action
- `orientation`: show where the presenter is, what tool is open, or how elements relate
- `comparison`: make a difference visible
- `emotion`: preserve reaction, stakes, or human presence
- `analogy`: make an abstract concept easier to imagine without presenting it as proof
- `pacing_breath`: create a deliberate pause after dense instruction
- `payoff`: answer an earlier visual question or reveal the result

## Selection ladder

Use this ladder in order:

1. Actual user-owned evidence.
2. Exact screen recording or product capture.
3. A custom diagram or motion graphic.
4. Legally verified stock.
5. Generated illustration.
6. Host or intentional hold.

Do not force a lower rung when a higher rung exists.

## Host visibility

Keep the host visible when:

- personal credibility or emotion matters
- the host is reacting to proof
- the explanation is interpretive rather than procedural
- the viewer benefits from a stable human anchor through a long visual

Remove or reduce the host when:

- the interface must be read
- the result needs the full frame
- the host covers the point of interest
- the visual already carries the emotional beat

## Timing patterns

- `picture_leads`: reveal the next visual slightly before the sentence names it; useful for curiosity and orientation
- `audio_leads`: start the next sentence before changing picture; useful for J-cuts and smooth section movement
- `keyword_land`: cut on the word that resolves what the audience should inspect
- `action_match`: switch views on a shared physical or screen action
- `reaction_return`: return to the host after proof for interpretation
- `hold_after_payoff`: give the viewer time to absorb a result before the next claim

## Duration

Duration follows comprehension, not a fixed cadence. Keep a visual long enough to:

- identify the subject
- understand the relevant action or comparison
- read any essential text
- absorb the implication

Cut sooner only when the next image adds new information. Reframing the same information is not progress.

## B-roll plan fields

Every item should record:

```text
beat_id
spoken_line
information_job
audience_question
visual_form
source_candidate_ids
selected_source_id
start_sec/end_sec or relative cue
host_visibility
natural_sound
texture_profile
entry_bridge
exit_bridge
rights_status
confidence
review_required
```
