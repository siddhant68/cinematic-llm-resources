---
name: youtube-launch-optimizer
description: Review and improve a published long-form YouTube video's launch using channel-specific analytics and the approved release package. Use when examining impressions, click-through rate by traffic source, first-30-second retention, average view duration, watch time, audience-retention dips, A/B title-and-thumbnail results, end-screen performance, playlist continuation, subscribers, comments, or launch posts; when deciding whether to keep, test, or revise packaging; or when producing 24-hour, 72-hour, and 7-day review records. Do not promise virality or make rapid changes from tiny samples.
---

# YouTube Launch Optimizer

Optimize the launch after `youtube-studio-finisher` has published or scheduled the video. Treat the title, thumbnail, opening, topic, traffic source, and audience as a connected system. Do not optimize click-through rate in isolation.

## Required inputs

- video ID and exact publish timestamp/timezone
- approved release manifest and title/thumbnail variants
- final master and first-minute transcript
- channel-level context and comparable recent videos when available
- analytics snapshot exported from YouTube Studio or the YouTube Analytics API
- current A/B test state and eligibility
- end-screen, card, playlist, community-post, and pinned-comment configuration

## Outputs

```text
release-package/post-publish/
  analytics-24h.json
  analytics-72h.json
  analytics-7d.json
  launch-review-24h.md
  launch-review-72h.md
  launch-review-7d.md
  packaging-action.json
  next-video-learnings.md
```

When insufficient data exists, state that clearly and choose `hold` rather than manufacturing certainty.

## Review cadence

Use channel scale and impression volume, not the clock alone. Sensible checkpoints are:

- early operational check after publication: page, comments, processing, captions, and links
- first meaningful analytics review around 24 hours or after a reasonable impression sample
- follow-up around 72 hours
- broader learning review around 7 days
- native A/B result review when YouTube declares a winner or the test ends

Do not swap titles or thumbnails repeatedly during the first few hours. Do not interrupt an active native A/B test with manual changes unless the packaging is inaccurate or unsafe.

## Workflow

### 1. Verify release integrity

Confirm the live page still matches the approved release:

- correct title and thumbnail/test variants
- description, chapters, captions, links, disclosure, and credits
- pinned comment visible when planned
- playlist placement
- cards and end screen
- HD processing and audio
- no restriction, copyright, or monetization surprise

Operational defects take priority over optimization.

### 2. Read reach in context

Evaluate together:

- impressions
- click-through rate
- traffic-source mix
- views from impressions
- browse, suggested, search, subscriptions, notifications, external, and end-screen traffic
- new versus returning viewers when available

A falling CTR can accompany healthy expansion to a broader audience. Compare like-for-like traffic sources and channel history rather than using one universal benchmark.

### 3. Read retention and satisfaction

Inspect:

- first 30 seconds
- first minute
- average view duration and percentage viewed
- relative retention when available
- spikes, dips, and rewatch points
- likes, comments, shares, subscribers, and viewer feedback
- end-screen click rate and next-video continuation

Map every major dip to the exact spoken beat and visual treatment. Distinguish:

- packaging mismatch
- slow or repetitive opening
- premature channel introduction or housekeeping
- unclear section structure
- dense explanation without proof
- irrelevant B-roll or overactive effects
- audio/legibility defect
- natural completion of a viewer's question

### 4. Diagnose before acting

Read `references/analytics-decision-tree.md`.

Common patterns:

- **High impressions + weak CTR + healthy retention among clickers:** packaging may be the main opportunity.
- **Healthy CTR + steep opening drop:** the video is not paying off the click quickly enough; record an editing/hook lesson and avoid masking it with a more aggressive thumbnail.
- **Weak CTR + steep opening drop:** topic/packaging/opening alignment may all be weak; do not assume one thumbnail swap fixes it.
- **Low impressions + healthy CTR and retention:** distribution, topic breadth, channel size, or competition may be limiting reach; hold unless the package is unclear.
- **Search traffic works, browse does not:** retain searchable precision and test a stronger browse-facing visual only when the native experiment supports it.
- **End-screen clicks are weak:** the proposed next video, timing, or final CTA may not fit the viewer's next question.

### 5. Choose one controlled action

Allowed recommendations:

- hold current packaging
- continue native A/B test
- start title-only, thumbnail-only, or paired A/B test when eligible
- stop an inaccurate or harmful variant
- replace the primary title/thumbnail after adequate evidence
- fix description, chapter, caption, link, or pinned-comment defect
- update playlist or end screen
- publish a relevant community follow-up
- record a first-minute editing lesson for the next upload

Prefer one controlled change at a time unless using YouTube's native concurrent A/B test.

### 6. Use the pinned comment and community post deliberately

The pinned comment should extend the conversation with one useful resource, correction, question, or next step. It should not repeat the description or ask for generic engagement.

Use a community post only when it adds a new angle, visual, poll, or discussion prompt. Do not repeatedly repost the same link.

### 7. Produce a decision record

Validate snapshots:

```bash
python scripts/analyze_launch_snapshot.py \
  release-package/post-publish/analytics-72h.json \
  --out release-package/post-publish/analytics-72h-derived.json
```

For every action, record:

- evidence
- traffic-source context
- sample size caveat
- expected mechanism
- exact asset/copy change
- start time
- review time
- rollback condition

## Non-negotiable rules

- Never guarantee that a video will “catch on.”
- Never optimize CTR without considering watch time, retention, and traffic source.
- Never call normal broadening-related CTR decline a failure by itself.
- Never use misleading packaging to repair weak distribution.
- Never make repeated manual title/thumbnail changes during an active native A/B test.
- Never infer a causal result from a tiny or sequential sample.
- Never delete provenance, experiment, or prior-variant records.
