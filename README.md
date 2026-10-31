# Vonlet Security — Operations Showcase

A responsive, visual-first corporate website built with semantic HTML5, modern CSS and vanilla ES6 JavaScript. There are no runtime frameworks or external CDNs.

## Run locally

Open `index.html` directly, or serve the folder so fonts, images and dialogs behave consistently:

```bash
python3 -m http.server 8080 --bind 0.0.0.0
```

Then visit `http://localhost:8080`.

## Deliverables

- `index.html` — semantic structure, inline SVG icon sprite, accessible labels, gallery cards, estimator and dispatch form.
- `styles.css` — design tokens, self-hosted fonts, grid/flex layouts, HUD styling, animations and responsive breakpoints.
- `main.js` — modular navigation, focus-trapped dialogs, gallery filters, lightbox, counters, live estimator, form validation and email handoff.
- `assets/` — optimized WebP imagery, SVG favicon and locally hosted Barlow font files with their licenses.

## Content & provenance

- Company facts, services, hotline, email and head-office address were referenced from the existing Vonlet Security website.
- `assets/vonlet-team.webp` is an authentic company-archive team photograph sourced from the existing site.
- The remaining operation and equipment images are AI-generated capability illustrations. They are labeled as illustrative in the gallery, lightbox and equipment notes; they are not presented as verified Vonlet missions.
- HUD labels and the operations reel are interface demonstrations, not a live telemetry feed.
- The metric values requested for the showcase are displayed as illustrative performance targets, not verified live statistics.
- Estimator rates are transparent demonstration rates in USD. Replace them with approved tariffs before commercial use.

## Production notes

- The dispatch form validates locally and prepares a `mailto:` handoff. It does **not** send or store data. Connect a server-side endpoint or form provider before expecting direct submissions; add spam protection, rate limiting and server-side validation at that point.
- Licensing numbers were not published on the reference site, so the compliance dialog directs procurement teams to verify current documents with Vonlet instead of inventing credentials.
- Replace illustrative imagery with approved operational photography when available, and update the provenance notes accordingly.
- Add the final deployment URL to canonical/Open Graph metadata when the site is deployed.
- Fonts are self-hosted under the SIL Open Font License; license files are included in `assets/fonts/`.

## Accessibility & behavior

- Keyboard-operable navigation, filters, dialogs and forms.
- Native `<dialog>` overlays with explicit focus trapping, Escape/backdrop closing and focus restoration.
- Reduced-motion support, visible focus states, live regions and form error associations.
- Responsive layouts for phones, tablets and large screens.
