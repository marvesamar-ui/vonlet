# VONLET — SIGNAGE & RECEPTION KIT

Fifteen boards, drawn to scale in millimetres. Every file is a print-resolution
PNG with a bleed, so a fabricator, printer or sign shop can take it straight
into production. Sizes are finished sizes; the bleed is extra on each edge.

Three things live here:

| Folder | What it is |
| --- | --- |
| `*.png` | The flat artwork. This is what a fabricator prints. |
| `plans/` | Technical elevations — dimensioned drawings with material, fixing and installation heights. |
| `insitu/` | Photorealistic renders showing each board on a real wall, in perspective, in daylight. |

Build all three:

```bash
python3 tools/build_signage.py           # flat artwork
python3 tools/build_signage_plans.py     # dimensioned elevations
python3 tools/build_signage_3d.py        # in-situ renders
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

## Specification

**Colour.** Navy `#030816`, signal red `#e61919`, safety yellow `#facc15`,
white `#ffffff`, slate `#94a3b8` / `#64748b` for secondary type.

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
