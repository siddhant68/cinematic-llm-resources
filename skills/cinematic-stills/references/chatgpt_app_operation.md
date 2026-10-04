# Driving ChatGPT image generation with computer use

Images are made in **ChatGPT image (GPT Image 2)** inside the **ChatGPT desktop app**, driven with computer use. It is included in a ChatGPT Plus plan, so the only cost is time. Redoing an image is the normal way to fix it; don't fix bad images later in video.

## Which ChatGPT
- **The desktop app.** On our Mac it lived inside the Codex/ChatGPT app (bundle `com.openai.codex`).
  - Use the top-left menu to switch to **ChatGPT**.
  - For every **New chat**, choose **Chat** mode, with effort **Medium**.
  - Use a paid (Plus) account. **Image generation in Chat mode still works when the Codex/Work 5-hour quota shows 0%**: Chat conversations are outside that meter (seen on 2026-09-29).
- **Not a Free-account chatgpt.com in a browser pane.** **Pasting images does not attach there** (the pane can't read the system clipboard). Text-only generation works there, but you can't attach references, so don't use it for this pipeline.
- Decline side prompts such as "Allow ChatGPT to use Google Drive?" (choose Not now).
- Don't change the account owner's settings or touch their existing chats.

## Access
- Load the computer-use tools in one go (ToolSearch `computer-use`), then `request_access` for the ChatGPT/Codex app.
- **Full-screen control** (`request_full_control`) is needed to paste images with cmd+v. Ask once per session.
- Keep the Mac awake for long runs: `caffeinate -dimsu &`.

## Attaching images and text
- **An image to the clipboard:**
  ```
  osascript -e 'set the clipboard to (read (POSIX file "/abs/path/image.png") as «class PNGf»)'
  ```
  Then cmd+v in the composer. For a JPG, convert it first: `sips -s format png in.jpg --out /tmp/in.png`.
- **Several images:** paste them **one at a time, in the order the prompt numbers them** ("the first attached photo…"). Check that the thumbnails in the composer are in that order before sending.
- **Text:** `LANG=en_US.UTF-8 pbcopy < prompt.txt`, then cmd+v. **Never type a multi-line prompt**: each Return sends the message early. Without `LANG=en_US.UTF-8`, characters like "·", "×" and curly quotes paste as garbage.
- Save every prompt you send as a file first (`<work>/prompts/<still>.txt`), so the log can point to the exact text.

## Generating
- **One fresh chat per image.** An old chat carries its earlier images into the new one.
- You can run **up to three chats in parallel** when their inputs don't depend on each other (for example, breakdowns of different pins).
- Generation takes about 1–2 minutes. **A chat stuck at "99%"**: switch to another chat and back, and it refreshes.
- **Trap:** clicking a generated image opens an **editor tab**, and anything typed there becomes an *edit request* on that image. To keep working, go back to the chat view first.
- **Expect redos.** A hard frame can take a dozen tries; ours typically took 1–3.

## Saving
- Use the image's **share or download icon → Download / "Download a copy"**, and type the file name.
  - The Save dialog opens on the last folder used (it once defaulted to an earlier project's folder). Check where it saves.
  - Then copy the file into `<work>/04_stills/` (or 01_cast, 05_grids, 06_boards) under the planned name.
- **Check the size:** ChatGPT returns 2:3 (1024×1536) or 9:16 (941×1672), and square for grids (1254×1254). Crop with `scripts/to_9x16.sh` for video start frames.
- **Breakdowns:** copy ChatGPT's text answer into `<work>/03_breakdowns/<slot>.md` (select and copy, then `pbpaste > file`).

## Words to keep out of ChatGPT
- No real names: no character, show, book, place, actor or real-person names. Write HER, HIM, THE CAPTAIN. This avoids lookalikes and refusals.
- Don't ask it to recreate a real identifiable person from a photo. It may refuse, and we don't do it anyway (see SKILL.md, the identity rule).
- Keep violence by its effect (a red stain, a thrown body), never gore. Keep children out of danger framing.
