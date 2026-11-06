#!/usr/bin/env bash
# Vonlet Security — WhatsApp site-frame pipeline.
#
# Source: the client's on-site frames, dropped into assets/ under their original
# "WhatsApp Image <date> at <time>.jpeg" names. These are company photographs,
# but they arrive already shrunk by WhatsApp — 960x1280, 744x992, 780x1040 — so
# they are NOT 4K masters: there is no extra detail to recover. The pipeline
# therefore "filters" them the other way round: it improves what is actually
# there rather than inflating the pixel count:
#
#   -level 1%,99.5%         recover the full range without clipping highlights
#   -modulate 100,108       WhatsApp strips colour; put a little saturation back
#   -enhance                despeckle the JPEG artefacts around the badge/patch
#   -unsharp 0x0.7+0.7      recover edge definition lost to the compression
#
# A portrait study sent in flat, late-afternoon shade (the three officers in the
# blue lounge suit) gets a gentler chain instead, because the first attempt
# crushed the navy suiting into black: see PORTRAITS below.
#
# Then each frame is written at the two sizes the site uses — never enlarged
# past its own width:
#
#   assets/images/thumbs/<slug>.webp   <=640px, quality 72  — cards, thumbnails
#   assets/images/full/<slug>.webp    <=1600px, quality 78  — lightbox + services
#
# Every slug written here must also be catalogued in PHOTOS in
# tools/build_gallery.py — that script refuses to run if the catalogue and the
# files on disk disagree.
#
# Usage:  bash tools/process-wa-frames.sh [slug ...]
#         with no arguments every frame below is rebuilt; name slugs to rebuild
#         just those (e.g. `bash tools/process-wa-frames.sh wa-13-rapid-response-vehicle`).
#
# Crops: several frames are portraits shot on a phone with the subject small in
# frame. For those a crop geometry is given (W x H + X + Y, top-left origin) so
# the card shows the officer at a usable size instead of a strip of pavement.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/assets"
THUMBS="$ROOT/assets/images/thumbs"
FULL="$ROOT/assets/images/full"
mkdir -p "$THUMBS" "$FULL"

export MAGICK_TMPDIR=/tmp

# Standard chain for the site frames.
FILTER=(-auto-orient -level 1%,99.5% -modulate 100,108 -enhance -unsharp 0x0.7+0.7+0.02 -colorspace sRGB -strip)
# Portrait studies in flat shade: keep the midtones, lift the suit a touch,
# leave the compression alone beyond a light despeckle.
PORTRAIT=(-auto-orient -level 0.5%,99.8%,1.02 -modulate 100,106 -enhance -unsharp 0x0.6+0.55+0.02 -colorspace sRGB -strip)

# A frame that has been retouched (see assets/retouched/) is used as the master
# instead of the WhatsApp original, and is NOT filtered again: the retouch was
# made from the already-filtered derivative, so the correction is baked in.
RETOUCHED="$ROOT/assets/retouched"

# slug | source filename | filter chain (std|portrait) | crop geometry ("" = none)
FRAMES=(
  # --- Batch 1: 4 November 2026, seven site frames ------------------------
  "wa-01-foot-patrol|WhatsApp Image 2026-11-04 at 08.06.23.jpeg|std|"
  "wa-02-gatehouse-register|WhatsApp Image 2026-11-04 at 08.19.47.jpeg|std|"
  "wa-03-quad-driveway|WhatsApp Image 2026-11-04 at 08.19.48.jpeg|std|"
  "wa-04-quad-lawn|WhatsApp Image 2026-11-04 at 08.19.49.jpeg|std|"
  "wa-05-site-desk-pair|WhatsApp Image 2026-11-04 at 08.19.49 (1).jpeg|std|1150x960+130+0"
  "wa-06-armed-sentry|WhatsApp Image 2026-11-04 at 08.19.50.jpeg|std|"
  "wa-07-veranda-post|WhatsApp Image 2026-11-04 at 08.19.50 (1).jpeg|std|"

  # --- Batch 2: 5 November 2026, ten deployed-officer and fleet frames -----
  # The branded Rapid Response Nissan NP300 parked outside the branch. Cropped
  # to the vehicle: the original is a tall phone frame with a third of pavement.
  "wa-08-rapid-response-vehicle|WhatsApp Image 2026-11-05 at 20.33.52.jpeg|std|744x558+0+215"
  # Three officers in the blue lounge suit and tie, under the turquoise strip.
  "wa-09-suit-team-entrance|WhatsApp Image 2026-11-05 at 20.34.22.jpeg|portrait|"
  # Banking-hall duty: one officer in the light-blue shirt, the other in the
  # lounge suit, both on the same ZB Financial Holdings corner.
  "wa-10-bank-duty-shirt|WhatsApp Image 2026-11-05 at 20.34.22 (1).jpeg|std|744x984+0+100"
  "wa-11-bank-duty-suit|WhatsApp Image 2026-11-05 at 20.34.23.jpeg|std|"
  # Depot discipline: reflective storm coats beside the core-values boards.
  "wa-12-depot-briefing|WhatsApp Image 2026-11-05 at 20.34.24 (1).jpeg|std|"
  "wa-13-fidelity-room-duty|WhatsApp Image 2026-11-05 at 20.34.25 (1).jpeg|portrait|"
  # Airport arrivals hall: close protection / meet-and-greet deployment.
  "wa-14-airport-arrivals|WhatsApp Image 2026-11-05 at 20.34.26.jpeg|std|"
  # Veranda relief post under a canopied walkway, cycle parked beside him.
  "wa-15-veranda-relief|WhatsApp Image 2026-11-05 at 20.34.25 (2).jpeg|portrait|"
  # Blue lounge suit, posted at the barred entrance of a client building.
  "wa-16-site-post-suit|WhatsApp Image 2026-11-05 at 20.34.25.jpeg|std|"
)

# Batch 2 arrived as ten frames, but 20.34.24 is the same officer on the same
# bank corner in the same pose as 20.34.23, a second apart — the archive keeps
# one frame per scene, so it is not processed. Add it back here and to PHOTOS in
# tools/build_gallery.py if the client wants both angles after all.

wanted=("$@")

for entry in "${FRAMES[@]}"; do
  IFS='|' read -r slug file chain crop <<<"$entry"
  if [ ${#wanted[@]} -gt 0 ]; then
    hit=0
    for want in "${wanted[@]}"; do [ "$want" = "$slug" ] && hit=1; done
    [ "$hit" -eq 1 ] || continue
  fi

  case "$chain" in
    portrait) CHAIN=("${PORTRAIT[@]}"); tag="filtered, portrait" ;;
    *) CHAIN=("${FILTER[@]}"); tag="filtered" ;;
  esac

  if [ -f "$RETOUCHED/$slug.png" ]; then
    master="$RETOUCHED/$slug.png"
    CHAIN=(-strip)
    tag="retouched"
  else
    master="$SRC/$file"
  fi
  [ -f "$master" ] || { echo "missing source: $master" >&2; exit 1; }

  CROP=()
  [ -n "$crop" ] && CROP=(-crop "$crop" +repage)

  convert "$master" "${CHAIN[@]}" "${CROP[@]}" -resize 640x640\> -quality 72 "$THUMBS/$slug.webp"
  convert "$master" "${CHAIN[@]}" "${CROP[@]}" -resize 1600x1600\> -quality 78 "$FULL/$slug.webp"
  printf '%-30s %-20s %s\n' "$slug" "($tag)" "$(identify -format '%wx%h' "$FULL/$slug.webp")"
done

echo "processed ${#FRAMES[@]} frame definitions into $(ls "$THUMBS"/wa-*.webp | wc -l) thumbs + $(ls "$FULL"/wa-*.webp | wc -l) full frames"
du -sh "$THUMBS" "$FULL"
