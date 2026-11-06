#!/usr/bin/env python3
"""Build services.html: all twenty-three Vonlet service lines on the local site.

Fifteen of the lines were taken from the company's live site — the services
index, the fourteen individual /service/... pages and the cash-in-transit block
on the home page — and rewritten into the local page's voice. The slug and the
"Source" link on each block point back at the page it came from, so the copy can
be audited against the original at any time.

The other eight (bank and ATM, warehouse, retail, farms and mines, residential,
functions, private escorts, private investigations) were given to us directly by
the company for this site and are not yet published on vonletsecurity.co.zw. They
carry no source link and say so, and their photographs are the recent site frames
the client sent over WhatsApp — see tools/process-wa-frames.sh.

Usage:  python3 tools/build_services.py
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
OUTPUT = ROOT / "services.html"

SITE = "https://vonletsecurity.co.zw"

# ---------------------------------------------------------------------------
# Service lines. Field order:
#   slug, name, group, summary, paragraphs, points, image, alt, note, source,
#   dispatch value, dispatch label
# `note` is shown under the photograph: only the cash-in-transit image is not a
# company photograph, and the site frames the client sent directly are labelled
# as such. `source` is the page the copy came from; leave it out (None) for a
# line the company gave us for this site but has not published yet, and the
# block says so instead of linking to a page that does not exist.
# ---------------------------------------------------------------------------
ARCHIVE_NOTE = "FROM THE COMPANY ARCHIVE"
CONCEPT_NOTE = "ILLUSTRATIVE CONCEPT IMAGE — NOT A COMPANY PHOTOGRAPH"
CLIENT_NOTE = "SUPPLIED BY THE CLIENT — SITE FRAME, NOVEMBER 2026"
LOCAL_ONLY = "This line was given to us by the company for this site and is not yet published on vonletsecurity.co.zw."

SERVICES = [
    dict(
        slug="armed-guards",
        name="Armed guards",
        group="Manned guarding",
        summary="Static or roving guards trained to carry firearms, deployed where the risk justifies an armed presence.",
        paragraphs=[
            "Vonlet's armed officers train intensively in-house in collaboration with the Zimbabwe Republic Police and the Zambia National Police, keeping their shooting skills and handling drills current.",
            "They are deployed to high-risk environments where valuable goods or volatile conditions demand an armed presence.",
        ],
        points=[
            "Static or roving armed posts",
            "In-house training with ZRP and Zambia National Police",
            "Regular shooting-skills practice",
            "Mines, sand-poaching areas, fuel depots and high-value premises",
        ],
        image="assets/images/full/IMG_9302.webp",
        alt="Two Vonlet officers in body armour and helmets, one holding a baton",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/armed-guards/",
        dispatch="armed",
        dispatch_label="Armed guards",
    ),
    dict(
        slug="unarmed-guards",
        name="Unarmed guards",
        group="Manned guarding",
        summary="Static and roving guards who hold a post or patrol a property, trained to handle access, theft and vandalism.",
        paragraphs=[
            "This branch of the service covers two postings. Static guards are designated to a specific area and protect it until they are relieved, escorting staff and protecting assets and infrastructure at entrances and exits.",
            "Roving or patrolling guards move across the whole area or premises, guarding against theft and vandalism and providing a human safety presence.",
        ],
        points=[
            "Static guards on fixed posts",
            "Roving and patrolling guards",
            "Staff escorts",
            "Protection of entrances, exits and infrastructure",
        ],
        image="assets/images/full/IMG_9326.webp",
        alt="Vonlet site team lined up in front of the mobile office truck",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/unarmed-guards/",
        dispatch="unarmed",
        dispatch_label="Unarmed guards",
    ),
    dict(
        slug="secret-service",
        name="Secret service — undercover guards",
        group="Manned guarding",
        summary="Guards placed into the workplace discreetly, with an inconspicuous identity, to work alongside your staff.",
        paragraphs=[
            "Undercover guards are incorporated into the workplace in a discreet and diplomatic way, which clothes them with an inconspicuous identity and lets them mingle with your personnel and customers.",
            "In the course of their duties they report back and bring an evaluation of the areas that need improvement or monitoring. Their presence saves a premises loss of time and resources, cash theft, shoplifting and vandalism.",
        ],
        points=[
            "Discreet, plain-clothes deployment",
            "Working among staff and customers",
            "Reporting and evaluation of weak points",
            "Cash theft, shoplifting and vandalism prevention",
        ],
        image="assets/images/full/wa-16-site-post-suit.webp",
        alt="Vonlet officer in a light-blue suit and tie standing discreetly at the barred entrance of a client building",
        note=CLIENT_NOTE,
        source=f"{SITE}/service/secret-service/",
        dispatch="secret",
        dispatch_label="Undercover guards",
    ),
    # --- Sector security: given to us by the company, not yet on the live site.
    dict(
        slug="bank-and-atm-security",
        name="Bank & ATM security",
        group="Sector security",
        summary="Guarding at branches, cash offices and standalone ATM points — presence where the queue forms, cover where the machine stands.",
        paragraphs=[
            "Officers are posted at banking premises and at standalone ATM points, where the risk sits in the few minutes a customer spends withdrawing cash. A visible uniform beside the machine discourages the observation of PIN entry, snatch-and-run theft, and the tampering and skimming that target an unattended terminal.",
            "After hours the same post keeps the machine and its surroundings under watch. Attempted break-ins, loitering vehicles, blocked sight-lines and damaged casing are reported to the control room while there is still time to act, and every visit is written into the occurrence book so the client has a record of cover, not a promise of it.",
        ],
        points=[
            "Static posts at entrances, queues and cash desks",
            "Day and after-hours cover at ATM points",
            "Deterrence of snatching, skimming and tampering",
            "Queue and door management at peak hours",
            "Logged visits and incident reporting to the control room",
        ],
        image="assets/images/full/wa-11-bank-duty-suit.webp",
        alt="Vonlet officer in a navy lounge suit and tie on post at a bank branch, beside the bank's glazed frontage",
        note=CLIENT_NOTE,
        source=None,
        dispatch="bank-atm",
        dispatch_label="Bank & ATM security",
    ),
    dict(
        slug="warehouse-security",
        name="Warehouse & logistics security",
        group="Sector security",
        summary="Gate, yard and stock protection for warehouses, depots and distribution points, where the loss is usually in the goods.",
        paragraphs=[
            "A warehouse is guarded at three points: the gate, the yard and the stock itself. Officers register vehicles and visitors, check outbound loads against the paperwork that should accompany them, and keep the fence line walked, so a load cannot leave the premises without a document to match it.",
            "Because most loss in distribution is internal, posts are paired with discreet checks — seal numbers, weighbridge tickets, night-shift movement and the loading bays that sit outside a supervisor's eye. Mobile patrols on Vonlet's vehicles, quad bikes included, cover the perimeter ground a fixed post cannot see from its chair.",
        ],
        points=[
            "Gate and boom control with a vehicle register",
            "Load, waybill and seal verification",
            "Roving patrols of yard, racks and fence line",
            "Night-shift and after-hours stock cover",
            "Mobile quad-bike and vehicle patrol",
        ],
        image="assets/images/full/wa-03-quad-driveway.webp",
        alt="Vonlet officer riding a quad bike up a concrete driveway past a gated entrance",
        note=CLIENT_NOTE,
        source=None,
        dispatch="warehouse",
        dispatch_label="Warehouse & logistics security",
    ),
    dict(
        slug="retail-security",
        name="Retail security",
        group="Sector security",
        summary="Store-floor, forecourt and cash-office guarding that cuts shrinkage without turning the entrance into a checkpoint.",
        paragraphs=[
            "Store detection works best when customers stop noticing it. A uniformed officer holds the entrance, the trolley bay and the queue lines, while discreet cover on the floor — the undercover guards described above work this sector in particular — watches fitting rooms, high-value shelves and the points where security tags are defeated.",
            "The other half of the job sits outside trading hours: deliveries in the early morning, the cash office before a banking run, alarm response once the shutters are down, and the parking area after dark, when the store is closed but the stock inside is not.",
        ],
        points=[
            "Uniformed presence at the door and on the floor",
            "Discreet cover for fitting rooms and high-value stock",
            "Tag, till and cash-office watch",
            "Delivery and collection hours covered",
            "After-hours perimeter, parking and alarm response",
        ],
        image="assets/images/full/wa-12-depot-briefing.webp",
        alt="Vonlet officers in reflective storm coats on post inside a client premises",
        note=CLIENT_NOTE,
        source=None,
        dispatch="retail",
        dispatch_label="Retail security",
    ),
    dict(
        slug="farms-and-mines-security",
        name="Farms & mines security",
        group="Sector security",
        summary="Boundary, access and materials control over ground too large to walk — farms, ranches, mines, and sand and aggregate operations.",
        paragraphs=[
            "On a farm or a mine the perimeter is the problem: kilometres of fence, gates that are meant to be open, and value that is in the ground, in a dam, on a weighbridge or in a truck. Vonlet works the boundary on foot and by vehicle, posts officers at the gate that matters and roves the rest rather than leaving it to chance.",
            "Higher-risk ground — ore, fuel, explosives stores, and sand and aggregate operations where the material itself can be carried off in a wheelbarrow — is covered by armed officers trained in-house with the Zimbabwe Republic Police and the Zambia National Police. Patrol routes and check-times are set by the site risk assessment, not by a fixed timetable an intruder can learn.",
        ],
        points=[
            "Perimeter patrols on foot and by vehicle",
            "Gate control and a stock movement register",
            "Armed cover for ore, fuel, explosives and aggregate",
            "Weighbridge and load-out checks",
            "K-9 support for veld, dam and store searches",
        ],
        image="assets/images/full/wa-01-foot-patrol.webp",
        alt="Vonlet officer walking a cleared sand boundary line between trees on a dry site",
        note=CLIENT_NOTE,
        source=None,
        dispatch="farms-mines",
        dispatch_label="Farms & mines security",
    ),
    dict(
        slug="residential-security",
        name="Residential security",
        group="Sector security",
        summary="Estates, complexes and private homes — gatehouse control, patrols of the common ground and response in the hours a house is empty.",
        paragraphs=[
            "Most residential loss happens inside a two-hour window: the school run, the workday, the house empty and the gate propped for a contractor. Vonlet mans the gatehouse, screens and registers visitors and tradespeople, and patrols the boundary and the common ground between them — on foot, or by quad bike where an estate is too large to walk twice an hour.",
            "Where there is no gatehouse, the service is a roving patrol with a logged arrival time, keyholding, and an agreed response to an alarm, plus cover for staff and service entrances and for the days a family is away. House rules, gate codes and the neighbours' sensitivities are written into the standing orders before the first shift.",
        ],
        points=[
            "Gatehouse duty with a visitor and contractor register",
            "Roving patrols of boundary and common ground",
            "Keyholding and alarm response",
            "Absence, holiday and staff-hours cover",
            "Standing orders agreed with the complex or owner",
        ],
        image="assets/images/full/wa-04-quad-lawn.webp",
        alt="Vonlet officer on a quad bike on a lawn inside a razor-wire perimeter fence",
        note=CLIENT_NOTE,
        source=None,
        dispatch="residential",
        dispatch_label="Residential security",
    ),
    dict(
        slug="functions-security",
        name="Functions & event security",
        group="Sector security",
        summary="Guarding at weddings, funerals, launches and corporate functions — the guest list, the parking, and the property afterwards.",
        paragraphs=[
            "A function is a short, sharp security problem: a guest list that changes at the door, cash and gifts gathered in one room, alcohol, a crowded parking area, and a property at its most exposed the moment the last guest leaves. Vonlet crews are briefed to the list, control entry, keep the vehicles watched and stay on after the cleaning starts.",
            "Crews can be deployed as visibly as a row of uniforms at the gate, or quietly enough to stay out of the photographs when a family asks for that. Dogs are available on the same booking for perimeter and parking coverage where the numbers justify them.",
        ],
        points=[
            "Guest-list and gate control",
            "Parking, vehicle and gift-room watch",
            "Visible or discreet deployment by brief",
            "Crowd and bar-queue management",
            "After-event perimeter cover and sweep",
        ],
        image="assets/images/full/wa-09-suit-team-entrance.webp",
        alt="Armed Vonlet officer seated along a building veranda with a colleague at a desk behind him",
        note=CLIENT_NOTE,
        source=None,
        dispatch="functions",
        dispatch_label="Functions & event security",
    ),
    # --- Close protection & investigation, also client-supplied for this site.
    dict(
        slug="private-escorts",
        name="Private escorts",
        group="Protection & investigation",
        summary="Escorted movement of people and valuables — principals, families and high-value consignments — with a protection officer in the vehicle.",
        paragraphs=[
            "Escort work covers the journey rather than the address. An officer travels with the principal, the family or a valuable consignment from door to door, on foot or in the client's own vehicle or one of Vonlet's. Routes are planned before wheels move, pickup and drop-off points are checked first, and the detail of the day — who is met, where the vehicle stops — stays with the crew rather than the front desk.",
            "It is the service clients add when a fixed guard cannot follow them: an airport transfer, a business trip between towns, a payroll or valuation run, a school move at a time when the risk is personal rather than property. Escorts are unarmed or armed according to the threat assessment agreed with the client.",
        ],
        points=[
            "Door-to-door protection of people in transit",
            "Route planning with alternates, points checked first",
            "Foot escort or vehicle escort, unarmed or armed",
            "Airport transfers and inter-town travel",
            "Cash, valuation and high-value consignment escort",
            "Officers briefed to confidentiality, vetted as in training",
        ],
        image="assets/images/full/wa-14-airport-arrivals.webp",
        alt="Vonlet officer in a navy lounge suit meeting travellers in the International Arrivals hall",
        note=CLIENT_NOTE,
        source=None,
        dispatch="escorts",
        dispatch_label="Private escorts",
    ),
    dict(
        slug="private-investigations",
        name="Private investigations",
        group="Protection & investigation",
        summary="Surveillance, verification and internal enquiry, closed out with a report written to be usable by an insurer, an advocate or the police.",
        paragraphs=[
            "Investigations answer the questions a guard cannot: who is shorting the till, who is passing information out of the yard, what an applicant was doing before they sent you the CV that arrived this morning. The work is surveillance, enquiry and verification, run against a brief agreed in advance — scope, dates, ground and what may and may not be recorded.",
            "Every assignment closes with a written report: times, places, photographs, statements and the records checked, in a form that can be handed to an insurer, an advocate or the police. The enquiry is run alongside a guarding contract, never through the crew holding it, so the officers on site are not investigating their own shift. Enquiries stay within the law — no interception of communications, no entry to private premises.",
        ],
        points=[
            "Covert surveillance and observation",
            "Background, employment and reference verification",
            "Internal theft, shrinkage and fraud enquiries",
            "Evidence handling with an unbroken continuity record",
            "Written report for insurer, advocate or police",
            "Liaison with the Zimbabwe Republic Police where a case opens",
        ],
        image="assets/images/full/IMG_9260.webp",
        alt="Vonlet officer reviewing paperwork beside a laptop in the operations room",
        note=ARCHIVE_NOTE,
        source=None,
        dispatch="investigations",
        dispatch_label="Private investigations",
    ),
    dict(
        slug="dog-services",
        name="Dog services",
        group="K-9",
        summary="Watch and attack dogs supplied to clients, with handlers and kennel support behind them.",
        paragraphs=[
            "Because of their attentive and intimidating nature, dogs have become a substantial part of the security domain. Vonlet supplies clients with watch and attack dogs, which help bring the level of crime down and meet head-on any threat posed to a client or their property.",
            "Vonlet's service dogs are also trained to assist guards and other law-enforcement officers: drugs and explosives searches, locating missing people and finding crime-scene evidence.",
        ],
        points=[
            "Watch dogs",
            "Attack dogs",
            "Sniffing dogs for drugs and explosives searches",
            "A trained handler with every dog",
        ],
        image="assets/images/full/IMG_9294.webp",
        alt="Vonlet handler kneeling with a service dog beside a branded company car",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/dog-services/",
        dispatch="k9",
        dispatch_label="Dog services",
    ),
    dict(
        slug="dog-handling-training",
        name="Dog handling training",
        group="K-9",
        summary="Motivational training for the dogs and for the handlers who work with them.",
        paragraphs=[
            "The dog section uses motivational training techniques, in line with current international approaches, to teach its dogs to obey their handlers and apprehend intruders. The kennels breed Boerboels, German Shepherds and Rottweilers — all well suited to guard work.",
            "Training starts with the dog responding to its handler's commands and progresses to pursuing an intruder who runs away, even inside a building. Handlers are trained alongside their dog, because the professional handling and control of the dog matters as much as the dog itself. Welfare at the kennels is treated as paramount.",
        ],
        points=[
            "Boerboels, German Shepherds and Rottweilers",
            "Motivational training methods",
            "Obedience and apprehension drills",
            "Handlers trained with the dog they will work with",
            "Deployed to homes, businesses, farms, mines and schools",
        ],
        image="assets/images/full/IMG_9297.webp",
        alt="Vonlet handler standing with a service dog beside a branded company vehicle",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/dog-handling-training/",
        dispatch="training",
        dispatch_label="Dog handling training",
    ),
    dict(
        slug="close-circuit-television-cctv",
        name="Close circuit television (CCTV)",
        group="Electronic security",
        summary="Camera systems specified, installed and maintained by Vonlet's technical team.",
        paragraphs=[
            "CCTV lets you keep an eye on everything happening in a building through cameras. Vonlet supplies and installs these systems, and the components behind them are worth knowing.",
            "Image sensors convert light into electronic signals: CCD sensors are more sensitive in poor light, while CMOS sensors are the cost-effective option and a megapixel CMOS can outperform CCD on quality. Video encoders bring analogue cameras onto a network so a site can use modern features and cheaper hardware. Recorders split into digital video recorders, which process footage themselves and suit analogue cameras, and network video recorders, which encode at the camera and stream for storage and remote monitoring with IP cameras.",
        ],
        points=[
            "Camera and coverage design for the site",
            "CCD and CMOS image sensors",
            "Video encoders for analogue-to-network migration",
            "DVR and NVR recording, with remote monitoring",
        ],
        image="assets/images/full/IMG_9399.webp",
        alt="CCTV camera fixed under the eaves of a commercial building",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/close-circuit-television-cctv/",
        dispatch="cctv",
        dispatch_label="CCTV systems",
    ),
    dict(
        slug="access-control-systems",
        name="Access control systems",
        group="Electronic security",
        summary="Control over who enters, when, and where.",
        paragraphs=[
            "Vonlet supplies and installs access control systems. The published types are discretionary access control (DAC), where leadership sets who may pass, rule-based access control, which decides by policy, and identity-based access control, which decides by the person presenting credentials.",
        ],
        points=[
            "Discretionary access control (DAC)",
            "Rule-based access control",
            "Identity-based access control",
            "Installation and maintenance",
        ],
        image="assets/images/full/IMG_9325.webp",
        alt="Vonlet guard at a site entrance speaking with a visitor",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/access-control-systems/",
        dispatch="access",
        dispatch_label="Access control systems",
    ),
    dict(
        slug="intruder-alarm-systems",
        name="Intruder alarm systems",
        group="Electronic security",
        summary="Alarm systems engineered to tell you the moment an intrusion is detected.",
        paragraphs=[
            "The system comprises a control panel, an LED or LCD keypad, pet-immune and general sensors, magnetic contacts for windows and doors, and sirens. It is built to alert clients in cases of invasion or intrusion.",
        ],
        points=[
            "Control panel and keypad (LED or LCD)",
            "Pet-immune and general sensors",
            "Magnetic contacts on windows and doors",
            "Sirens and client alerting",
        ],
        image="assets/images/full/IMG_9396.webp",
        alt="Camera unit on a tall pole overlooking a walled property",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/intruder-alarm-systems/",
        dispatch="alarms",
        dispatch_label="Intruder alarm systems",
    ),
    dict(
        slug="rapid-response-systems",
        name="Rapid response systems",
        group="Electronic security",
        summary="Your alarm linked to Vonlet's control room, with a reaction team behind it.",
        paragraphs=[
            "The client's alarm system is linked to Vonlet's rapid response control room. In the event of a break-in, the report is relayed to the control room and automatically triggers the reaction team, which responds to the premises within reasonable time and inspects for any burglary.",
        ],
        points=[
            "Alarm linked to the Vonlet control room",
            "Break-in reports received and logged",
            "Reaction team triggered automatically",
            "Site inspection on arrival",
        ],
        image="assets/images/full/wa-08-rapid-response-vehicle.webp",
        alt="Vonlet's branded Rapid Response pickup on a shopping-centre forecourt",
        note=CLIENT_NOTE,
        source=f"{SITE}/service/rapid-response-systems/",
        dispatch="response",
        dispatch_label="Rapid response systems",
    ),
    dict(
        slug="guard-monitoring-systems",
        name="Guard monitoring systems",
        group="Electronic security",
        summary="A real-time online guard tour built on NFC, beacon and QR-code tags.",
        paragraphs=[
            "Staff scan tags placed on locations and assets, and the monitoring centre is informed in real time about incidents and events. Every QR-code, NFC tag or beacon scan travels to the system's web application through a cloud server.",
            "Each guard carries a unique technology identity. The smartphone becomes the work tool: photographs, voice messages, notes and signatures can be attached to the scanned item, and the guard or worker can inform facility managers immediately who is responsible for the asset or location. Departments, locations, warehouses, transport areas, airports, stores and remote areas can all be brought under the same control.",
        ],
        points=[
            "NFC, beacon and QR-code checkpoints",
            "Real-time reporting to the monitoring centre",
            "Photos, voice notes and signatures per scan",
            "Warehouses, stores, transport hubs and remote sites",
        ],
        image="assets/images/full/IMG_9250.webp",
        alt="Vonlet manager briefing two officers at the operations desk",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/guard-monitoring-systems/",
        dispatch="monitoring",
        dispatch_label="Guard monitoring systems",
    ),
    dict(
        slug="fire-drill",
        name="Fire drill",
        group="Training & safety",
        summary="Guards keep escape routes usable and fire equipment serviceable.",
        paragraphs=[
            "The guard on site ensures that fire extinguishers are neither expired nor damaged, clears corridors of impediments so people can evacuate quickly, and makes sure exit doors are kept clear and accessible to anyone who needs to leave.",
            "The frame below is deliberately the equipment and nothing else: what a Vonlet officer checks on a fire round is the extinguisher in its bracket, its seal and its service tag, the pressure reading, and the path to the exit door.",
        ],
        points=[
            "Fire extinguisher checks",
            "Corridors cleared of obstructions",
            "Exit doors kept accessible",
            "Faster, safer evacuation",
        ],
        image="assets/images/concept/fire-drill-equipment.jpg",
        alt="Illustration: a red dry-powder extinguisher with an intact safety seal and a blank inspection tag, standing against a corrugated steel kerb painted in faded hazard stripes",
        note=CONCEPT_NOTE,
        source=f"{SITE}/service/fire-drill/",
        dispatch="training",
        dispatch_label="Fire drill training",
    ),
    dict(
        slug="first-aid",
        name="First aid",
        group="Training & safety",
        summary="Life-saving training for the first minutes of a medical emergency.",
        paragraphs=[
            "First aid is the immediate treatment of a patient before trained medical personnel can take over. It is a core part of guard training at Vonlet rather than an optional extra, because it is the technique that keeps a casualty alive at the scene of an emergency.",
            "The frame below shows the kit and nothing else, because the kit is the part the guard owns: the dressing, the tape, the gloves and the sling that have to be packed, in date and reachable before an ambulance can be.",
        ],
        points=[
            "Immediate casualty care",
            "Delivered inside basic guard training",
            "Taught alongside fire drill and firearm handling",
        ],
        image="assets/images/concept/first-aid-kit.jpg",
        alt="Illustration: an open white first aid kit on a concrete floor, with a rolled bandage, gauze pads, adhesive tape, scissors and disposable gloves, and a green cross inside the lid",
        note=CONCEPT_NOTE,
        source=f"{SITE}/service/first-aid/",
        dispatch="training",
        dispatch_label="First aid training",
    ),
    dict(
        slug="basic-security-guard-training",
        name="Basic security guard training",
        group="Training & safety",
        summary="Vetting first, then a two-week training programme before any guard is deployed.",
        paragraphs=[
            "Vonlet probes every person it employs, with the emphasis on guards. Vetting is a pre-requisite and happens before any Vonlet training, in sequence: fingerprints are taken as an inspection of criminal records; every applicant must have gone through “O” Level; previous employment with another manned security service is checked; at least three references are required, excluding the previous employer; and the curriculum vitae is scrutinised to confirm its authenticity.",
            "Successful applicants then complete a two-week training programme covering basic security guard training, firearm handling, dog handling, first aid and fire drill.",
        ],
        points=[
            "Fingerprints and criminal-record inspection",
            "“O” Level as the minimum standard",
            "Previous employment and three references",
            "CV authenticity check",
            "Two-week training programme",
        ],
        image="assets/images/full/IMG_9274.webp",
        alt="Facilitator explaining a whiteboard plan to seated Vonlet staff",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/basic-security-guard-training/",
        dispatch="training",
        dispatch_label="Basic security guard training",
    ),
    dict(
        slug="firearm-handling",
        name="Firearm handling",
        group="Training & safety",
        summary="Additional training and licensing before an officer may carry a firearm on duty.",
        paragraphs=[
            "To become an armed security guard and carry a firearm on duty, an officer must complete additional hours of training specialising in firearm handling and safety, on top of the basic guard course. Those hours include learning how to handle and fire a weapon.",
            "On completion the officer is issued a card that allows them to legally carry a firearm while on duty. Requirements differ between jurisdictions, and all of them involve a rigorous, multi-point background check before anyone is qualified to carry.",
        ],
        points=[
            "Firearm handling and safety",
            "Weapon handling and live firing",
            "Licensing card for carriage on duty",
            "Multi-point background check",
        ],
        image="assets/images/full/IMG_9299.webp",
        alt="Two Vonlet officers in body armour and helmets beside a branded response vehicle",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/firearm-handling/",
        dispatch="armed",
        dispatch_label="Firearm handling training",
    ),
    dict(
        slug="cash-in-transit",
        name="Cash-in-transit",
        group="Cash services",
        summary="Management of the cash collection service, from task assignment to accounting for every book.",
        paragraphs=[
            "Cash-in-transit provides management of the cash collection service for CIT staff: the assignment of tasks, the selection of routes, and the accounting of all books. Runs are made with Vonlet's branded fleet.",
            "Vonlet publishes CIT as a core service on its home page rather than as one of the fourteen individual service pages, which is why it completes the fifteen lines the company publishes — the eight sector, escort and investigation lines below it were given to us for this site directly.",
        ],
        points=[
            "Task assignment",
            "Route selection",
            "Accounting for all books",
            "Branded vehicles and trained crews",
        ],
        image="assets/images/cit/v2-convoy.jpg",
        alt="Illustration: two branded armoured vans flanking an escort pickup",
        note=CONCEPT_NOTE,
        source=f"{SITE}/#home",
        dispatch="cit",
        dispatch_label="Cash-in-transit",
    ),
]

GROUPS_IN_ORDER = [
    "Manned guarding",
    "Sector security",
    "Protection & investigation",
    "K-9",
    "Electronic security",
    "Training & safety",
    "Cash services",
]

# Groups whose copy came from the company's own published pages, versus the
# lines the company supplied for this site and has not published yet.
PUBLISHED_GROUPS = {"Manned guarding", "K-9", "Electronic security", "Training & safety", "Cash services"}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def dispatch_href(service: dict) -> str:
    label = esc(service["dispatch_label"]).replace(" ", "%20")
    return f"index.html?service={service['dispatch']}&amp;label={label}#dispatch"


def source_element(service: dict) -> str:
    """A link back to the published page, or an honest label when there is none."""
    if service.get("source"):
        return (
            f'<a class="service-source" href="{service["source"]}" rel="noopener">Source page '
            '<svg class="icon" aria-hidden="true"><use href="#i-up-right"/></svg></a>'
        )
    return f'<span class="service-source service-source--local">{LOCAL_ONLY}</span>'


def render_block(service: dict, position: int, total: int) -> str:
    paragraphs = "\n              ".join(f"<p>{p}</p>" for p in service["paragraphs"])
    points = "\n                ".join(f"<li>{p}</li>" for p in service["points"])
    if service["note"] == CONCEPT_NOTE:
        note_class = "service-media-note service-media-note--concept"
    elif service["note"] == CLIENT_NOTE:
        note_class = "service-media-note service-media-note--client"
    else:
        note_class = "service-media-note"
    return f'''          <article class="service-block" id="{service["slug"]}">
            <div class="service-block-media">
              <img src="{service["image"]}" alt="{esc(service["alt"])}" loading="lazy" decoding="async">
              <span class="service-block-index">{position:02d} / {total:02d}</span>
              <span class="{note_class}">{service["note"]}</span>
            </div>
            <div class="service-block-body">
              <p class="eyebrow">{esc(service["group"].upper())}</p>
              <h2>{service["name"]}</h2>
              <p class="service-block-summary">{service["summary"]}</p>
              <div class="service-block-copy">
              {paragraphs}
              </div>
              <ul class="service-points">
                {points}
              </ul>
              <div class="service-block-actions">
                <a class="button button--red" href="{dispatch_href(service)}">Request this service <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>
                {source_element(service)}
              </div>
            </div>
          </article>'''


def render_overview() -> str:
    """A thumbnail index of every line, so the catalogue opens on pictures.

    The jump chips above handle navigation; this grid is the visual contents
    page - one photograph, the group and the name per line, each linking to its
    own block. It is generated from the same SERVICES list, so a line cannot be
    in one and missing from the other.
    """
    cards = []
    for index, service in enumerate(SERVICES, start=1):
        image = service["image"]
        card = ROOT / "assets/images/cards" / f"{service['slug']}.webp"
        thumb = (
            f"assets/images/cards/{service['slug']}.webp"
            if card.exists()
            else image.replace("/full/", "/thumbs/") if "/full/" in image else image
        )
        meta = "SUPPLIED FOR THIS SITE" if not service.get("source") else "PUBLISHED SERVICE"
        cards.append(
            '            <li class="svc-index-card">\n'
            f'              <a href="#{service["slug"]}">\n'
            f'                <span class="svc-index-media"><img src="{thumb}" alt="{esc(service["alt"])}" loading="lazy" decoding="async"><span class="svc-index-number">{index:02d}</span></span>\n'
            f'                <span class="svc-index-text"><span class="svc-index-group">{esc(service["group"].upper())}</span><strong>{service["name"]}</strong><span class="svc-index-note">{meta}</span></span>\n'
            '              </a>\n'
            '            </li>'
        )
    total = len(SERVICES)
    return (
        '        <div class="svc-index reveal">\n'
        '          <div class="svc-index-head">\n'
        '            <p class="eyebrow">THE CATALOGUE AT A GLANCE</p>\n'
        '            <h2>Every line,<br>photographed.</h2>\n'
        f'            <p>All {total} service lines in one grid. Select a photograph to open that line\'s full brief, its inclusions and its request button below.</p>\n'
        '            <p class="svc-index-key"><span></span> Published on vonletsecurity.co.zw <span></span> Supplied for this site</p>\n'
        '          </div>\n'
        '          <ul class="svc-index-grid">\n'
        + "\n".join(cards)
        + '\n          </ul>\n'
        '        </div>\n'
    )


def main() -> None:
    index = INDEX.read_text(encoding="utf-8")
    head_end = index.index("</head>") + len("</head>")
    head = index[:head_end]

    # The landing page title has changed more than once; match the <title> and
    # the two social/SEO strings by pattern so this build never silently keeps
    # the home-page metadata on the services page.
    head = re.sub(
        r"<title>.*?</title>",
        "<title>All Twenty-Three Service Lines — Guards, Bank &amp; ATM, Farms &amp; Mines, Escorts | Vonlet Security</title>",
        head,
        count=1,
    )
    head = re.sub(
        r'<meta name="description" content="[^"]*">',
        '<meta name="description" content="Every Vonlet service line on one page: armed and unarmed guards, bank and ATM, warehouse, retail, farms and mines, residential, functions, private escorts and investigations, undercover guards, K-9, CCTV, access control, alarms, rapid response, guard monitoring, training and cash-in-transit.">',
        head,
        count=1,
    )
    head = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        '<meta property="og:title" content="Vonlet Security — All Twenty-Three Service Lines">',
        head,
        count=1,
    )
    head = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        '<meta property="og:description" content="The complete Vonlet service catalogue: guarding by sector, close protection and investigations, K-9, electronic security, training and cash-in-transit — described from the company\'s own information.">',
        head,
        count=1,
    )
    head = re.sub(
        r'\s*<link rel="preload" href="assets/images/full/[^"]+" as="image" fetchpriority="high">',
        "",
        head,
        count=1,
    )

    body_open = index.index("<body>")
    main_open = index.index('<main id="main">') + len('<main id="main">')
    shell = index[body_open:main_open]

    for anchor in ("home", "gallery", "fleet", "services", "about", "estimator", "dispatch", "cash-in-transit"):
        shell = shell.replace(f'href="#{anchor}"', f'href="index.html#{anchor}"')

    # This page is the services page: mark it current and point every service
    # link at itself rather than back at the landing-page overview.
    shell = shell.replace(
        '<a class="nav-link is-active" href="index.html#home">Home</a>',
        '<a class="nav-link" href="index.html#home">Home</a>',
    )
    shell = shell.replace(
        '<a class="nav-link" href="index.html#services">Services</a>',
        '<a class="nav-link is-active" href="services.html" aria-current="page">Services</a>',
    )
    shell = shell.replace(
        '<a href="index.html#services"><span>02</span> Services',
        '<a href="services.html"><span>02</span> Services',
    )
    shell = shell.replace(
        '<a href="index.html#services">Services <svg',
        '<a href="services.html">Services <svg',
    )

    main_close = index.index("</main>")
    tail = index[main_close:]
    tail = re.sub(
        r'href="#(home|gallery|fleet|services|about|estimator|dispatch|cash-in-transit)"',
        r'href="index.html#\1"',
        tail,
    )
    tail = tail.replace(
        '<a href="index.html#services">Our services</a>',
        '<a href="services.html">All twenty-three service lines</a>',
    )
    tail = tail.replace(
        '<a href="index.html#services">Armed &amp; unarmed guards</a><a href="index.html#services">K-9 services</a><a href="index.html#services">Electronic security</a><a href="index.html#services">Cash-in-transit</a><a href="https://vonletsecurity.co.zw/services/" rel="noopener">All services on vonletsecurity.co.zw</a>',
        '<a href="services.html#armed-guards">Armed &amp; unarmed guards</a><a href="services.html#dog-services">K-9 services</a><a href="services.html#close-circuit-television-cctv">Electronic security</a><a href="services.html#cash-in-transit">Cash-in-transit</a><a href="services.html">All twenty-three service lines</a>',
    )
    tail = tail.replace(
        '<div class="noscript-note">All 152 archive photographs and the contact details work without JavaScript. Enable JavaScript to use collection filters, full-size previews, the estimator and request preparation.</div>',
        '<div class="noscript-note">All twenty-three service lines, the contact details and the hotline work without JavaScript. Enable JavaScript to filter the archive or prepare a dispatch request.</div>',
    )

    chips = "\n            ".join(
        f'<a href="#{s["slug"]}">{s["name"]}</a>' for s in SERVICES
    )
    group_counts = {g: sum(1 for s in SERVICES if s["group"] == g) for g in GROUPS_IN_ORDER}
    legend = " · ".join(f"{g.upper()} ({group_counts[g]})" for g in GROUPS_IN_ORDER)
    published = sum(1 for s in SERVICES if s["group"] in PUBLISHED_GROUPS)
    supplied = len(SERVICES) - published

    blocks = "\n".join(
        render_block(service, i, len(SERVICES)) for i, service in enumerate(SERVICES, start=1)
    )
    overview = render_overview()

    main = f'''
    <section class="page-hero" aria-labelledby="services-page-title">
      <div class="container">
        <p class="eyebrow"><span class="eyebrow-line"></span> SERVICES / COMPLETE CATALOGUE</p>
        <h1 id="services-page-title">Twenty-three ways<br><span>we protect.</span></h1>
        <p class="page-hero-lead">Every service line Vonlet offers — the {published} it publishes on its own site (fourteen service pages plus cash-in-transit from the home page) and {supplied} sector, close-protection and investigation lines the company gave us directly for this site — described here in full, on this site, without sending you elsewhere. Published blocks link back to the page they came from; supplied blocks say so in their place.</p>
        <ul class="page-hero-stats">
          <li><strong>{len(SERVICES)}</strong><span>SERVICE LINES</span></li>
          <li><strong>{len(GROUPS_IN_ORDER)}</strong><span>GROUPS</span></li>
          <li><strong>2010</strong><span>SERVING SINCE</span></li>
        </ul>
        <div class="page-hero-actions">
          <a class="button button--red" href="index.html#dispatch">Open a dispatch request <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>
          <a class="button button--outline" href="index.html#estimator">Estimate coverage <svg class="icon" aria-hidden="true"><use href="#i-up-right"/></svg></a>
        </div>
      </div>
    </section>

    <section class="section services-page" aria-labelledby="catalogue-title">
      <div class="container">
        <div class="service-jump reveal">
          <p class="eyebrow">JUMP TO A SERVICE</p>
          <nav class="service-jump-links" aria-label="Service lines">
            {chips}
          </nav>
          <p class="service-jump-legend">{legend}</p>
          <p class="service-jump-legend">{published} lines are published on vonletsecurity.co.zw and linked to their source page below; the {supplied} under SECTOR SECURITY and PROTECTION &amp; INVESTIGATION were given to us by the company for this site and are awaiting publication there.</p>
        </div>
        <h2 class="sr-only" id="catalogue-title">The {len(SERVICES)} Vonlet service lines</h2>
{overview}{blocks}
        <div class="service-close reveal">
          <div>
            <p class="eyebrow">NOT SURE WHICH YOU NEED?</p>
            <h2>Start with the risk,<br>not the service.</h2>
            <p>Tell us what you are protecting and the operations desk will assemble the right combination of people, dogs, technology and response.</p>
          </div>
          <div class="service-close-actions">
            <a class="button button--red" href="index.html#dispatch">Open a dispatch request <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>
            <a class="button button--outline" href="index.html#estimator">Build a coverage estimate <svg class="icon" aria-hidden="true"><use href="#i-up-right"/></svg></a>
          </div>
        </div>
      </div>
    </section>
'''

    OUTPUT.write_text(head + shell + main + tail, encoding="utf-8")
    print(f"Rendered services.html with {len(SERVICES)} service lines across {len(GROUPS_IN_ORDER)} groups.")
    for group in GROUPS_IN_ORDER:
        names = [s["name"] for s in SERVICES if s["group"] == group]
        print(f"  {group:<18} {len(names):>2}  {', '.join(names)}")


if __name__ == "__main__":
    main()
