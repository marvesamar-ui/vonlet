# VONLET — SIGNAGE & RECEPTION KIT

Fifteen boards, drawn to scale in millimetres. Every file is a print-resolution
PNG with a bleed, so a fabricator, printer or sign shop can take it straight
into production. Sizes are finished sizes; the bleed is extra on each edge.

This is the **modern edition**: paper fields, ink type, hairline structure and a
single mustard accent, matching the website's light theme. The sizes, bleeds,
materials, fixing heights and clear-space rules below are unchanged — only the
design language moved. `tools/build_signage.py` carries the tokens at the top of
the file.

Four things live here:

| Folder | What it is |
| --- | --- |
| `*.png` | The flat artwork. This is what a fabricator prints. |
| `plans/` | Technical elevations — dimensioned drawings with material, fixing and installation heights. |
| `insitu/` | Photorealistic renders showing each board on a real wall, in perspective, in daylight. |
| `premium/` | Ten illuminated designs, rendered lit at dusk — the specification for the signs that have to work after dark. |

Build all four:

```bash
python3 tools/build_signage.py             # flat artwork
python3 tools/build_signage_plans.py       # dimensioned elevations
python3 tools/build_signage_3d.py          # in-situ renders
python3 tools/build_signage_lighting.py    # illuminated set + contact sheet
```

## The set

### Gate & perimeter

| File | Finished size | Use | Notes |
| --- | --- | --- | --- |
| `01-gate-pylon.png` | 3600 × 2200 mm | Main gate pylon or hoarding | Read at 50 m: brand, one statement, one number. 40 mm bleed. |
| `02-gate-plate.png` | 2400 × 900 mm | Pedestrian gate or boom plate | Two columns: identity left, the instruction right. 30 mm bleed. |
| `03-warning-cctv.png` | 600 × 450 mm | At every camera zone entrance | 15 mm bleed. |
| `04-warning-dogs.png` | 600 × 450 mm | K-9 patrol areas | 15 mm bleed. |
| `05-warning-search.png` | 600 × 450 mm | Vehicle entrances | 15 mm bleed. |

The three warning boards share one typographic system, so they can be printed as
a set on 3 mm ACM, aluminium or rigid PVC.

### Reception

| File | Finished size | Use | Notes |
| --- | --- | --- | --- |
| `06-reception-wall.png` | 5200 × 2400 mm | Wall behind the reception desk | The hero piece. A 60/40 split: brand field left, team photograph and sign-in instructions right. 50 mm bleed. |
| `07-reception-desk.png` | 2400 × 1100 mm | Desk front fascia | Sits below the counter line, so all type is above waist height. 30 mm bleed. |
| `08-reception-after-hours.png` | 1200 × 800 mm | Reception door, after hours | Redirects arrivals to the gate and gives the control-room number. 20 mm bleed. |
| `14-wayfinding.png` | 900 × 300 mm | Floor or wall directional | Floor graphics need an anti-slip laminate. 15 mm bleed. |

### Identity, fleet & people

| File | Finished size | Use | Notes |
| --- | --- | --- | --- |
| `09-vehicle-livery.png` | 2200 × 900 mm | Door panel of the response fleet | Reverse-printed on white vinyl for a white vehicle. 25 mm bleed. |
| `10-notice-board.png` | 800 × 1100 mm | Site entrance or staff area | Five numbered house rules. 20 mm bleed. |
| `11-hi-vis-vest.png` | 560 × 640 mm | Back panel of a hi-vis vest | Screen-printed; keep to two spot colours if the printer prefers it. 10 mm bleed. |
| `12-company-plaque.png` | 600 × 400 mm | Boardroom, entrance, reception | Brushed-metal or acrylic plaque. 12 mm bleed. |
| `13-event-backdrop.png` | 3000 × 750 mm | Pop-up or step-and-repeat backdrop | 30 mm bleed. |
| `15-a-frame.png` | 700 × 1000 mm | Pavement or open-day A-frame | Needs a double-sided print; mirror the file for the reverse. 15 mm bleed. |

## Plans — `signage/plans/`

A3 landscape drawing sheets, each a dimensioned elevation with a title block,
scale bar, numbered callouts and, on the warning-board sheet, a mounting section.

| File | Drawing |
| --- | --- |
| `01-gate-pylon-plan.png` | The 3.6 × 2.2 m pylon: face layout, plinth, frame, LED flood positions, 3.6 m and 2.2 m dimensions |
| `02-reception-wall-plan.png` | The 5.2 × 2.4 m wall graphic: layout, centre line, mounting height, photo-area resolution |
| `03-warning-boards-plan.png` | The three 600 × 450 mm boards side by side, plus a section showing the 25 mm stand-offs |

These carry the information a shopfitter needs that artwork cannot express:
panel thickness, stand-off length, anchor type, plinth size, centre-line heights.

## In-situ renders — `signage/insitu/`

Nine renders showing the boards where they will actually hang. These are the
images to put in front of a client who asks "but what will it look like?".

| File | Scene | Board | Treatment |
| --- | --- | --- | --- |
| `01-gate-pylon.jpg` | Free-standing monolith at a driveway | 3.6 × 2.2 m pylon | 9 mm ACM on a steel frame, 9 mm edge |
| `02-gate-pillar-entrance.jpg` | Concrete gate pillar | 1600 × 2400 mm portrait | Panel fixed to the pillar face, 12 mm edge |
| `03-reception-wall.jpg` | Empty lobby wall, raking daylight | 5.2 × 2.4 m wall graphic | Vinyl on foamex, flush to the wall |
| `04-reception-desk.jpg` | Curved reception desk | 2.4 × 1.1 m fascia | Panel on the desk front |
| `05-warning-cctv.jpg` | Painted exterior wall | 600 × 450 mm warning board | 3 mm ACM on stand-offs |
| `06-notice-board.jpg` | Same wall | 800 × 1100 mm notice board | 3 mm ACM on stand-offs |
| `07-company-plaque.jpg` | Same wall | 600 × 400 mm plaque | Brushed plaque, 12 mm stand-off |
| `08-wayfinding.jpg` | Same wall, low mount | 900 × 300 mm directional | 3 mm ACM |
| `09-a-frame.jpg` | Paving in front of the building | 700 × 1000 mm A-frame | Double-sided, standing on the paving |

### How the renders are made

There is no 3D package here, so `tools/insitu.py` does the three things that
actually make a mock-up read as real:

- **Perspective.** Each board is mapped onto a measured four-point quad with a
  true homography, so it sits in the scene's vanishing geometry rather than
  being pasted on flat. The quads were measured off each scene's silhouette —
  columns sampled for the top edge, rows for the base — then inset so the board
  sits within the wall instead of over its edges.
- **Light.** A blurred luminance field is sampled from the patch of wall behind
  the board and the board's colour is modulated by it. A sign on a wall in
  raking light is brighter on the lit side; this is the single biggest cue that
  lifts a composite out of "sticker on a photo".
- **Depth.** Boards are not paper. `place()` extrudes the quad along a direction
  and fills the visible side faces, so a 3 mm ACM panel, a 12 mm stand-off
  plaque and a 110 mm blade each read with their own thickness.

The scenes in `assets/signage-scenes/` are generated plates: an empty lobby wall,
a bare gate pillar, a blank monolith, an empty desk, a blank exterior wall and an
empty sign bracket. They are deliberately empty — no lettering anywhere — so
nothing in them competes with, or contradicts, the board that gets composited on
top. The company's own photography could not be used for this: those frames
already contain the existing wall boards, and a rendered sign would have had to
be pasted over real signage.

## Premium illuminated set — `signage/premium/`

Ten designs for the signs that have to work after dark: the gate, the pylon, the
entrance, the lobby. Every one is shown lit, at dusk, on the surface it is
actually fixed to — because an illuminated sign is a lighting brief as much as
an artwork, and a flat file cannot show a fabricator where the light comes from.

| File | Sign | Size | Lighting | Where |
| --- | --- | --- | --- | --- |
| `01-channel-letters.png` | Fabricated channel letters | 2400 × 1200 mm | Face-lit acrylic letters on a halo-lit back tray | Lobby wall |
| `02-acrylic-blade.png` | Framed acrylic blade | 1640 × 800 mm | Edge-lit acrylic in a black frame, bracket-mounted | Blade wall |
| `03-halo-wall.png` | LED halo wall sign | 3800 × 1700 mm | Reverse-lit mark on a stand-off tray, 60 mm off the stone | Night wall |
| `04-lightbox-totem.png` | Backlit fabric lightbox | 1200 × 2240 mm | Even panel illumination, dye-sublimation textile face | Gate approach |
| `05-metal-plate.png` | Brushed stainless plate | 3000 × 1000 mm | Wall-washed by two surface downlights | Reception desk |
| `06-neon-gate-totem.png` | LED neon-line totem | 900 × 1740 mm | Halo-lit lettering on a dark monolith | Gate pillar |
| `07-illuminated-pylon.png` | Downlit pylon | 3000 × 2080 mm | Two spot heads on a top arm, raking the face | Site boundary |
| `08-window-vinyl.png` | Frosted manifest film | 2600 × 1670 mm | Interior backlight through frosted vinyl | Glass frontage |
| `09-canopy-letters.png` | Fascia letters | 4500 × 300 mm | Soffit-lit halo letters on a deep fascia | Entrance canopy |
| `10-lit-a-frame.png` | Edge-lit A-frame | 700 × 1000 mm | Internally illuminated double-sided leaf | On the paving |

`contact-sheet.png` is all ten on one page, captioned.

### How the renders are made

`tools/build_signage_lighting.py` draws the artwork in millimetres, then
composites it into one of the blank scene plates with `tools/lighting.py` as the
lighting rig. Two rules, both learned the hard way:

- **The artwork's aspect matches its quad's.** Every board is built at the size
  of the face it is mounted on, so no letter is ever squashed into a quad. The
  quads were measured off each plate with a grid overlay, not estimated.
- **Light is added, never painted.** Halos, rims, spill and wall-washes are
  screened onto the scene, so they brighten what is behind them instead of
  covering it with a grey rectangle.

The rig is a set of small, physical pieces: `bloom` for the halo off a lit face,
`pool`/`wash` for light landing on a surface, `backlit` for a panel that glows
through its own print, and `*_layer` variants of the light functions so a cone
thrown by a spot can be clipped to the sign it lands on rather than also lighting
the sky. `dusk()` grades a daylight plate to night; `brushed_metal`,
`acrylic_edge_glow` and `scuff` supply material. Light is never a flat fill: the
halo falls off as `a / (1 + a)` so a bright face does not leave a hard-edged
grey plateau behind it.

```bash
python3 tools/build_signage_lighting.py                    # all ten + contact sheet
python3 tools/build_signage_lighting.py 04-lightbox-totem  # just one
```

Copy lives in the `sig_*` function for each design; the quads, lighting values
and spill positions live in the matching `render_*` function directly below it.

The ten scene plates in `assets/signage-scenes/` are the same deliberately-empty
generated plates used by the in-situ set, adding a night wall, a pylon at dusk,
an exterior wall with paving, a canopy, a glass frontage and a gate pillar.

## Specification

**Colour.** Paper `#ffffff` and stone `#f1f3f5` for fields, ink `#0b0f16` for
type (19:1 on paper), slate `#5f6a7a` for technical lines (5.5:1), brand mustard
`#facc15` and signal red `#c81a1a`.

Mustard and red are **graphics, never type on paper**: `#facc15` sits at 1.9:1 on
white and would be unreadable at any mounting height. Where the accent has to be
set as type it becomes `#985c06` (5.4:1), the same mustard the website uses.
Signal red is held back for the work it does: the warning boards and the
after-hours redirect. The hi-vis vest is the one board that stays on yellow,
because the garment is yellow; its type is navy at 12.1:1.

**Design system.** The kit is drawn as modern architectural signage rather than
as safety signage. Four rules carry it:

- **The field is the material.** Boards are white, because that is what a
  fabricator prints on. Colour arrives as one structural element — a spine down
  an edge or a plinth along the foot — not as bands top and bottom.
- **Structure is hairline.** Separators are 2–3 mm rules at `#cfd6dd`, and the
  type sits on them rather than in boxes. Nothing is outlined that does not need
  to be.
- **One voice per level.** Condensed ink caps for the statement, Barlow regular
  ragged-right for body copy, letterspaced mono-style captions at 0.18–0.24 em
  for anything technical. Body copy is never justified: stretched word gaps read
  as damage at three metres.
- **Air is part of the design.** Margins run at roughly 5–6% of the long edge and
  the largest element on each board is the one thing a person needs at that
  distance — the statement on the pylon, the number on the after-hours board.

| Material | Boards | Finish |
| --- | --- | --- |
| 3 mm ACM / aluminium composite | 01, 02, 03, 04, 05, 12 | Matte laminate, UV-stable ink |
| Rigid PVC or foamex | 08, 10, 14 | Matte laminate |
| Vinyl on substrate | 06 | Matte laminate; matte vinyl to kill reflections in a lit lobby |
| Cast vinyl | 09 | Reverse-print if applying to glass; otherwise standard |
| Woven polyester | 13 | Tension-fabric or pop-up, dye-sublimation |
| Screen print | 11 | Two spot colours on hi-vis polyester |
| PVC or aluminium | 07, 15 | Matte laminate |

**Installation.** Nothing hangs below 1200 mm or above 1800 mm where it must be
read at close range. Board 06 is centred on the desk, 1500 mm to its centre.
Board 08 goes at eye height beside the after-hours door. Floor graphics (14)
need an anti-slip overlaminate rated R10 or better.

**Clear space.** Keep one shield-width of clear wall around any board. Nothing
should be mounted within 300 mm of the edge of 06 — the composition already
holds its own margins.

## Fonts

Barlow Condensed (Bold, SemiBold) for display, Barlow (Regular, SemiBold) for
body. Both are already in `assets/fonts/` with their licences, so a fabricator
can set replacement copy in the identical face. Do not substitute a condensed
grotesque: the wide apertures and flat terminals are what make the numeral
stack read at distance.

## Rebuilding or editing

```bash
python3 tools/build_signage.py                      # all fifteen boards
python3 tools/build_signage.py --only 06-reception-wall
```

Copy lives at the top of each board function in `tools/build_signage.py`. The
phone number, email, address and strapline are constants at the top of the file
— change them once and every board follows.

Each board sets its own render resolution, because a 5.2 m wall does not need
300 dpi. If a printer asks for a specific resolution, change the third value in
the `SIGNS` table at the bottom of the file.

## What is real in these files

The team photograph on board 06 is the company's own frame
(`wa-09-suit-team-entrance`), taken from the unwatermarked master at
`assets/images/master/full/`. No generated imagery appears on any signage board:
every board is type, colour and the real shield.

Contact details, address and the strapline are the published company details
used across the site and the magazine.
