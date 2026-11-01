#!/usr/bin/env bash
# Vonlet Security — image pipeline.
# Source: Google Drive folder "security" (152 original JPG captures).
# Produces two WebP derivatives per photo:
#   assets/images/thumbs/<name>.webp  640px wide  — gallery grid
#   assets/images/full/<name>.webp   1600px wide  — lightbox
set -euo pipefail

SRC="${1:-/tmp/raw}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
THUMBS="$ROOT/assets/images/thumbs"
FULL="$ROOT/assets/images/full"
mkdir -p "$THUMBS" "$FULL"

export MAGICK_TMPDIR=/tmp

count=0
for f in "$SRC"/*.JPG "$SRC"/*.jpg; do
  [ -e "$f" ] || continue
  name="$(basename "${f%.*}")"
  if [ ! -f "$THUMBS/$name.webp" ]; then
    convert "$f" -auto-orient -resize 640x640\> -strip -quality 72 "$THUMBS/$name.webp"
  fi
  if [ ! -f "$FULL/$name.webp" ]; then
    convert "$f" -auto-orient -resize 1600x1600\> -strip -quality 78 "$FULL/$name.webp"
  fi
  count=$((count + 1))
done
echo "processed $count source photos"
du -sh "$THUMBS" "$FULL"
