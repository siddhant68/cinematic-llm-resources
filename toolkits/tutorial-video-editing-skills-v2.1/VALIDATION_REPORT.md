# Validation report

Validation date: 2026-09-10

## v2.1 installation-handoff update

- Updated the setup contract so DaVinci Resolve is not assumed to be installed.
- Added official-source application installation, first-launch, disposable edit/render verification, prerequisite installation, edition selection, and restricted escalation rules.
- Added environment setup controls to the episode-brief template and example.
- Updated and repackaged `davinci-tutorial-builder`; its installable `skill.zip` passed the skill validator and ZIP integrity check.
- Revalidated every editable skill after the update.
- Verified both episode-brief JSON files parse successfully.
- No live DaVinci installation, license activation, operating-system elevation, or MCP connection was executed in this environment.

## Skill-package validation

All eight editing skills passed the skill validator and packaging workflow:

- `tutorial-edit-director`
- `tutorial-broll-producer`
- `tutorial-view-design`
- `tutorial-motion-graphics`
- `tutorial-audio-finish`
- `davinci-tutorial-builder`
- `palmier-tutorial-builder`
- `tutorial-qc`

Each skill was packaged independently as `skill.zip`. All eight archives passed ZIP integrity checks and contain no `__pycache__`, `.pyc`, or `.DS_Store` files.

## Deterministic checks

- `validate_episode_brief.py`: the completed example produced zero errors; only expected missing-media warnings were allowed.
- `validate_edit_blueprint.py --strict`: zero errors and zero warnings.
- `validate_broll_plan.py --strict`: zero errors and zero warnings.
- `download_approved_assets.py`: guarded dry-run and receipt generation passed.
- `validate_style_profile.py --strict`: zero errors and zero warnings.
- `validate_motion_graphics_plan.py --strict`: zero errors and zero warnings.
- `validate_audio_plan.py --strict`: zero errors and zero warnings.
- `download_approved_audio.py`: approved-entry dry-run, quarantine path, and receipt generation passed.
- `align_retakes.py`: 21 of 21 regression cases passed.
- `check_mcp_config.py`: accepted a representative compound-mode MCP configuration and retained the required connectivity caveat.
- Python compilation: every bundled Python file compiled successfully.

## Media utility fixture

A generated 1920x1080, 30 fps H.264/AAC fixture at 48 kHz was used to exercise local media analysis.

- `analyze_audio.py` completed with zero errors and zero warnings after the fixture was set inside the bundle's practical house range.
- `qc_media.py --strict` completed with zero errors and zero warnings, including stream, frame-size, black/freeze/silence, and loudness checks.

## Retake regression coverage

The 21-case suite covers cut-off flubs, nested retakes, paragraph restarts, repeated scripted lines, refrains, WhisperX and Scribe word shapes, invalid segment-only transcripts, semantic filler, ad-libs, skipped lines, ASR omissions, spoken-number normalization, no-silence restarts, duplicate complete takes, non-negative padding, cascade failures, partial supersedes, and full supersedes.

## Boundary of validation

These checks establish skill structure, schema behavior, script execution, packaging integrity, and local media-analysis behavior. They do not establish the visual quality of a real edit or a live MCP connection to the user's Resolve installation. The workflow therefore requires a disposable MCP connection test, a 60-90 second look-development render, representative frame review, and a final human editorial/QC pass.
# Session refresh validation — 2026-09-15

- All eight `SKILL.md` files route only to a relevant, local progressive-disclosure reference.
- All eight skill folders pass the bundled `quick_validate.py` frontmatter and scaffold checks.
- Local session reference paths exist inside each skill so installable archives remain self-contained.
- Installable ZIP archives were rebuilt from the refreshed editable skill directories and tested with `unzip -t`.
- `CHECKSUMS.sha256` was regenerated after packaging.
