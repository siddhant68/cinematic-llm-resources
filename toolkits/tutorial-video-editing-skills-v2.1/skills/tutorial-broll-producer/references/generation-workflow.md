# Generated B-roll workflow

## Choose LTX or Higgsfield

Use LTX/ComfyUI when:

- local iteration and control matter
- the shot can be tested cheaply
- the exact installed checkpoint permits commercial use
- the user has a working workflow and sufficient hardware

Use Higgsfield when:

- the shot is a high-value hero visual
- a supported model offers a material quality advantage
- references or motion requirements exceed the local workflow
- the user approved the current estimated credit cost

Use neither when actual evidence, a screen recording, a diagram, or licensed stock is clearer.

## Prompt contract

Every prompt must include:

```text
story role
illustrative/evidentiary label
duration and aspect ratio
opening composition
subject identity and action
environment and relevant objects
camera distance, angle, movement, and speed
lighting direction and quality
motion continuity and environmental response
ending composition
negative constraints
text/logo policy
reference assets and rights
```

For tutorial B-roll, prefer one coherent action over multiple shots packed into one generation. Avoid embedded readable text unless the model is explicitly being tested for text.

## LTX chronology

Write chronologically:

1. Opening state.
2. Primary action.
3. Camera behavior.
4. Secondary environmental motion.
5. Ending state suitable for the next edit.

Record workflow JSON, checkpoint, model version, seed, resolution, duration, and license URL.

## Higgsfield cost gate

Before submission:

1. Select the exact model, duration, resolution, and number of outputs.
2. Obtain the current platform or API estimate using those same parameters.
3. Add planned spend to `higgsfield_spend_plan.json`.
4. Confirm that spend plus reserve remains within the correct pool.
5. Confirm user approval.
6. Submit once.

If a submission response is ambiguous, check job history/status before retrying. Do not create duplicate charges through blind retries.

## Acceptance review

Reject or regenerate when the clip contains:

- identity drift that matters to the story
- unreadable or warped interface/text
- impossible object interaction
- loop discontinuity where looping is required
- camera motion that fights the next cut
- inconsistent light direction
- obvious morphing, duplicated limbs, or temporal shimmer
- a factual implication the clip cannot support

Use a simpler visual form when repeated generation fails.
