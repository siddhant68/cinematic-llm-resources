# Research notes and source policy

Last reviewed: 2026-09-12

The workflow uses current primary documentation where possible. Re-check changing product behavior at runtime, especially pricing, model availability, feature eligibility, API quotas, and editor/MCP compatibility.

## DaVinci Resolve and MCP

- DaVinci Resolve: https://www.blackmagicdesign.com/products/davinciresolve
- DaVinci Resolve Studio: https://www.blackmagicdesign.com/products/davinciresolve/studio
- Blackmagic support/downloads: https://www.blackmagicdesign.com/support/
- Selected third-party Resolve MCP: https://github.com/samuelgursky/davinci-resolve-mcp
- MCP installation guide: https://github.com/samuelgursky/davinci-resolve-mcp/blob/main/docs/install.md
- MCP README and limits: https://github.com/samuelgursky/davinci-resolve-mcp/blob/main/README.md

The MCP is not an official Blackmagic product. The agent must pass a disposable-project test against the installed Resolve version before touching production media.

## Palmier

- Multicam: https://www.palmier.io/docs/multicam
- Export: https://www.palmier.io/docs/export
- Color, masks, and effects: https://www.palmier.io/docs/color-and-effects

Palmier is restricted to optional early rough-cut work. Transfer FCPXML, originals, references, and notes; never promote a flattened Palmier render to authoritative A-roll.

## Licensed visual and audio assets

Preferred starting points, subject to exact-asset review:

- Pexels license: https://www.pexels.com/license/
- Pixabay license summary: https://pixabay.com/service/license-summary/
- Mixkit licenses: https://mixkit.co/license/
- YouTube Audio Library: https://support.google.com/youtube/answer/3376882

A platform-level license summary is not proof that a specific asset is free of trademarks, privacy/publicity rights, recognizable-property restrictions, embedded third-party content, or attribution obligations. Record the exact source page and terms at download time.

## Generative media

- Higgsfield documentation/help: https://higgsfield.ai/
- ComfyUI LTX workflows: https://docs.comfy.org/tutorials/video/ltx/ltx-2

Confirm the exact live generation cost before each paid request. Check the exact checkpoint and service terms; repository-code licensing and model-weight licensing may differ.

## YouTube packaging and release

- Title and thumbnail A/B testing: https://support.google.com/youtube/answer/16391400
- Custom thumbnail guidance: https://support.google.com/youtube/answer/72431
- Thumbnail upload API: https://developers.google.com/youtube/v3/docs/thumbnails/set
- Title and thumbnail tips: https://support.google.com/youtube/answer/12340300
- Description tips: https://support.google.com/youtube/answer/12948449
- Video chapters: https://support.google.com/youtube/answer/9884579
- Comments and pinning: https://support.google.com/youtube/answer/6000964
- End screens: https://support.google.com/youtube/answer/6388789
- Cards: https://support.google.com/youtube/answer/6140493
- Upload API: https://developers.google.com/youtube/v3/docs/videos/insert
- Top-level comment API: https://developers.google.com/youtube/v3/docs/commentThreads/insert
- Audience retention: https://support.google.com/youtube/answer/9314415
- Impressions and click-through-rate guidance: https://support.google.com/youtube/answer/9314486

Key implementation consequences:

- Build title and thumbnail as a truthful pair and evaluate the opening against the same promise.
- Create actual thumbnail files, including a high-quality master and an API-safe derivative.
- Use native A/B testing only when the video/channel state is eligible; do not manually disrupt an active test without reason.
- The API may post a top-level comment when comments are available, but pinning requires visible YouTube-interface verification.
- Private uploads do not offer a comment surface; pin after an approved eligible state.
- Reserve the final seconds for the end screen rather than covering essential picture, subtitles, or CTA.
- Read CTR in the context of traffic source, impressions, retention, and watch time rather than as a standalone score.

## Editorial continuity

- J-cuts and L-cuts: https://helpx.adobe.com/premiere/desktop/edit-projects/trim-clips/perform-j-cuts-and-l-cuts.html

Transitions and SFX are not retention by themselves. Prefer audio continuity, useful view changes, proof, open questions, progress, movement/gaze matching, and payoffs.

## Policy encoded in the skills

- Use owned evidence before generic stock.
- Download only after recording exact source, license, creator, restrictions, and hash.
- Do not infer commercial permission from search visibility.
- Estimate paid-generation cost before submitting.
- Preserve camera originals through every editor handoff.
- Upload private first and verify API readback.
- Treat YouTube Studio visual readback as mandatory for cards, end screens, pinning, experiments, and final release state.
- Never publish without explicit approval.
- Never promise virality; optimize alignment, comprehension, watch time, and continuation.
