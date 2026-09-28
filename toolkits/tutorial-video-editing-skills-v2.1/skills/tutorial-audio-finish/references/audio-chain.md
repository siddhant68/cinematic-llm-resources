# Audio chain reference

## Dialogue source and repair

Start with source gain and clip-level phrase matching. Repair edits with handles, matched room tone, and short equal-power or equal-gain fades chosen by ear. Do not ask a compressor to correct wildly different clip levels.

## Noise and voice isolation

Use a representative noise-only region to understand the floor. Apply the minimum repair that improves comprehension. Heavy isolation can remove breath detail, smear consonants, and make room tone pump.

## EQ

Filter confirmed rumble, not body. Remove resonances narrowly and shape broad tone gently. Check whether laptop speakers still carry the voice.

## Compression

Use moderate dynamics control that preserves articulation. Listen for breaths becoming louder than words, flattened emphasis, and ambience pumping after phrases.

## De-essing

Target actual harsh consonants. Avoid dulling all high-frequency detail.

## Bus order

A sensible starting topology:

```text
Dialogue clips -> Dialogue bus
Natural sound -> Natural sound bus
Music -> Music bus
SFX -> SFX bus
All buses -> Main mix bus
```

Use bus processing lightly and keep clip-level automation available.

## Final limiter

Use the limiter only for delivery safety and modest level control. Do not solve an unbalanced mix by crushing the master.
