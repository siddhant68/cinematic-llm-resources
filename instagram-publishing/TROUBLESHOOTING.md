# When the Instagram flow changes

The scripts use visible Edge UI labels. Instagram can rename buttons, add notices, or change the post composer. A failure prints `TAKEOVER_REQUIRED`, saves a screenshot and page text in the local `.runs/<run-id>/` folder, and keeps its Edge window open when run from a live terminal.

1. Read the failure step and `state.json`. Inspect `failure.png` and the open Edge window with computer use.
2. If state is `share_clicked`, check the profile for the new post **before** clicking Share again. An Instagram success message or navigation may have failed after the post was already accepted. Record the published URL if present. Do not reset the state file to bypass duplicate protection.
3. If the post is still in the composer, finish the upload in the open Edge window: choose the correct file, explicit crop, cover, exact caption, AI label, and Share. Verify Instagram's shared message, then open the public URL.
4. Repair the changed selector or logic in the local script. Add a focused test if the failure was in local parsing/state logic. Run `npm test` and `--check`, and consider `--stage` to validate the UI before the next release. Copy the repaired script into this repository's `scripts/` folder and document the change.
5. Keep the evidence and final URL in the release record. Only then close the held script by pressing Enter in its terminal.

## Known cases

| Symptom | What to do |
| --- | --- |
| Reel appears square or top/bottom is cut in the Reel player | Select **Crop → Select Crop → 9:16** in the composer. Check `crop_9_16.png`. |
| Reel player is correct, but feed preview cuts the edges | Use the feed-safe packaging helper and a centre-safe cover; inspect both views. |
| Carousel is cropped | Use consistently sized 4:5 or 1:1 slides and explicitly select the matching crop in the composer. |
| `share_clicked` but no final URL | Inspect profile for a new Reel/post and check account status. Do not automatically retry. |
| Instagram says post could not be shared or shows an appeal screen | Stop the upload, preserve evidence, and resolve the account status. After access returns, check for a duplicate before any retry. |
| AI label switch count changes | Inspect the new UI manually, set the intended label, then update the script's targeting. Do not guess which switch to click. |
| Video looks small inside the Reel | Check the layout before the upload: a clip drawn as a card on a dark canvas looks small even in a full 1080x1920 file. Make the clip edge to edge in the edit, and upload the full-frame file rather than a feed-safe copy unless a 4:5 feed preview is the goal. |
| A published Reel needs a different video or cover | Instagram's web editor only changes the caption and AI label. Delete the post (check the caption text first, as `delete_posts` does) and upload again with a new manifest, or change the cover in the mobile app (Edit, then cover). Confirm with the account owner before deleting. |
| Own comment cannot be pinned in Edge | Post and verify the comment, record it as unpinned, and use the Instagram mobile app if pinning is needed. The tested Edge menu showed Delete and Cancel only. |
| Comment-to-DM CTA is used | This repository does not automate DMs. Fulfil the offer manually or connect and test a separate approved service before promising automation. |

Keep media review and cover selection in the release process. A script passing `--check` confirms file shape and caption length; it does not prove that a shot, music mix, title, or story claim is good.
