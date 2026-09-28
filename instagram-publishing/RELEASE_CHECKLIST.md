# Release checklist

Use a dedicated `release/` folder for the new reel. Keep local masters and private references there; publish only the intended outputs.

## 1. Establish the facts

- [ ] Read the handoff, script, generation log, prompt files, and music/source licence notes.
- [ ] Record the exact number of clips, model, settings, takes, retries, and edit steps from the log.
- [ ] Identify the approved post order, account, CTA, and any claims or media that must not appear publicly.
- [ ] Watch every final video, including its beginning, transitions, and final second.
- [ ] Check actual resolution, aspect ratio, duration, sound, integrated loudness/peak where available, black frames, caption readability, and clipped edges.

## 2. Package each post

- [ ] Film: choose the correct master or feed-safe version, handpick a cover, write the story caption, and include required music credit.
- [ ] Tutorial: choose the finished tutorial, handpick a distinct cover, describe the actual method and honest limitations, and make the CTA fulfilable.
- [ ] Carousel: use 2–20 original images/videos in the intended order, make each slide a consistent 4:5 or 1:1 size, and write a caption that points to the exact prompt pack.
- [ ] Check cover title legibility in 9:16, the centre 4:5 feed preview, and the centre profile-grid crop.
- [ ] Set `aiLabel` explicitly in every manifest. Use `true` for realistic AI imagery.
- [ ] Confirm captions are at most 2,200 characters and have no unsupported claims or wrong model names.
- [ ] Ensure third-party photos, private identity references, download folders, login data, and licensed assets are not in the public GitHub pack.

## 3. Preflight and publish

- [ ] Run `--check` for each manifest and inspect the output.
- [ ] Use `--stage` when the UI or script has changed; inspect its crop, cover, AI label, caption, and ready-to-share screenshot.
- [ ] Publish the film; open its URL and check cover, image, sound, caption, AI label, and profile tile.
- [ ] Publish the tutorial and perform the same check.
- [ ] Publish the carousel; inspect the first **and last** slide and confirm the slide count/order.
- [ ] Add any promised comment and verify it after reloading the post. Record whether Instagram actually offers a Pin action.
- [ ] Record all URLs, run IDs, any claim notice, and unresolved manual tasks in a release record.

## 4. Public resources

- [ ] Put the exact shareable prompts and original generated assets in a reel-specific folder of this repository.
- [ ] Link that folder from the carousel caption and confirm the GitHub link loads after push.
- [ ] Commit and push only reviewed files. Verify the remote folder and release record.
