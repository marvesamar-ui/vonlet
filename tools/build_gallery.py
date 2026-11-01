#!/usr/bin/env python3
"""Build the Vonlet operations gallery markup from the company photo archive.

Every photograph in the Google Drive folder "security" was reviewed and
catalogued. This script renders the static gallery markup (so the archive also
works without JavaScript) twice: a curated dozen between the GALLERY markers in
index.html, and the complete set between the ARCHIVE markers in archive.html.

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
    # --- Operations room -------------------------------------------------
    ("IMG_9248", "operations", "Duty desk portrait", "A Vonlet operations officer in a blue company polo at his desk"),
    ("IMG_9249", "operations", "Operations officer on station", "Vonlet operations officer working at a desk beside a window"),
    ("IMG_9250", "operations", "Operations desk briefing", "Vonlet manager briefing two officers at the OPERATIONS desk"),
    ("IMG_9251", "operations", "Supervisor at the operations desk", "Supervisor and colleagues at the Vonlet OPERATIONS desk"),
    ("IMG_9252", "operations", "Shift briefing", "Vonlet manager, officer and uniformed colleague at the operations desk"),
    ("IMG_9253", "operations", "Uniformed officer on shift", "Uniformed Vonlet officer with colleagues during an operations briefing"),
    ("IMG_9255", "operations", "Planning notes at the desk", "Vonlet officer working at a laptop in front of a strategy whiteboard"),
    ("IMG_9256", "operations", "Reviewing the day's reports", "Vonlet officer reviewing documents beside a laptop and whiteboard"),
    ("IMG_9257", "operations", "Client service desk", "Vonlet officer at a desk with a wall-mounted display behind him"),
    ("IMG_9258", "operations", "Head office desk", "Senior Vonlet officer seated at a desk with a laptop"),
    ("IMG_9259", "operations", "Working through the files", "Vonlet officer at a laptop with folders and a water bottle on the desk"),
    ("IMG_9260", "operations", "Records and reporting", "Vonlet officer reviewing paperwork beside a laptop"),
    # --- Strategy & training ---------------------------------------------
    ("IMG_9261", "training", "Strategy workshop opens", "Vonlet staff seated around a conference table with laptops and water bottles"),
    ("IMG_9262", "training", "Group discussion", "Vonlet facilitator leading a discussion at the training table"),
    ("IMG_9263", "training", "Facilitator at the table", "Facilitator standing among seated Vonlet staff during a workshop"),
    ("IMG_9264", "training", "Workshop round table", "Vonlet staff smiling around the training table with laptops open"),
    ("IMG_9265", "training", "Listening session", "Vonlet staff following a presentation at the training table"),
    ("IMG_9266", "training", "Working through the workbook", "Two Vonlet staff reviewing a laptop during the workshop"),
    ("IMG_9267", "training", "Laptop exercise", "Vonlet colleagues comparing notes on a laptop during training"),
    ("IMG_9268", "training", "Peer review", "Vonlet staff reviewing a laptop together at the workshop"),
    ("IMG_9269", "training", "Coaching at the table", "Facilitator coaching two staff members at the training table"),
    ("IMG_9270", "training", "IBSP whiteboard session", "Facilitator writing on a whiteboard headed Introduction to Business Strategy and Planning"),
    ("IMG_9271", "training", "Strategy presentation", "Vonlet facilitator presenting at the IBSP whiteboard"),
    ("IMG_9272", "training", "Table discussion", "Vonlet staff discussing points during a strategy session"),
    ("IMG_9273", "training", "Presenting the strategy map", "Facilitator presenting a whiteboard strategy map to seated staff"),
    ("IMG_9274", "training", "Explaining the roadmap", "Facilitator and staff member at the whiteboard during a planning session"),
    ("IMG_9275", "training", "Classroom questions", "Seated Vonlet staff listening to the facilitator at the whiteboard"),
    # --- People & teams --------------------------------------------------
    ("IMG_9277", "people", "Marketing team with branded car", "Four Vonlet marketing staff beside a branded white Honda Fit"),
    ("IMG_9278", "people", "Marketing team, alternate pose", "Vonlet marketing staff posing beside the branded company car"),
    ("IMG_9279", "people", "Brand team at the office", "Four Vonlet staff standing by a marketing vehicle on the lawn"),
    ("IMG_9280", "people", "Marketing team group photo", "Vonlet marketing team lined up in front of their branded car"),
    ("IMG_9281", "people", "Team portrait with vehicle", "Vonlet marketing staff posed beside the branded Honda Fit"),
    ("IMG_9282", "people", "Mixed team portrait", "Male and female Vonlet staff beside a branded vehicle"),
    ("IMG_9283", "people", "Team at the head office", "Vonlet team portrait in front of a branded car at head office"),
    ("IMG_9284", "people", "Company car and team", "Four Vonlet team members beside a branded white car"),
    ("IMG_9289", "people", "Team with response pickup", "Vonlet staff beside a branded Toyota Hilux at head office"),
    ("IMG_9290", "people", "Field team portrait", "Four Vonlet team members beside the response pickup"),
    ("IMG_9291", "people", "Response team group photo", "Vonlet response team posed in front of a branded Hilux"),
    ("IMG_9292", "people", "Operations team portrait", "Three Vonlet staff beside the company pickup"),
    ("IMG_9293", "people", "Team briefing at the pickup", "Vonlet team members standing at a branded Hilux"),
    ("IMG_9363", "people", "Reception team group photo", "Six Vonlet staff in company polo shirts at the reception counter"),
    ("IMG_9364", "people", "Reception team, alternate pose", "Vonlet reception team posed behind the head office counter"),
    ("IMG_9365", "people", "Front office team", "Four Vonlet staff standing in the reception area"),
    ("IMG_9366", "people", "Client service team", "Four Vonlet staff in blue uniforms at the reception area"),
    ("IMG_9367", "people", "Uniform display", "Vonlet officer with a mannequin wearing the tactical uniform"),
    ("IMG_9368", "people", "Uniform display portrait", "Female Vonlet officer beside a uniformed mannequin"),
    ("IMG_9369", "people", "Tactical uniform display", "Vonlet officer posing next to a mannequin in body armour"),
    ("IMG_9370", "people", "Officer with uniform display", "Vonlet officer beside the tactical uniform mannequin"),
    ("IMG_9371", "people", "Operations officer portrait", "Vonlet officer in a blue company shirt seated at a desk"),
    ("IMG_9372", "people", "Desk portrait, arms folded", "Vonlet officer smiling with arms folded at her desk"),
    ("IMG_9373", "people", "Client service officer", "Vonlet officer in blue uniform holding a phone at her desk"),
    ("IMG_9374", "people", "Reception officer portrait", "Smiling Vonlet officer with a phone at the reception desk"),
    ("IMG_9375", "people", "Officer at the keyboard", "Vonlet officer working at a computer in the head office"),
    ("IMG_9376", "people", "Front desk portrait", "Vonlet officer smiling at a reception desk"),
    ("IMG_9377", "people", "Seated officer portrait", "Vonlet officer seated at her workstation"),
    ("IMG_9378", "people", "Workstation portrait", "Vonlet officer at a desktop computer with a water bottle beside her"),
    ("IMG_9379", "people", "Desk duty", "Vonlet officer seated at a Lenovo desktop in the office"),
    ("IMG_9380", "people", "Accounts desk portrait", "Vonlet staff member in a grey polo at a workstation"),
    ("IMG_9381", "people", "Finance officer at work", "Vonlet staff member working at a desktop computer"),
    ("IMG_9382", "people", "Office portrait", "Vonlet officer at her desk in a blue company shirt"),
    ("IMG_9383", "people", "Customer service desk", "Vonlet officer smiling at her workstation"),
    ("IMG_9384", "people", "Service desk portrait", "Vonlet officer seated at a desktop computer"),
    ("IMG_9385", "people", "Senior officer portrait", "Senior Vonlet officer in a white company polo at his desk"),
    ("IMG_9386", "people", "Management at the desk", "Vonlet manager at a desktop computer in the head office"),
    ("IMG_9387", "people", "Head office management", "Senior Vonlet officer working at his desk"),
    ("IMG_9388", "people", "Reception counter briefing", "Vonlet reception staff seated behind the curved wooden counter"),
    ("IMG_9389", "people", "Reception counter team", "Three Vonlet reception staff at the counter with mission boards behind"),
    ("IMG_9390", "people", "Canteen staff at work", "Vonlet catering staff preparing food in the staff kitchen"),
    ("IMG_9391", "people", "Kitchen duty", "Canteen team member stirring a pot in the kitchen"),
    ("IMG_9392", "people", "Staff kitchen portrait", "Vonlet catering staff in blue uniform at the stove"),
    ("IMG_9393", "people", "Catering team", "Canteen staff preparing a meal in the company kitchen"),
    # --- Reception & office ----------------------------------------------
    ("IMG_9340", "office", "Reception and client service", "Vonlet reception staff behind the curved wooden counter with mission boards"),
    ("IMG_9341", "office", "Front desk team", "Vonlet receptionists assisting visitors at the head office counter"),
    ("IMG_9342", "office", "Visitor check-in", "Vonlet receptionist standing at the counter with seated colleagues"),
    ("IMG_9343", "office", "Client handover at reception", "Vonlet receptionist handing documents across the counter"),
    ("IMG_9344", "office", "Reception duty", "Vonlet reception staff serving at the front desk"),
    ("IMG_9346", "leadership", "Chief executive at her desk", "Vonlet chief executive in a pink blouse working at a laptop"),
    ("IMG_9347", "leadership", "Chief executive portrait", "Chief executive in a pink blouse, hand to her chin, at her desk"),
    ("IMG_9348", "leadership", "Executive office portrait", "Chief executive seated at her office desk with hands clasped"),
    ("IMG_9349", "leadership", "Leadership at work", "Chief executive working at a laptop in her head office"),
    ("IMG_9350", "leadership", "Board papers review", "Chief executive at her desk with a laptop, diary and notebooks"),
    ("IMG_9351", "leadership", "Chief executive briefing", "Chief executive in a pink blouse seated behind her desk"),
    ("IMG_9352", "leadership", "Strategy session", "Chief executive reviewing work at her laptop"),
    ("IMG_9353", "leadership", "Head office leadership", "Chief executive seated at her desk with a laptop open"),
    ("IMG_9354", "office", "IT desk portrait", "Vonlet staff member working at a desktop computer"),
    ("IMG_9355", "office", "Systems desk", "Vonlet officer at a Lenovo workstation in the head office"),
    ("IMG_9356", "office", "Workstation review", "Vonlet staff member seated at a desktop computer"),
    ("IMG_9357", "office", "Office systems duty", "Vonlet officer working at a desktop with a water bottle beside him"),
    ("IMG_9358", "office", "Records office", "Vonlet staff member reviewing documents at a workstation"),
    ("IMG_9359", "office", "Desktop duty", "Vonlet officer typing at a desktop computer"),
    ("IMG_9360", "office", "Head office workstation", "Vonlet staff member at a desktop computer"),
    # --- Tactical & equipment --------------------------------------------
    ("IMG_9299", "tactical", "Body armour team", "Two Vonlet officers wearing body armour beside a branded car"),
    ("IMG_9300", "tactical", "Tactical kit inspection", "Officers in body armour and helmets standing by a company vehicle"),
    ("IMG_9301", "tactical", "Response team with pickup", "Two officers in tactical kit in front of a silver Hilux"),
    ("IMG_9302", "tactical", "Tactical response pair", "Vonlet officers in body armour and helmets with a baton"),
    ("IMG_9303", "tactical", "Kit check before deployment", "Officers adjusting body armour beside the response pickup"),
    ("IMG_9304", "tactical", "Equipped for high-risk duty", "Two Vonlet officers in protective kit at the pickup"),
    ("IMG_9305", "tactical", "Baton drill", "Officer holding a baton in front of a company pickup"),
    ("IMG_9306", "tactical", "Tactical stance", "Vonlet officer with baton and helmet beside the pickup"),
    ("IMG_9307", "tactical", "Response drill partners", "Two officers in tactical kit standing by the vehicle"),
    ("IMG_9308", "tactical", "Deployment brief", "Officers in body armour preparing beside the pickup"),
    ("IMG_9309", "tactical", "Supervisor and tactical team", "Manager with two officers in body armour beside the pickup"),
    ("IMG_9310", "tactical", "Tactical team and supervisor", "Vonlet supervisor standing with two equipped officers"),
    ("IMG_9311", "tactical", "Pre-deployment photo", "Three Vonlet staff posed in front of the response pickup"),
    ("IMG_9312", "tactical", "Team check", "Supervisor with two officers in body armour at the vehicle"),
    ("IMG_9313", "tactical", "Control and restraint drill", "Vonlet officer demonstrating a control technique during training"),
    ("IMG_9314", "tactical", "Restraint technique practice", "Officer practising a control hold on a colleague in a drill"),
    ("IMG_9315", "tactical", "Response drill, control position", "Vonlet officers rehearsing a control technique on the lawn"),
    ("IMG_9316", "tactical", "Ground control drill", "Officer demonstrating a restraint technique during a training exercise"),
    ("IMG_9317", "tactical", "Drill practice", "Vonlet officer holding a colleague in a control position"),
    ("IMG_9318", "tactical", "Response training", "Vonlet officers rehearsing a restraint technique outdoors"),
    # --- Field duty -------------------------------------------------------
    ("IMG_9319", "field", "Officers at the pickup", "Two Vonlet officers standing at a branded pickup"),
    ("IMG_9320", "field", "Field team at the vehicle", "Two officers leaning against the response pickup"),
    ("IMG_9321", "field", "Office team at the pickup", "Vonlet staff standing beside the company pickup"),
    ("IMG_9322", "field", "Gate post duty", "Vonlet guard at a container gate post speaking with a visitor"),
    ("IMG_9323", "field", "Visitor at the gate", "Uniformed Vonlet guard taking details from a visitor"),
    ("IMG_9324", "field", "Static post check", "Guard at a container post with a chair and clipboard"),
    ("IMG_9325", "field", "Access point duty", "Vonlet guard at a site entrance with a visitor"),
    ("IMG_9326", "field", "Team with mobile office", "Vonlet staff lined up in front of a mobile office truck"),
    ("IMG_9327", "field", "Site team group photo", "Vonlet team assembled beside the mobile office unit"),
    ("IMG_9328", "field", "Field team with truck", "Vonlet staff posed in front of the mobile office truck"),
    ("IMG_9329", "field", "Full team lineup", "Large Vonlet team lined up outdoors in uniform"),
    ("IMG_9330", "field", "Team muster", "Vonlet staff and officers in a wide group photo"),
    ("IMG_9331", "field", "Company muster photo", "Vonlet team group photograph with vehicles behind"),
    ("IMG_9332", "field", "Staff lineup", "Vonlet staff and guards assembled outdoors"),
    ("IMG_9333", "field", "Truck driver on duty", "Vonlet driver at the wheel of a branded truck"),
    ("IMG_9409", "field", "ATM duty officer", "Vonlet officer in a blue suit standing beside a bank ATM"),
    # --- Fleet & logistics ------------------------------------------------
    ("IMG_9334", "fleet", "Driver at the wheel", "Vonlet driver in the cab of a covered truck"),
    ("IMG_9335", "fleet", "Truck cab portrait", "Vonlet driver seated in the cab of a branded truck"),
    ("IMG_9336", "fleet", "Covered truck at the depot", "Branded Vonlet Security truck with a covered load"),
    ("IMG_9337", "fleet", "Fleet truck", "Vonlet Security covered truck parked on site"),
    ("IMG_9338", "fleet", "Open truck inspection", "Vonlet officer standing at the open rear of a truck"),
    ("IMG_9339", "fleet", "Loading bay check", "Officer at the open rear of a company truck"),
    # --- Electronic security ---------------------------------------------
    ("IMG_9285", "tech", "CCTV mast installation", "Technician on a ladder adjusting a solar-powered camera mast"),
    ("IMG_9286", "tech", "Installing a camera post", "Vonlet technician setting a camera on a pole while a colleague steadies the ladder"),
    ("IMG_9287", "tech", "Camera alignment", "Technician aligning a camera mounted on a mast"),
    ("IMG_9288", "tech", "Solar camera check", "Vonlet staff securing a camera and solar panel on a mast"),
    ("IMG_9394", "tech", "Solar camera mast", "Solar-powered CCTV camera on a pole against a blue sky"),
    ("IMG_9395", "tech", "Camera over the perimeter", "CCTV camera on a mast above a residential wall"),
    ("IMG_9396", "tech", "Perimeter mast camera", "Camera unit on a tall pole overlooking a walled property"),
    ("IMG_9397", "tech", "Mast camera and sky", "CCTV camera on a mast with a solar panel above a garden"),
    ("IMG_9398", "tech", "Solar-powered surveillance", "Dual-lens camera with a solar panel on a street-side pole"),
    ("IMG_9399", "tech", "Eaves-mounted camera", "CCTV camera fixed under a building's eaves"),
    ("IMG_9400", "tech", "External camera installation", "Wall-mounted CCTV camera under a roof overhang"),
    ("IMG_9401", "tech", "Camera coverage check", "Security camera mounted on an exterior wall"),
    ("IMG_9402", "tech", "Camera on the overhang", "CCTV camera installed under a timber roof overhang"),
    ("IMG_9403", "tech", "Roofline camera", "Dome camera fixed beneath the eaves of a building"),
    # --- K-9 units ---------------------------------------------------------
    ("IMG_9294", "k9", "Handler and service dog", "Vonlet handler kneeling with a service dog beside the branded car"),
    ("IMG_9295", "k9", "K-9 team portrait", "Uniformed handler with a dog in front of a company vehicle"),
    ("IMG_9296", "k9", "Service dog on duty", "Vonlet handler posing with a dog beside a branded car"),
    ("IMG_9297", "k9", "K-9 patrol pair", "Handler and dog standing beside a company vehicle"),
    ("IMG_9298", "k9", "K-9 unit ready", "Vonlet handler with a service dog in front of a branded car"),
]

# Lead each collection with its strongest frame, then interleave collections so
# consecutive near-identical frames are not shown side by side.
COVER = {
    "leadership": "IMG_9346",
    "tactical": "IMG_9309",
    "operations": "IMG_9250",
    "people": "IMG_9363",
    "field": "IMG_9329",
    "tech": "IMG_9399",
    "k9": "IMG_9295",
    "office": "IMG_9341",
    "fleet": "IMG_9337",
    "training": "IMG_9270",
}
ORDER = ["leadership", "tactical", "operations", "people", "field", "tech", "k9", "office", "fleet", "training"]

# The landing page shows a dozen frames; the complete set lives on archive.html.
FEATURED = [
    "IMG_9346",  # leadership
    "IMG_9299",  # tactical
    "IMG_9250",  # operations room
    "IMG_9329",  # field team lineup
    "IMG_9399",  # electronic security
    "IMG_9295",  # K-9 unit
    "IMG_9341",  # reception & office
    "IMG_9337",  # fleet & logistics
    "IMG_9270",  # strategy & training
    "IMG_9302",  # tactical response pair
    "IMG_9409",  # ATM duty officer
    "IMG_9390",  # people & teams
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
