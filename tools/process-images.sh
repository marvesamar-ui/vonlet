#!/usr/bin/env bash
# Vonlet Security — image pipeline.
# Source: Google Drive folder "security" (152 original JPG captures).
# The archive is de-duplicated: only the 35 catalogued frames in
# tools/build_gallery.py survive, so the prune step at the end removes any
# derivative that the catalogue does not reference.
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
# Drop derivatives that are not in the catalogue (build_gallery.py requires the
# on-disk thumb set to match PHOTOS exactly).
mapfile -t KEEP < <(sed -n 's/^    ("\(IMG_[0-9]\{4\}\)",.*/\1/p' "$ROOT/tools/build_gallery.py")
for dir in "$THUMBS" "$FULL"; do
  for f in "$dir"/IMG_*.webp; do
    [ -e "$f" ] || continue
    name="$(basename "${f%.webp}")"
    printf '%s\n' "${KEEP[@]}" | grep -qx "$name" || rm -f "$f"
  done
done

echo "processed $count source photos; kept ${#KEEP[@]} catalogued frames"
du -sh "$THUMBS" "$FULL"
