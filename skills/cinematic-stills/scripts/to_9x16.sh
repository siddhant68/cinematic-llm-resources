#!/bin/bash
# Centre-crop a ChatGPT 2:3 image (1024x1536) to 9:16 (864x1536) so the start frame matches the video aspect.
# usage: to_9x16.sh in.png out.png
ffmpeg -v error -y -i "$1" -vf "crop=trunc(ih*9/16/2)*2:ih:(iw-trunc(ih*9/16/2)*2)/2:0" "$2" && ffprobe -v error -show_entries stream=width,height -of csv=p=0 "$2"
