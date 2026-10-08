# Take the shine off (the ffmpeg grade used on this ad)

Raw generations look too clean. This chain scales the 480p take to 1080x1920, lowers contrast and colour a little, lifts the blacks and highlights, and adds a very faint hand-held shake. Compare before and after, and stop before it looks washed out.

```sh
ffmpeg -i take1_480p.mp4 -an \
 -vf "fps=30,scale=1112:1976:flags=lanczos,unsharp=5:5:0.55:5:5:0.0,\
eq=contrast=0.93:saturation=0.92:brightness=0.005,\
curves=all='0/0.025 0.25/0.265 0.6/0.615 0.9/0.915 1/0.985',\
crop=1080:1920:'(in_w-1080)/2+3.2*sin(t*8.3)+1.6*sin(t*19.7)':'(in_h-1920)/2+3.2*cos(t*7.3)+1.4*sin(t*17.9)',format=yuv420p" \
 -c:v libx264 -preset slow -crf 17 -r 30 ad_graded.mp4
```

- `scale=1112:1976` is 3% larger than the frame so the shake never shows an edge.
- If you can see the shake as an effect, it is too strong: lower the 3.2 and 1.6 values.
- The upload master was re-encoded afterwards at about 14 Mbps (`-crf 18 -maxrate 14M -bufsize 28M`, AAC 256k, `-movflags +faststart`).
