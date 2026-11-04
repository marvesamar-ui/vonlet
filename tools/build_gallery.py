#!/usr/bin/env python3
"""Build the Vonlet operations gallery markup from the company photo archive.

Every photograph in the Google Drive folder "security" was reviewed and
catalogued - 152 captures in all. The archive then keeps only one frame per
distinct scene: near-identical bursts (the same pose from eight angles, the same
desk shot repeated) are culled, so every surviving frame shows something the
others do not. This script renders the static gallery markup (so the archive also
works without JavaScript) twice: a curated dozen between the GALLERY markers in
index.html, and the curated set between the ARCHIVE markers in archive.html.

Usage:  python3 tools/build_gallery.py
"""

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
ARCHIVE = ROOT / "archive.html"
THUMBS = ROOT / "assets/images/thumbs"
FULL = ROOT / "assets/images/full"

# --------------------------------------------------------------------------
# Collections: label, filter key, short brief shown in the lightbox, kit tags.
# --------------------------------------------------------------------------
COLLECTIONS = {
    "leadership": {
        "label": "Leadership",
        "brief": "Vonlet's chief executive officer at head office in Queensdale, Harare. The company is indigenous owned and, since 2010, has grown into a provider operating across Zimbabwe and part of Zambia.",
        "kit": "Executive office|Client liaison|Company strategy|24/7/365 oversight",
        "service": "integrated",
    },
    "operations": {
        "label": "Operations room",
        "brief": "Vonlet's operations desk coordinates duty rosters, site reports and client communication. Supervisors brief officers, review reports and keep the field teams informed from this control point at head office.",
        "kit": "Duty roster|Site reports|Two-way radio|Client liaison",
        "service": "monitoring",
    },
    "training": {
        "label": "Strategy & training",
        "brief": "Management and staff working through Vonlet's business strategy and planning programme - mission, vision, SWOT and PEST analysis, competitor review and growth planning - alongside practical site and guard reviews.",
        "kit": "Strategy workbook|SWOT analysis|PEST analysis|Guard training",
        "service": "training",
    },
    "people": {
        "label": "People & teams",
        "brief": "Vonlet personnel at head office and on site: marketing staff, reception and client service teams, uniform displays and officers photographed on duty. Every image is from the company's own archive.",
        "kit": "Company uniform|ID badge|Duty roster|Client briefing",
        "service": "integrated",
    },
    "office": {
        "label": "Reception & office",
        "brief": "The head office reception and client service division receives visitors, answers service enquiries and keeps the records behind a deployment - the customer-centric team described in Vonlet's mission.",
        "kit": "Reception desk|Client enquiries|Service records|Management reporting",
        "service": "integrated",
    },
    "tactical": {
        "label": "Tactical & equipment",
        "brief": "Higher-risk assignments call for protective equipment and rehearsed procedure: body armour, helmets, batons and control-and-restraint drills. Deployment is matched to the site risk assessment.",
        "kit": "Body armour|Ballistic helmet|Baton|Control & restraint drill",
        "service": "armed",
    },
    "field": {
        "label": "Field duty",
        "brief": "Static posts, gate and access control, site supervision and banking duty points - the visible, trained presence that Vonlet deploys to client premises.",
        "kit": "Guard post|Access register|Two-way radio|Site keys",
        "service": "unarmed",
    },
    "sites": {
        "label": "Site deployments",
        "brief": "Recent frames the company sent us directly from a live deployment: a gatehouse register, quad-bike patrols of a razor-wire perimeter, armed posts along a site office and a foot patrol on a cleared boundary line. They illustrate the sector work - warehouse, farms and mines, residential, functions - described on the services page.",
        "kit": "Quad bike|Occurrence book|Perimeter fence|Two-way radio",
        "service": "integrated",
    },
    "fleet": {
        "label": "Fleet & logistics",
        "brief": "Vonlet's branded vehicles support patrol supervision, personnel movement and equipment delivery, including covered trucks used for secure movement of goods.",
        "kit": "Branded vehicles|Covered truck|Driver|Vehicle logbook",
        "service": "cit",
    },
    "tech": {
        "label": "Electronic security",
        "brief": "Electronic security in the field: CCTV cameras and solar-powered camera masts installed on client perimeters and buildings, part of Vonlet's technical surveillance and rapid response offering.",
        "kit": "CCTV camera|Solar mast|Network recorder|Site survey",
        "service": "cctv",
    },
    "k9": {
        "label": "K-9 units",
        "brief": "Vonlet service dog teams: watch and attack dogs handled by uniformed handlers, adding deterrence and patrol support to a site's security plan.",
        "kit": "Service dog|Handler lead|Patrol route|Deterrence",
        "service": "k9",
    },
}

# --------------------------------------------------------------------------
# Photograph catalogue: image, collection, title, alt text.
# Titles and alt text describe what is actually visible in each frame.
# --------------------------------------------------------------------------
PHOTOS = [
    # --- Operations room --------------------------------------------------
    ("IMG_9249", "operations", "Operations officer on station", "Vonlet operations officer working at a desk beside a window"),
    ("IMG_9250", "operations", "Operations desk briefing", "Vonlet manager briefing two officers at the OPERATIONS desk"),
    ("IMG_9255", "operations", "Planning notes at the desk", "Vonlet officer working at a laptop in front of a strategy whiteboard"),
    ("IMG_9260", "operations", "Records and reporting", "Vonlet officer reviewing paperwork beside a laptop"),

    # --- Strategy & training ----------------------------------------------
    ("IMG_9261", "training", "Strategy workshop opens", "Vonlet staff seated around a conference table with laptops and water bottles"),
    ("IMG_9264", "training", "Workshop round table", "Vonlet staff smiling around the training table with laptops open"),
    ("IMG_9267", "training", "Laptop exercise", "Vonlet colleagues comparing notes on a laptop during training"),
    ("IMG_9274", "training", "Explaining the roadmap", "Facilitator and staff member at the whiteboard during a planning session"),

    # --- People & teams ---------------------------------------------------
    ("IMG_9280", "people", "Marketing team group photo", "Vonlet marketing team lined up in front of their branded car"),
    ("IMG_9291", "people", "Response team group photo", "Vonlet response team posed in front of a branded Hilux"),
    ("IMG_9363", "people", "Reception team group photo", "Vonlet reception team lined up in front of the company mission boards"),
    ("IMG_9367", "people", "Uniform display", "Vonlet officer with a mannequin wearing the tactical uniform"),
    ("IMG_9371", "people", "Operations officer portrait", "Vonlet officer in a blue company shirt seated at a desk"),
    ("IMG_9390", "people", "Canteen staff at work", "Vonlet catering staff preparing food in the staff kitchen"),

    # --- Reception & office -----------------------------------------------
    ("IMG_9343", "office", "Client handover at reception", "Vonlet receptionist handing documents across the counter"),
    ("IMG_9359", "office", "Desktop duty", "Vonlet officer typing at a desktop computer"),
    ("IMG_9389", "office", "Reception counter team", "Vonlet client service staff behind the curved reception counter"),

    # --- Leadership -------------------------------------------------------
    ("IMG_9346", "leadership", "Chief executive at her desk", "Vonlet chief executive in a pink blouse working at a laptop"),
    ("IMG_9347", "leadership", "Chief executive portrait", "Chief executive in a pink blouse, hand to her chin, at her desk"),

    # --- Tactical & equipment ---------------------------------------------
    ("IMG_9299", "tactical", "Body armour team", "Two Vonlet officers wearing body armour beside a branded car"),
    ("IMG_9302", "tactical", "Tactical response pair", "Vonlet officers in body armour and helmets with a baton"),
    ("IMG_9309", "tactical", "Supervisor and tactical team", "Manager with two officers in body armour beside the pickup"),
    ("IMG_9313", "tactical", "Control and restraint drill", "Vonlet officer demonstrating a control technique during training"),

    # --- Field duty -------------------------------------------------------
    ("IMG_9325", "field", "Access point duty", "Vonlet guard at a site entrance with a visitor"),
    ("IMG_9326", "field", "Team with mobile office", "Vonlet staff lined up in front of a mobile office truck"),
    ("IMG_9409", "field", "ATM duty officer", "Vonlet officer in a blue suit standing beside a bank ATM"),

    # --- Fleet & logistics ------------------------------------------------
    ("IMG_9334", "fleet", "Driver at the wheel", "Vonlet driver in the cab of a covered truck"),
    ("IMG_9336", "fleet", "Covered truck at the depot", "Branded Vonlet Security truck with a covered load"),
    ("IMG_9339", "fleet", "Loading bay check", "Officer at the open rear of a company truck"),

    # --- Electronic security ----------------------------------------------
    ("IMG_9287", "tech", "Camera alignment", "Technician aligning a camera mounted on a mast"),
    ("IMG_9396", "tech", "Perimeter mast camera", "Camera unit on a tall pole overlooking a walled property"),
    ("IMG_9398", "tech", "Solar-powered surveillance", "Dual-lens camera with a solar panel on a street-side pole"),
    ("IMG_9399", "tech", "Eaves-mounted camera", "CCTV camera fixed under a building's eaves"),

    # --- Canine unit ------------------------------------------------------
    ("IMG_9294", "k9", "Handler and service dog", "Vonlet handler kneeling with a service dog beside the branded car"),
    ("IMG_9297", "k9", "K-9 patrol pair", "Handler and dog standing beside a company vehicle"),

    # --- Site deployments (frames the client sent directly, Nov 2026) ------
    ("wa-01-foot-patrol", "sites", "Cleared boundary, walked", "Vonlet officer walking a cleared sand boundary line between trees on a dry site"),
    ("wa-02-gatehouse-register", "sites", "Gatehouse duty", "Two Vonlet officers at a guard desk with occurrence books and a two-way radio"),
    ("wa-03-quad-driveway", "sites", "Quad bike to the main gate", "Vonlet officer riding a quad bike up a concrete driveway past a gated entrance"),
    ("wa-04-quad-lawn", "sites", "Patrolling inside the fence", "Vonlet officer on a quad bike on a lawn inside a razor-wire perimeter fence"),
    ("wa-05-site-desk-pair", "sites", "Post at the site desk", "Two Vonlet officers at a desk outside a site building, one seated with a rifle across his knees"),
    ("wa-06-armed-sentry", "sites", "Armed sentry at the entrance", "Armed Vonlet officer seated at an entrance with a shotgun, hard hats and a kit crate beside him"),
    ("wa-07-veranda-post", "sites", "Veranda post and relief", "Armed Vonlet officer seated along a building veranda with a colleague at a desk behind him"),
]

# Lead each collection with its strongest frame, then interleave collections so
# consecutive near-identical frames are not shown side by side.
COVER = {
    "leadership": "IMG_9346",
    "tactical": "IMG_9309",
    "operations": "IMG_9250",
    "people": "IMG_9363",
    "field": "IMG_9326",
    "sites": "wa-04-quad-lawn",
    "tech": "IMG_9399",
    "k9": "IMG_9294",
    "office": "IMG_9343",
    "fleet": "IMG_9336",
    "training": "IMG_9261",
}
ORDER = ["leadership", "tactical", "operations", "people", "field", "sites", "tech", "k9", "office", "fleet", "training"]

# The landing page shows a curated set; the complete archive lives on archive.html.
# Two of the frames the client sent directly are carried up here so the sector
# work (warehouses, farms and mines, residential estates) is visible on the
# landing page, not only on the catalogue.
FEATURED = [
    "IMG_9346",  # leadership
    "IMG_9299",  # tactical
    "IMG_9250",  # operations room
    "IMG_9326",  # field team with the mobile office
    "wa-04-quad-lawn",  # site deployments: quad patrol inside the fence
    "IMG_9399",  # electronic security
    "IMG_9294",  # K-9 handler
    "IMG_9343",  # reception & office
    "IMG_9336",  # fleet & logistics
    "wa-02-gatehouse-register",  # site deployments: gatehouse register
    "IMG_9274",  # strategy & training
    "IMG_9280",  # people & teams
    "IMG_9409",  # ATM duty officer
    "IMG_9390",  # people & teams, staff kitchen
]


def image_size(name: str) -> tuple[int, int]:
    out = subprocess.check_output(
        ["identify", "-format", "%w %h", str(THUMBS / f"{name}.webp")], text=True
    )
    width, height = out.split()
    return int(width), int(height)


def build_order() -> list[tuple[str, str, str, str]]:
    by_collection: dict[str, list[tuple[str, str, str, str]]] = {}
    for row in PHOTOS:
        by_collection.setdefault(row[1], []).append(row)

    for collection, rows in by_collection.items():
        cover = COVER.get(collection)
        rows.sort(key=lambda row: (row[0] != cover, row[0]))

    queues = {collection: list(rows) for collection, rows in by_collection.items()}
    ordered: list[tuple[str, str, str, str]] = []
    # First pass: one cover photo per collection.
    for collection in ORDER:
        if queues.get(collection):
            ordered.append(queues[collection].pop(0))
    # Remaining photos, round-robin across collections.
    while any(queues.values()):
        for collection in ORDER:
            if queues.get(collection):
                ordered.append(queues[collection].pop(0))
    return ordered


def render_card(row: tuple[str, str, str, str], indent: str = "          ") -> str:
    name, collection, title, alt = row
    meta = COLLECTIONS[collection]
    width, height = image_size(name)
    brief = meta["brief"].replace(" - ", " — ")
    return (
        f'{indent}<article class="mission-card" data-category="{collection}" data-group="archive"\n'
        f'{indent}  data-title="{html.escape(title, quote=True)}"\n'
        f'{indent}  data-service="{meta["service"]}"\n'
        f'{indent}  data-kind="Vonlet company archive photograph"\n'
        f'{indent}  data-full="assets/images/full/{name}.webp"\n'
        f'{indent}  data-brief="{html.escape(brief, quote=True)}"\n'
        f'{indent}  data-equipment="{html.escape(meta["kit"], quote=True)}">\n'
        f'{indent}  <button class="mission-open" type="button" aria-haspopup="dialog" aria-label="Expand photograph: {html.escape(title, quote=True)}">\n'
        f'{indent}    <img src="assets/images/thumbs/{name}.webp" alt="{html.escape(alt, quote=True)}" width="{width}" height="{height}" loading="lazy" decoding="async">\n'
        f'{indent}    <span class="card-scrim" aria-hidden="true"></span>\n'
        f'{indent}    <span class="mission-info"><span class="mission-category">{html.escape(meta["label"].upper())}</span><span class="mission-title">{html.escape(title)}</span></span>\n'
        f'{indent}    <span class="card-expand" aria-hidden="true"><svg class="icon"><use href="#i-up-right"/></svg></span>\n'
        f'{indent}  </button>\n'
        f'{indent}</article>'
    )


def main() -> None:
    photos = build_order()
    every = {p.stem for p in THUMBS.glob("*.webp")}
    if {row[0] for row in PHOTOS} != every:
        missing = every - {row[0] for row in PHOTOS}
        extra = {row[0] for row in PHOTOS} - every
        raise SystemExit(f"Catalogue mismatch. Uncatalogued: {sorted(missing)} Missing files: {sorted(extra)}")

    by_name = {row[0]: row for row in photos}
    counts = {key: sum(1 for row in PHOTOS if row[1] == key) for key in COLLECTIONS}

    # Landing page: a curated dozen, not the whole archive.
    unknown = [name for name in FEATURED if name not in by_name]
    if unknown:
        raise SystemExit(f"Featured names are not in the catalogue: {unknown}")
    featured_cards = "\n".join(render_card(by_name[name]) for name in FEATURED)
    featured_html = (
        '        <p class="sr-only" id="gallery-status" role="status" aria-live="polite">'
        f"Showing {len(FEATURED)} selected photographs from the {len(PHOTOS)}-frame company archive.</p>\n"
        '        <div class="gallery-grid gallery-grid--archive gallery-grid--featured" id="gallery-grid">\n'
        + featured_cards
        + "\n        </div>"
    )
    index_source = INDEX.read_text(encoding="utf-8")
    index_source, replaced = re.subn(
        r"(<!-- GALLERY:START -->).*?(<!-- GALLERY:END -->)",
        lambda match: f"{match.group(1)}\n{featured_html}\n        {match.group(2)}",
        index_source,
        flags=re.S,
    )
    if not replaced:
        raise SystemExit("GALLERY markers not found in index.html")
    INDEX.write_text(index_source, encoding="utf-8")

    # Archive page: the complete set with collection filters.
    cards = "\n".join(render_card(row) for row in photos)
    tabs = [
        f'<button class="filter-tab is-active" type="button" data-filter="all" aria-pressed="true">All photographs <span>{len(PHOTOS)}</span></button>'
    ]
    for key in ORDER:
        tabs.append(
            f'<button class="filter-tab" type="button" data-filter="{key}" aria-pressed="false">{html.escape(COLLECTIONS[key]["label"])} <span>{counts[key]}</span></button>'
        )
    archive_html = (
        '        <div class="gallery-toolbar reveal">\n'
        '          <div class="filter-tabs" role="group" aria-label="Filter the archive by collection">\n'
        "            " + "\n            ".join(tabs) + "\n"
        "          </div>\n"
        '          <span class="gallery-hint"><svg class="icon" aria-hidden="true"><use href="#i-expand"/></svg> SELECT TO EXPAND</span>\n'
        "        </div>\n"
        '        <p class="sr-only" id="gallery-status" role="status" aria-live="polite">Showing all '
        f"{len(PHOTOS)} photographs from the Vonlet company archive.</p>\n\n"
        '        <div class="gallery-grid gallery-grid--archive" id="gallery-grid">\n'
        + cards
        + "\n        </div>"
    )
    if ARCHIVE.exists():
        archive_source = ARCHIVE.read_text(encoding="utf-8")
        archive_source, replaced = re.subn(
            r"(<!-- ARCHIVE:START -->).*?(<!-- ARCHIVE:END -->)",
            lambda match: f"{match.group(1)}\n{archive_html}\n        {match.group(2)}",
            archive_source,
            flags=re.S,
        )
        if not replaced:
            raise SystemExit("ARCHIVE markers not found in archive.html")
        ARCHIVE.write_text(archive_source, encoding="utf-8")

    print(f"Rendered {len(FEATURED)} featured frames on index.html and {len(PHOTOS)} across {len(COLLECTIONS)} collections on archive.html.")
    for key in ORDER:
        print(f"  {COLLECTIONS[key]['label']:<24} {counts[key]:>3}")


if __name__ == "__main__":
    main()
