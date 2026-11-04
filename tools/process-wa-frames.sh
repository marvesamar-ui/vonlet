#!/usr/bin/env bash
# Vonlet Security — WhatsApp site-frame pipeline.
#
# Source: the client's recent on-site frames, dropped into assets/ under their
# original "WhatsApp Image <date> at <time>.jpeg" names. These are company
# photographs, but they arrive already shrunk by WhatsApp to 1280x960 /
# 960x1280, so they are NOT 4K masters: there is no extra detail to recover.
# The pipeline therefore "filters" them the other way round — it improves what
# is actually there rather than inflating the pixel count:
#
#   -level 4%,99%,1.18       clip the haze veil at both ends, lift the midtones
#                            so a dark navy uniform still reads against shade
#   -sigmoidal-contrast      contrast around the mid-grey, without crushing
#   -modulate 101,120        WhatsApp strips colour; put the saturation back
#   -enhance                 despeckle the JPEG artefacts around the badge/patch
#   -unsharp                 recover edge definition lost to the compression
#
# Then each frame is written at the two sizes the site uses — never enlarged
# past its own width:
#
#   assets/images/thumbs/<slug>.webp   <=640px, quality 72  — gallery grid
#   assets/images/full/<slug>.webp    <=1600px, quality 78  — lightbox + services
#
# One frame is cropped: a thumb intrudes into the bottom-left corner of the
# "two officers at the site desk" shot, so 130px comes off the left edge, which
# keeps both officers and drops the pillar.
#
# Every slug written here must also be catalogued in PHOTOS in
# tools/build_gallery.py — that script refuses to run if the catalogue and the
# files on disk disagree. Frames are given "wa-" names so the IMG_* prune step
# in tools/process-images.sh leaves them alone.
#
# Usage:  bash tools/process-wa-frames.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/assets"
THUMBS="$ROOT/assets/images/thumbs"
FULL="$ROOT/assets/images/full"
mkdir -p "$THUMBS" "$FULL"

export MAGICK_TMPDIR=/tmp

FILTER=(-auto-orient -level 4%,99%,1.18 -sigmoidal-contrast 2.2x44% -modulate 101,120 -enhance -unsharp 0x1+0.9+0.02 -colorspace sRGB -strip)

# slug | source filename | gravity | crop geometry ("" = no crop)
FRAMES=(
  "wa-01-foot-patrol|WhatsApp Image 2026-11-04 at 08.06.23.jpeg||"
  "wa-02-gatehouse-register|WhatsApp Image 2026-11-04 at 08.19.47.jpeg||"
  "wa-03-quad-driveway|WhatsApp Image 2026-11-04 at 08.19.48.jpeg||"
  "wa-04-quad-lawn|WhatsApp Image 2026-11-04 at 08.19.49.jpeg||"
  "wa-05-site-desk-pair|WhatsApp Image 2026-11-04 at 08.19.49 (1).jpeg|NorthWest|1150x960+130+0"
  "wa-06-armed-sentry|WhatsApp Image 2026-11-04 at 08.19.50.jpeg||"
  "wa-07-veranda-post|WhatsApp Image 2026-11-04 at 08.19.50 (1).jpeg||"
)

for entry in "${FRAMES[@]}"; do
  IFS='|' read -r slug file gravity crop <<<"$entry"
  [ -f "$SRC/$file" ] || { echo "missing source: $SRC/$file" >&2; exit 1; }
  CROP=()
  [ -n "$crop" ] && CROP=(-gravity "$gravity" -crop "$crop" +repage)
  convert "$SRC/$file" "${FILTER[@]}" "${CROP[@]}" -resize 640x640\> -quality 72 "$THUMBS/$slug.webp"
  convert "$SRC/$file" "${FILTER[@]}" "${CROP[@]}" -resize 1600x1600\> -quality 78 "$FULL/$slug.webp"
  printf '%-26s %s\n' "$slug" "$(identify -format '%wx%h' "$FULL/$slug.webp")"
done

echo "processed ${#FRAMES[@]} WhatsApp frames into $(ls "$THUMBS"/wa-*.webp | wc -l) thumbs + $(ls "$FULL"/wa-*.webp | wc -l) full frames"
du -sh "$THUMBS" "$FULL"
