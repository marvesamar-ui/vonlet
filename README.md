# Vonlet Security — Company Archive & Capabilities

A responsive, visual-first corporate website built with semantic HTML5, modern CSS and vanilla ES6 JavaScript. There are no runtime frameworks or external CDNs.

## Run locally

Open `index.html` directly, or serve the folder so fonts, images and dialogs behave consistently:

```bash
python3 -m http.server 8080 --bind 0.0.0.0
```

Then visit `http://localhost:8080`.

## Deliverables

- `index.html` — the landing page: inline SVG icon sprite, hero, fourteen selected archive frames, fleet, services (including the eight-sector strip), cash-in-transit feature, company profile, estimator and dispatch form.
- `archive.html` — the 42-photograph archive, one frame per scene, with collection filters and the shared lightbox.
- `services.html` — all twenty-three service lines in full, with jump links and per-service request buttons; each published line carries a source link back to the page it came from, and each client-supplied line says so instead.
- `styles.css` — design tokens, self-hosted fonts, grid/flex layouts, HUD styling, animations and responsive breakpoints.
- `main.js` — modular navigation, focus-trapped dialogs, archive filters, lightbox, counters, live estimator, form validation and email handoff.
- `assets/images/thumbs/` — 640px WebP derivatives used in the archive grid (42 files).
- `assets/images/full/` — 1600px WebP derivatives used in the lightbox, hero and service blocks (42 files).
- `assets/logo.jpeg` — the supplied master logo lockup (shield, wordmark and `Zimbabwe` tag).
- `assets/logo-mark.png` — the shield badge cropped from the master, used in the header and footer; also the source for the browser icons.
- `assets/favicon.png`, `assets/apple-touch-icon.png` — icons generated from `assets/logo.jpeg`.
- `assets/fonts/` — locally hosted Barlow files with their licences.
- `tools/process-images.sh` — regenerates both WebP sizes from the original JPG archive.
- `tools/process-wa-frames.sh` — the second pipeline, for the WhatsApp site frames the client drops into `assets/`: filters each frame (haze/levels, shadow lift, gentle despeckle, unsharp) and writes the same two WebP sizes under `wa-*` names.
- `tools/build_gallery.py` — the photo catalogue (collection, title, alt text per image) and the generator that writes the featured grid into `index.html` and the full grid into `archive.html`.
- `tools/build_services.py` — the service catalogue (slug, group, copy, points, image, dispatch mapping, source URL) and the generator that writes `services.html`.

## Photo archive

- The photographs come from the client's Google Drive folder **security** (152 original `IMG_####.JPG` captures), plus seven recent site frames the client sent over WhatsApp, kept in `assets/` under their original `WhatsApp Image …jpeg` names. Every frame was reviewed and catalogued individually; captions and alt text describe what is visible in the photograph, not a generic template.
- Originals are converted to two WebP sizes and committed under `assets/images/`. The source JPGs are not committed; `google_drive/` is ignored as a scratch download directory.
- The archive is grouped into eleven collections: leadership (2), tactical & equipment (4), operations room (4), people & teams (6), field duty (3), site deployments (7), electronic security (4), K-9 units (2), reception & office (3), fleet & logistics (3) and strategy & training (4).
- The two frames in **leadership** show the company's chief executive officer — the woman in the pink blouse behind the desk — and are captioned by role only, not by name.
- The landing page carries a curated set of fourteen (`FEATURED` in `tools/build_gallery.py`), including two of the site-deployment frames; the whole set is only on `archive.html`.
- Photographs are shown in a curated order: one cover frame per collection, then interleaved so similar frames are not adjacent. Filtering re-groups by collection.
- Captions deliberately withhold individual officers' and clients' names. Do not add names to the archive without written consent.
- **The archive is de-duplicated.** The 152 captures were shot as bursts: the same two-man baton stance from eight angles, one CEO desk sitting in eight frames, one reception counter five times over. Each burst was reduced to its strongest frame (widest composition, sharpest, most representative), keeping one picture per distinct person, place and action — 35 frames in total. When adding photographs, apply the same rule: if two frames differ only by a step to the left, keep one. The `dHash` pass in the notes below groups candidates, but the keep/drop decision is a visual one.
- **The WhatsApp frames are the exception to that rule** — at the client's request all seven are kept, including the two quad-bike and two armed-post angles of the same site. WhatsApp had already shrunk them to 1280px, so they are *not* 4K masters and are never enlarged: `tools/process-wa-frames.sh` improves what is there (levels, haze, a shadow lift, gentle despeckle, unsharp) and writes `wa-*` WebPs at the same two sizes as the Drive set. One frame is cropped 130px on the left, which removes the thumb that intruded into the corner.

## Content & provenance

- Company facts, mission, vision, core values, services, recruitment steps, hotline, email and head-office address were taken from the live site **https://vonletsecurity.co.zw/** and its pages (`/about-us/`, `/services/`, the individual `/service/...` pages and the home page).
- All twenty-three service lines are described in full on `services.html`. Fifteen are sourced from the fourteen `/service/...` pages plus the cash-in-transit block on the home page, and each of those keeps a **Source page** link so the copy can be checked against the original. The other eight — bank & ATM, warehouse, retail, farms & mines, residential, functions, private escorts, private investigations — were given to us by the company for this site and are **not yet published on vonletsecurity.co.zw**; their blocks carry a client-supplied label instead of a source link, so nothing on the page implies a provenance the external site does not have. Nothing about a service line lives only on the external site now.
- Two source texts were corrected rather than copied blindly: the guard-training page lists "First Drill" where it means fire drill, and the firearm-handling page is written for a US licensing regime ("vary from state to state"), which is stated here as requirements differing between jurisdictions.
- The four figures in "Built on record" are published company facts: founded 2010, 24/7/365 technical support, two countries, and fifteen *published* service lines (fourteen published services plus cash-in-transit). The figure is labelled "Published service lines" so it stays true while the catalogue on this site runs to twenty-three.
- All 35 archived photographs are authentic company material, culled from the 152-capture set for near-duplicates; none were retouched.
- The four cash-in-transit images in `assets/images/cit/` are the one exception: AI-generated concept illustrations showing the route, a crew check, the loading bay and the counter handover. They are generated against the real brand kit — `assets/logo-mark.png` for the shield, `IMG_9336` for the fleet livery (white panel van, yellow windscreen band, blue VONLET SECURITY door lettering) and `IMG_9302`/`IMG_9299` for the uniform (light-blue shirt, navy tactical vest, navy cap, reflective overalls for drivers) — so the vehicle, livery, clothing and dry-season light stay consistent across all four. They sit in their own `#cash-in-transit` band and every one is labelled `ILLUSTRATIVE — AI-GENERATED CONCEPT IMAGERY, NOT COMPANY PHOTOGRAPHS`. Never move them into the archive grid or present them as company photographs.
- If these are ever regenerated, reuse the shipped `assets/images/cit/v2-*.jpg` frames as image references (plus `assets/logo-mark.png`) and keep one vehicle model, one uniform and one season across the set; the first attempt drifted into different vans, different shirts and a warped badge on each frame.

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

- The dispatch form validates locally, then opens **WhatsApp** (`https://wa.me/263772856852`) in a new tab with the whole request — name, email, phone, service, operational brief and consent — written into the message body. Nothing is sent by the site itself and nothing is stored; the visitor presses send in WhatsApp.
- The WhatsApp number lives in one place: `WHATSAPP_NUMBER` at the top of `initContact()` in `main.js`. Change it there and every handoff follows. Long briefs are trimmed to `WHATSAPP_TEXT_LIMIT` (1500 characters) inside the URL so the message survives practical URL limits; the **Copy request** button always carries the full, untrimmed text.
- If a browser blocks the new tab, the ready panel keeps an **Open WhatsApp** button with the same prefilled link, plus an email fallback to `info@vonletsecurity.co.zw`.
- To collect submissions server-side later, add an endpoint alongside the WhatsApp handoff; add spam protection, rate limiting and server-side validation at that point.
- Licensing numbers were not published on the reference site, so the compliance dialog directs procurement teams to verify current documents with Vonlet instead of inventing credentials.
- Set the deployment domain in `canonical` and `og:url`, and make `og:image` an absolute URL, when the site goes live.
- Fonts are self-hosted under the SIL Open Font License; license files are included in `assets/fonts/`.

## Updating the archive

1. Drop new JPGs into a source folder. Frames that arrive as `WhatsApp Image …jpeg` in `assets/` go through `bash tools/process-wa-frames.sh` instead: it filters them and writes `wa-*` WebPs at both sizes, never enlarging them.
2. Run `bash tools/process-images.sh /path/to/folder` to create both WebP sizes from the Drive JPGs.
3. Add each new frame to `PHOTOS` in `tools/build_gallery.py` (image name, collection, title, alt text), and give a genuinely new scene its own collection in `COLLECTIONS`, `COVER` and `ORDER` so the filter tabs pick it up.
4. Run `python3 tools/build_gallery.py`. The script verifies that every thumbnail is catalogued and every catalogue entry has a file, then regenerates the featured grid in `index.html` and the filter tabs plus full grid in `archive.html`. Counts written by hand outside those markers — the "Fourteen frames" heading on the landing page, the archive hero stats and both page titles — are edited in the pages themselves.

## Updating a service line

1. Edit the matching entry in `SERVICES` in `tools/build_services.py` (name, group, summary, paragraphs, points, image, source URL, dispatch value). Leave `source=None` for a line the company has not published yet — the block prints the client-supplied label instead of a link.
2. Run `python3 tools/build_services.py`. It rebuilds `services.html` from the `index.html` shell, so the header, footer and dialogs stay identical across pages; block counters, the group legend and the page totals are all derived from the list.
3. Request buttons carry `index.html?service=<value>&label=<name>#dispatch`; `main.js` reads that query, preselects the dispatch form and focuses it. A new dispatch value needs a matching `<option>` in the `#contact-service` select in `index.html`, and a line that should show on the landing page is added there twice: the `service-sectors-grid` strip and the `service-index-grid` list.
4. If the company later publishes the page, set its URL as `source` and rebuild — the client-supplied label disappears and the source link returns.

## Accessibility & behavior

- Keyboard-operable navigation, filters, dialogs and forms.
- Native `<dialog>` overlays with explicit focus trapping, Escape/backdrop closing and focus restoration.
- Reduced-motion support, visible focus states, live regions and form error associations.
- Responsive layouts for phones, tablets and large screens; archive images are lazy-loaded with reserved dimensions to avoid layout shift.
