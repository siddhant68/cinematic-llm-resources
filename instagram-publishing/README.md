# Instagram publishing workflow

This is the workflow used to publish the short film, tutorial, and resources carousel for [@cinematic_llm](https://www.instagram.com/cinematic_llm/). It combines repeatable scripts with editorial review. [Reel 008's release record](REEL_008_EXAMPLE.md) shows a completed three-post run.

## What is here

- [`scripts/`](scripts/) contains the actual Edge/Playwright uploaders and media preparation helpers. No login data, browser profile, screenshots, or run records are included.
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) is the order of operations for each new release.
- [MANIFESTS.md](MANIFESTS.md) describes the input files, commands, and state handling.
- [COVERS_AND_SLIDES.md](COVERS_AND_SLIDES.md) shows how to make and inspect the release artwork.
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) covers UI changes, failed shares, crop problems, and manual takeover.

## Setup

Use macOS with Microsoft Edge, Node.js, npm, Python 3, and FFmpeg/ffprobe available on `PATH`.

```sh
cd instagram-publishing/scripts
npm ci
npm test
node upload.mjs --login --account cinematic_llm
```

Sign in yourself in the Edge window and complete any account verification. The uploader never asks for a password. It saves the signed-in browser session locally in `scripts/.profile/`. That folder must remain private and must never be committed, copied to another machine, or shared. The normal Edge window and this dedicated upload profile are separate.

## Release at a glance

1. Read the reel handoff, narration/script, actual generation log, and prompt files. Distinguish creative intent from verified results. Write claims only from the actual run, including what did not work.
2. Inspect the finished video end to end. Confirm dimensions, duration, image edges, audio, music credit or licence terms, and any on-screen text. Use [feed-safe framing](MANIFESTS.md#feed-and-profile-crops) if a 9:16 Reel needs to remain fully visible in Instagram's narrower feed preview.
3. Handpick a cover from the actual reel and check its full 9:16 view and the centre crop in the profile grid. Place the title in the central safe area. Build a 4:5 carousel of original images or video clips in story order. Do not put third-party reference photos in public resources unless their use is licensed.
4. Write separate captions for the film, tutorial, and carousel. The film caption tells the story and credits its music. The tutorial explains the method and honest results. The carousel identifies the images and links to the exact prompt pack. Check CTA promises: a comment-to-DM offer needs a working fulfilment path; this channel currently replies manually.
5. Save manifest JSON files next to the media, then run `--check` for each. `--stage` can test the Instagram composer through the ready-to-share screen without posting.
6. Publish the film, tutorial, then carousel. The scripts explicitly set Reel crop to 9:16 and carousel crop to 4:5, set the handpicked cover, caption, and requested AI label, and record the final URL. Do not retry a run that reached `share_clicked` until you have checked the live profile for a duplicate.
7. Open each public URL. Review the Reel image and sound in Instagram, the cover on the profile, the caption and AI label, and the first and last carousel slides. Post any planned comment and verify it after a refresh. Record URLs and any remaining manual actions.
8. Push the public prompt pack to this repository. Keep local references, licensed source media, profile data, and run screenshots out of GitHub.

## Editorial decisions that stay manual

The scripts can select and upload a supplied cover; they cannot choose the strongest frame or validate a story claim. A person or an agent using visual review should choose the cover, verify the picture/sound and caption, check music rights/credit, review the carousel order, and inspect the finished Instagram post. The uploader does not create or automate comment-to-DM flows.

The script may need UI repair after Instagram changes its composer. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for the takeover and repair sequence.
