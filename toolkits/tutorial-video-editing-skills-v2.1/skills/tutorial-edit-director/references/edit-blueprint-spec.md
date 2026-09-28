# Edit blueprint specification

The blueprint is an editor-neutral contract. It records why an edit exists before an adapter translates it into Palmier or DaVinci actions.

## Top-level fields

```json
{
  "schema_version": "1.0",
  "project": {},
  "sources": [],
  "sections": [],
  "beats": [],
  "planning_files": {},
  "style_profile": "style_profile.json",
  "review_gates": []
}
```

## Project

Required:

- `id`
- `editor`: `davinci`, `palmier`, or `other`
- `fps`, `width`, `height`, `duration_sec`
- `audio_spine_source_id`

Recommended:

- `handoff_mode`: `resolve_direct`, `palmier_to_resolve`, or `palmier_only`
- `preserve_original_aroll`: true
- `never_use_intermediate_aroll_render`: true

## Sources

Each source needs a stable `id`, `kind`, and path or editor media ID. Allowed kinds:

- `face_camera`
- `side_camera`
- `screen_capture`
- `dialogue_audio`
- `broll`
- `graphic`
- `music`
- `sfx`

Record rights, original/proxy/intermediate status, duration, frame rate, and hash when available.

## Sections

Each section needs:

- `id`, `title`, `start_sec`, `end_sec`
- `viewer_question`
- `viewer_outcome`
- `proof_or_payoff`
- `memory_anchors`

Ranges must be ascending and non-overlapping.

## Beats

Required:

- `id`, `section_id`, `start_sec`, `end_sec`
- `narrative_function`, `spoken_idea`, `purpose`
- `primary_view`, `visual_source_ids`, `audio_source_id`
- `transition_in`
- `confidence`, `review_required`

Allowed views:

- `face`, `desk`, `screen`, `broll`
- `host_over_content`, `compare`, `graphic`, `hold`

Allowed transition types:

- `none`, `hard_cut`, `j_cut`, `l_cut`
- `dissolve`, `match_cut`, `graphic_bridge`
- `motivated_push`, `motivated_whip`

Every transition needs a reason. Decorative transition types must communicate time, space, action, comparison, or section structure.

Recommended beat fields:

- `retention`: device, setup, payoff beat, and reason
- `continuity_bridge`: audio, motion, gaze, shape, color, or screen geography
- `host_pip`
- `text`
- `screen_focus`
- `broll_plan_item_ids`
- `motion_graphic_ids`
- `music`
- `sfx`
- `notes`

## Planning files

Record paths to:

```text
broll_plan
motion_graphics_plan
audio_plan
rights_ledger
asset_manifest
```

## Confidence

Use 0 to 1. Any beat below 0.70 must set `review_required` true.

## Review gates

Recommended:

- `source_preflight_passed`
- `story_cut_reviewed`
- `planning_package_shown`
- `paid_generation_approved`
- `lookdev_reviewed`
- `full_edit_reviewed`
- `rights_reviewed`
- `audio_qc_passed`
- `technical_qc_passed`

Never mark a gate passed without evidence or reviewer note.
