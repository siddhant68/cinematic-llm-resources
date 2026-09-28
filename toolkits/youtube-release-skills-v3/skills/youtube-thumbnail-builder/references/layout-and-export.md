# Layout and export

## Master and upload derivative

Keep two files:

- `*-master.png`: lossless working master, normally 3840x2160.
- `*-upload.jpg` or `*-upload.png`: final 16:9 file prepared for upload.

The YouTube Data API thumbnail endpoint currently imposes a 2 MB media-upload limit, even though YouTube Studio on desktop may accept larger files. Build an API-safe derivative rather than reducing the quality of the working master.

## Safe composition

- Keep essential text and faces away from the extreme edges.
- Avoid placing critical details in the lower-right duration-badge region.
- Prefer one clear diagonal or left/right tension rather than many competing alignments.
- Use a background treatment that separates the subject without looking artificially pasted.
- Check the thumbnail on light and dark surrounding UI.

## Cutouts

- Inspect hair, glasses, fingers, microphone edges, and chair overlap.
- Match edge softness to the background depth of field.
- Use restrained contact shadow or light wrap only when it improves integration.
- Do not use heavy glow to conceal a poor matte.

## Screenshots

- Crop to the one feature that proves the point.
- Remove private information.
- Keep labels large enough to read at 320x180.
- Use a callout or highlight rather than showing the entire application window.

## Compression

Prefer high-quality JPEG for photographic composites and PNG for flat graphics where the API size limit permits it. Decrease JPEG quality gradually; do not repeatedly re-encode the same derivative. Always compress from the lossless master.
