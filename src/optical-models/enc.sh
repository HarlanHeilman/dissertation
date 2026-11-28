#!/bin/bash
# $1 = name (out/$1.mkv) ; $2 = output basename
set -e
cd /home/claude/omgif/out
ffmpeg -y -loglevel error -i $1.mkv -vf "split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a" -loop 0 $2.gif
ffmpeg -y -loglevel error -i $1.mkv -c:v libx264 -pix_fmt yuv420p -preset veryfast -crf 18 -movflags +faststart $2.mp4
