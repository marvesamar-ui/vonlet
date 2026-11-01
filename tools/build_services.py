#!/usr/bin/env python3
"""Build services.html: all fifteen Vonlet service lines on the local site.

Every service below was taken from the company's live site — the services index,
the fourteen individual /service/... pages and the cash-in-transit block on the
home page — and rewritten into the local page's voice. The slug and the
"Source" link on each block point back at the page it came from, so the copy can
be audited against the original at any time.

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
# `note` is shown under the photograph; only the cash-in-transit image is not a
# company photograph.
# ---------------------------------------------------------------------------
ARCHIVE_NOTE = "FROM THE COMPANY ARCHIVE"
CONCEPT_NOTE = "ILLUSTRATIVE CONCEPT IMAGE — NOT A COMPANY PHOTOGRAPH"

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
        image="assets/images/full/IMG_9325.webp",
        alt="Vonlet guard at a site entrance speaking with a visitor",
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
        image="assets/images/full/IMG_9409.webp",
        alt="Vonlet officer in a blue suit standing beside a bank ATM",
        note=ARCHIVE_NOTE,
        source=f"{SITE}/service/secret-service/",
        dispatch="secret",
        dispatch_label="Undercover guards",
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
        image="assets/images/full/IMG_9295.webp",
        alt="Uniformed Vonlet handler with a service dog in front of a company vehicle",
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
        image="assets/images/full/IMG_9296.webp",
        alt="Vonlet handler posing with a service dog beside a branded car",
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
        image="assets/images/full/IMG_9323.webp",
        alt="Uniformed Vonlet guard taking a visitor's details at a gate",
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
        image="assets/images/full/IMG_9319.webp",
        alt="Two Vonlet officers standing at the company pickup",
        note=ARCHIVE_NOTE,
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
        ],
        points=[
            "Fire extinguisher checks",
            "Corridors cleared of obstructions",
            "Exit doors kept accessible",
            "Faster, safer evacuation",
        ],
        image="assets/images/full/IMG_9273.webp",
        alt="Facilitator presenting a whiteboard strategy map to seated Vonlet staff",
        note=ARCHIVE_NOTE,
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
        ],
        points=[
            "Immediate casualty care",
            "Delivered inside basic guard training",
            "Taught alongside fire drill and firearm handling",
        ],
        image="assets/images/full/IMG_9269.webp",
        alt="Facilitator coaching two Vonlet staff at a training table",
        note=ARCHIVE_NOTE,
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
        image="assets/images/full/IMG_9270.webp",
        alt="Facilitator writing on a whiteboard headed Introduction to Business Strategy and Planning",
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
        image="assets/images/full/IMG_9309.webp",
        alt="Vonlet supervisor with two officers in body armour beside a pickup",
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
            "Vonlet publishes CIT as a core service on its home page rather than as one of the fourteen individual service pages, which is why it completes the fifteen service lines here.",
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

GROUPS_IN_ORDER = ["Manned guarding", "K-9", "Electronic security", "Training & safety", "Cash services"]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def dispatch_href(service: dict) -> str:
    label = esc(service["dispatch_label"]).replace(" ", "%20")
    return f"index.html?service={service['dispatch']}&amp;label={label}#dispatch"


def render_block(service: dict, position: int) -> str:
    paragraphs = "\n              ".join(f"<p>{p}</p>" for p in service["paragraphs"])
    points = "\n                ".join(f"<li>{p}</li>" for p in service["points"])
    note_class = "service-media-note service-media-note--concept" if service["note"] == CONCEPT_NOTE else "service-media-note"
    return f'''          <article class="service-block" id="{service["slug"]}">
            <div class="service-block-media">
              <img src="{service["image"]}" alt="{esc(service["alt"])}" loading="lazy" decoding="async">
              <span class="service-block-index">{position:02d} / 15</span>
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
                <a class="service-source" href="{service["source"]}" rel="noopener">Source page <svg class="icon" aria-hidden="true"><use href="#i-up-right"/></svg></a>
              </div>
            </div>
          </article>'''


def main() -> None:
    index = INDEX.read_text(encoding="utf-8")
    head_end = index.index("</head>") + len("</head>")
    head = index[:head_end]

    head = head.replace(
        "<title>Vonlet Security — Guarding, K-9 and Electronic Security in Zimbabwe &amp; Zambia</title>",
        "<title>All Fifteen Service Lines — Armed Guards, K-9, CCTV, Training | Vonlet Security</title>",
    )
    head = re.sub(
        r'<meta name="description" content="[^"]*">',
        '<meta name="description" content="Every Vonlet service line on one page: armed and unarmed guards, undercover guards, K-9 services and dog handling, CCTV, access control, intruder alarms, rapid response, guard monitoring, fire drill, first aid, guard and firearm training, and cash-in-transit.">',
        head,
        count=1,
    )
    head = head.replace(
        '<meta property="og:title" content="Vonlet Security — People. Technology. Response.">',
        '<meta property="og:title" content="Vonlet Security — All Fifteen Service Lines">',
    )
    head = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        '<meta property="og:description" content="The complete Vonlet service catalogue: guarding, K-9, electronic security, training and cash-in-transit, each described from the company\'s own published information.">',
        head,
        count=1,
    )
    head = head.replace('<link rel="preload" href="assets/images/full/IMG_9309.webp" as="image" fetchpriority="high">\n', "")

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
        '<a href="index.html#services"><span>04</span> Services',
        '<a href="services.html"><span>04</span> Services',
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
        '<a href="services.html">All fifteen service lines</a>',
    )
    tail = tail.replace(
        '<a href="index.html#services">Armed &amp; unarmed guards</a><a href="index.html#services">K-9 services</a><a href="index.html#services">Electronic security</a><a href="index.html#services">Cash-in-transit</a><a href="https://vonletsecurity.co.zw/services/" rel="noopener">All services on vonletsecurity.co.zw</a>',
        '<a href="services.html#armed-guards">Armed &amp; unarmed guards</a><a href="services.html#dog-services">K-9 services</a><a href="services.html#close-circuit-television-cctv">Electronic security</a><a href="services.html#cash-in-transit">Cash-in-transit</a><a href="services.html">All fifteen service lines</a>',
    )
    tail = tail.replace(
        '<div class="noscript-note">All 152 archive photographs and the contact details work without JavaScript. Enable JavaScript to use collection filters, full-size previews, the estimator and request preparation.</div>',
        '<div class="noscript-note">All fifteen service lines, the contact details and the hotline work without JavaScript. Enable JavaScript to filter the archive or prepare a dispatch request.</div>',
    )

    chips = "\n            ".join(
        f'<a href="#{s["slug"]}">{s["name"]}</a>' for s in SERVICES
    )
    group_counts = {g: sum(1 for s in SERVICES if s["group"] == g) for g in GROUPS_IN_ORDER}
    legend = " · ".join(f"{g.upper()} ({group_counts[g]})" for g in GROUPS_IN_ORDER)

    blocks = "\n".join(render_block(service, i) for i, service in enumerate(SERVICES, start=1))

    main = f'''
    <section class="page-hero" aria-labelledby="services-page-title">
      <div class="container">
        <p class="eyebrow"><span class="eyebrow-line"></span> SERVICES / COMPLETE CATALOGUE</p>
        <h1 id="services-page-title">Fifteen ways<br><span>we protect.</span></h1>
        <p class="page-hero-lead">Every service line Vonlet publishes — the fourteen on the company's service pages plus cash-in-transit from its home page — described here in full, on this site, without sending you elsewhere. Each block links back to the page it came from so you can check it against the original.</p>
        <ul class="page-hero-stats">
          <li><strong>15</strong><span>SERVICE LINES</span></li>
          <li><strong>5</strong><span>GROUPS</span></li>
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
        </div>
        <h2 class="sr-only" id="catalogue-title">The fifteen Vonlet service lines</h2>
{blocks}
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
