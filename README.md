# Vonlet Security — Company Archive & Capabilities

A responsive, visual-first corporate website built with semantic HTML5, modern CSS and vanilla ES6 JavaScript. There are no runtime frameworks or external CDNs.

## Run locally

Open `index.html` directly, or serve the folder so fonts, images and dialogs behave consistently:

```bash
python3 -m http.server 8080 --bind 0.0.0.0
```

Then visit `http://localhost:8080`.

## Deliverables

- `index.html` — the landing page: inline SVG icon sprite, hero, twelve selected archive frames, fleet, services, cash-in-transit feature, company profile, estimator and dispatch form.
- `archive.html` — the complete 152-photograph archive with collection filters and the shared lightbox.
- `styles.css` — design tokens, self-hosted fonts, grid/flex layouts, HUD styling, animations and responsive breakpoints.
- `main.js` — modular navigation, focus-trapped dialogs, archive filters, lightbox, counters, live estimator, form validation and email handoff.
- `assets/images/thumbs/` — 640px WebP derivatives used in the archive grid (152 files).
- `assets/images/full/` — 1600px WebP derivatives used in the lightbox and hero (152 files).
- `assets/logo.jpeg` — the supplied master logo lockup (shield, wordmark and `Zimbabwe` tag).
- `assets/logo-mark.png` — the shield badge cropped from the master, used in the header and footer; also the source for the browser icons.
- `assets/favicon.png`, `assets/apple-touch-icon.png` — icons generated from `assets/logo.jpeg`.
- `assets/fonts/` — locally hosted Barlow files with their licences.
- `tools/process-images.sh` — regenerates both WebP sizes from the original JPG archive.
- `tools/build_gallery.py` — the photo catalogue (collection, title, alt text per image) and the generator that writes the featured grid into `index.html` and the full grid into `archive.html`.

## Photo archive

- The photographs come from the client's Google Drive folder **security** (152 original `IMG_####.JPG` captures). Every frame was reviewed and catalogued individually; captions and alt text describe what is visible in the photograph, not a generic template.
- Originals are converted to two WebP sizes and committed under `assets/images/`. The source JPGs are not committed; `google_drive/` is ignored as a scratch download directory.
- The archive is grouped into ten collections: leadership (8), tactical & equipment (20), operations room (12), people & teams (44), field duty (16), electronic security (14), K-9 units (5), reception & office (12), fleet & logistics (6) and strategy & training (15).
- The eight frames in **leadership** show the company's chief executive officer — the woman in the pink blouse behind the desk — and are captioned by role only, not by name.
- The landing page carries a curated dozen (`FEATURED` in `tools/build_gallery.py`); the whole set is only on `archive.html`.
- Photographs are shown in a curated order: one cover frame per collection, then interleaved so similar frames are not adjacent. Filtering re-groups by collection.
- Captions deliberately withhold individual officers' and clients' names. Do not add names to the archive without written consent.

## Content & provenance

- Company facts, mission, vision, core values, services, recruitment steps, hotline, email and head-office address were taken from the live site **https://vonletsecurity.co.zw/** and its pages (`/about-us/`, `/services/`, the individual `/service/...` pages and the home page).
- The four figures in "Built on record" are published company facts: founded 2010, 24/7/365 technical support, two countries, and fifteen service lines (fourteen published services plus cash-in-transit).
- The 152 archive photographs are authentic company material.
- The four cash-in-transit images in `assets/images/cit/` are the one exception: they are AI-generated concept illustrations showing a convoy formation with escort, the vans on route, a loading bay and a counter handover. They were generated from `assets/logo-mark.png` plus the faces and uniforms in the archive, after the client asked for cash-in-transit imagery. They sit in their own `#cash-in-transit` band and every one is labelled `ILLUSTRATIVE — AI-GENERATED CONCEPT IMAGERY, NOT COMPANY PHOTOGRAPHS`. Never move them into the archive grid or present them as company photographs.

## Brand mark

- `assets/logo.jpeg` is the master lockup supplied for the project: VONLET shield (red banner, eagle, `SECURITY` and `SERVICES` arcs) beside the wordmark and the `Zimbabwe` tag, 2752×1536 on white.
- `assets/logo-mark.png` is the shield alone, cropped from the master at 512×512 with transparent-free white padding, used in the site header and footer where the wordmark is already typeset in HTML.
- To rebuild the mark and icons after replacing the master:
  `convert assets/logo.jpeg -crop 900x900+170+300 +repage -bordercolor white -border 70 -resize 512x512 -background white -gravity center -extent 512x512 PNG32:assets/logo-mark.png`
  `convert assets/logo-mark.png -resize 64x64 assets/favicon.png`
  `convert assets/logo-mark.png -resize 180x180 -background white -gravity center -extent 180x180 assets/apple-touch-icon.png`
- `assets/logo-lockup.jpg` is a trimmed light-weight copy of the master for social cards and print hand-off.

## Interface honesty

- HUD labels and the operations reel are interface demonstrations, not live telemetry. The reel is explicitly labelled `ILLUSTRATIVE`.
- The estimator uses demonstration rates in USD and says so in the interface. Replace them with approved tariffs before commercial use.

## Production notes

- The dispatch form validates locally and prepares a `mailto:` handoff. It does **not** send or store data. Connect a server-side endpoint or form provider before expecting direct submissions; add spam protection, rate limiting and server-side validation at that point.
- Licensing numbers were not published on the reference site, so the compliance dialog directs procurement teams to verify current documents with Vonlet instead of inventing credentials.
- Set the deployment domain in `canonical` and `og:url`, and make `og:image` an absolute URL, when the site goes live.
- Fonts are self-hosted under the SIL Open Font License; license files are included in `assets/fonts/`.

## Updating the archive

1. Drop new JPGs into a source folder.
2. Run `bash tools/process-images.sh /path/to/folder` to create both WebP sizes.
3. Add each new frame to `PHOTOS` in `tools/build_gallery.py` (image name, collection, title, alt text).
4. Run `python3 tools/build_gallery.py`. The script verifies that every thumbnail is catalogued and every catalogue entry has a file, then regenerates the featured grid in `index.html` and the filter tabs plus full grid in `archive.html`.

## Accessibility & behavior

- Keyboard-operable navigation, filters, dialogs and forms.
- Native `<dialog>` overlays with explicit focus trapping, Escape/backdrop closing and focus restoration.
- Reduced-motion support, visible focus states, live regions and form error associations.
- Responsive layouts for phones, tablets and large screens; archive images are lazy-loaded with reserved dimensions to avoid layout shift.
