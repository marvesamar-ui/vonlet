#!/usr/bin/env python3
"""Build the landing page's services showcase from the service catalogue.

The landing page used to spend its whole first screen after the hero on text:
six accordion rows, then a list of eight sector links, then a grid of twenty-three
more links. Nothing on that screen showed what any of the services look like,
which is the wrong shape for a company whose evidence is its photographs.

This script replaces it with a thumbnail-first showcase, generated from the same
SERVICES catalogue in tools/build_services.py so the landing page and the
services page cannot drift apart:

  * one lead card, 2x2 in the bento — photograph, group, name, summary, three
    points and two routes in (request a survey / read the full line);
  * every other service line as a thumbnail card — photograph, group, name,
    one-sentence summary, request shortcut;
  * group tabs that filter the grid without a page load (JavaScript), with the
    full grid rendered statically so it is complete without it;
  * a sector strip for the eight lines procurement shops for by sector.

Photographs come from assets/images/full/ with a 640px thumbnail in the srcset,
so a card paints from the small file and the lightbox on services.html can use
the wide one.

Usage:  python3 tools/build_services_gallery.py
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_services import GROUPS_IN_ORDER, SERVICES  # noqa: E402

ARCHIVE_NOTE = "COMPANY ARCHIVE"
CLIENT_NOTE = "ON SITE, NOVEMBER 2026"
CONCEPT_NOTE = "ILLUSTRATIVE CONCEPT"

# The catalogue's long provenance labels, shortened for a card meta line.
PROVENANCE = {
    "FROM THE COMPANY ARCHIVE": ARCHIVE_NOTE,
    "SUPPLIED BY THE CLIENT — SITE FRAME, NOVEMBER 2026": CLIENT_NOTE,
    "ILLUSTRATIVE CONCEPT IMAGE — NOT A COMPANY PHOTOGRAPH": CONCEPT_NOTE,
}

# The card the eye lands on first: the line the company leads with everywhere
# else, and the widest, most legible photograph in the catalogue.
LEAD = "armed-guards"

# Order of the remaining cards. Deliberately mixed: the first two rows after the
# lead are the lines a procurement officer is most often asked for, and the
# training/close-protection lines sit at the end where they read as depth.
CARD_ORDER = [
    "unarmed-guards",
    "bank-and-atm-security",
    "close-circuit-television-cctv",
    "dog-services",
    "cash-in-transit",
    "farms-and-mines-security",
    "warehouse-security",
    "rapid-response-systems",
    "secret-service",
    "retail-security",
    "functions-security",
    "residential-security",
    "access-control-systems",
    "guard-monitoring-systems",
    "intruder-alarm-systems",
    "private-escorts",
    "basic-security-guard-training",
    "private-investigations",
    "dog-handling-training",
    "firearm-handling",
    "first-aid",
    "fire-drill",
]

# Short tab labels per group (the catalogue's own names are used in the legend).
GROUP_TABS = {
    "Manned guarding": "Manned guarding",
    "Sector security": "Sector security",
    "Protection & investigation": "Close protection",
    "K-9": "K-9",
    "Electronic security": "Electronic security",
    "Training & safety": "Training & safety",
    "Cash services": "Cash services",
}

# The eight sector / escort / investigation lines: these have a full block on
# services.html and are the ones procurement actually shops for by sector.
SECTORS = [
    "bank-and-atm-security",
    "warehouse-security",
    "retail-security",
    "farms-and-mines-security",
    "residential-security",
    "functions-security",
    "private-escorts",
    "private-investigations",
]

BY_SLUG = {service["slug"]: service for service in SERVICES}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def request_href(service: dict) -> str:
    label = esc(service["dispatch_label"]).replace(" ", "%20")
    return f"index.html?service={service['dispatch']}&amp;label={label}#dispatch"


def picture(service: dict, sizes: str, loading: str = "lazy", priority: bool = False) -> str:
    """The 16:10 card derivative written by tools/build_card_crops.py.

    Card crops exist because `object-fit: cover` cannot be trusted with the
    company's 3:4 phone portraits: a wide box centre-cropped a standing officer
    at the chest. Each crop is composed once, at the aspect the card uses.
    """
    card = ROOT / "assets/images/cards" / f"{service['slug']}.webp"
    src = f"assets/images/cards/{service['slug']}.webp" if card.exists() else service["image"]
    fetch = ' fetchpriority="high"' if priority else ""
    return (
        f'<img src="{src}" sizes="{sizes}" alt="{esc(service["alt"])}" '
        f'loading="{loading}"{fetch} decoding="async">'
    )


def shape(service: dict) -> str:
    """Portrait frames need a different crop anchor than landscape ones.

    The WhatsApp site frames are 3:4 portraits of a standing officer; a wide
    landscape card would slice them at the chest. Cards carry the shape so the
    CSS can anchor the crop at the head instead of the middle.
    """
    path = ROOT / service["image"]
    try:
        width, height = subprocess.check_output(
            ["identify", "-format", "%w %h", str(path)], text=True
        ).split()
    except (OSError, subprocess.CalledProcessError):
        return "landscape"
    return "portrait" if int(width) / int(height) < 0.95 else "landscape"


def concept_stamp(service: dict) -> str:
    """Only the cash-in-transit art is generated: say so on the card itself."""
    if service["note"] != "ILLUSTRATIVE CONCEPT IMAGE — NOT A COMPANY PHOTOGRAPH":
        return ""
    return '<span class="svc-concept">ILLUSTRATIVE — NOT A COMPANY PHOTOGRAPH</span>'


def lead_card(service: dict) -> str:
    points = "".join(f"<li>{esc(point)}</li>" for point in service["points"][:3])
    return f'''          <article class="svc-card svc-card--lead reveal" data-group="{esc(service["group"])}" data-shape="{shape(service)}">
            <a class="svc-card-media" href="services.html#{service["slug"]}">
              {picture(service, "(min-width: 1080px) 58vw, 92vw", "eager", True)}
              <span class="svc-badge"><span class="svc-badge-dot"></span>{esc(service["group"].upper())}</span>{concept_stamp(service)}
              <span class="svc-open"><svg class="icon" aria-hidden="true"><use href="#i-up-right"/></svg></span>
            </a>
            <div class="svc-card-body">
              <p class="svc-card-meta"><span>01</span> THE LINE EVERY OTHER LINE RESTS ON · {PROVENANCE.get(service["note"], ARCHIVE_NOTE)}</p>
              <h3><a href="services.html#{service["slug"]}">{esc(service["name"])}</a></h3>
              <p class="svc-card-copy">{esc(service["summary"])}</p>
              <ul class="svc-points">{points}</ul>
              <div class="svc-card-actions">
                <a class="button button--red" href="{request_href(service)}">Request a survey <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>
                <a class="text-button" href="services.html#{service["slug"]}">Read the full line <svg class="icon" aria-hidden="true"><use href="#i-up-right"/></svg></a>
              </div>
            </div>
          </article>'''


def card(service: dict, number: int) -> str:
    return f'''          <article class="svc-card reveal" data-group="{esc(service["group"])}" data-shape="{shape(service)}">
            <a class="svc-card-media" href="services.html#{service["slug"]}">
              {picture(service, "(min-width: 1080px) 30vw, (min-width: 720px) 46vw, 92vw")}
              <span class="svc-badge"><span class="svc-badge-dot"></span>{esc(service["group"].upper())}</span>{concept_stamp(service)}
              <span class="svc-open"><svg class="icon" aria-hidden="true"><use href="#i-up-right"/></svg></span>
            </a>
            <div class="svc-card-body">
              <p class="svc-card-meta"><span>{number:02d}</span> {PROVENANCE.get(service["note"], ARCHIVE_NOTE)}</p>
              <h3><a href="services.html#{service["slug"]}">{esc(service["name"])}</a></h3>
              <p class="svc-card-copy">{esc(service["summary"])}</p>
              <div class="svc-card-actions">
                <a class="svc-card-request" href="{request_href(service)}">Request <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>
              </div>
            </div>
          </article>'''


# Short labels for the sector strip: the full line names are longer than a chip.
SECTOR_SHORT = {
    "bank-and-atm-security": "Bank &amp; ATM",
    "warehouse-security": "Warehouse &amp; logistics",
    "retail-security": "Retail",
    "farms-and-mines-security": "Farms &amp; mines",
    "residential-security": "Residential",
    "functions-security": "Functions &amp; events",
    "private-escorts": "Private escorts",
    "private-investigations": "Private investigations",
}


def sector_link(service: dict, number: int) -> str:
    title = SECTOR_SHORT[service["slug"]]
    return (
        f'            <li><a href="services.html#{service["slug"]}">'
        f'<span>{number:02d}</span><strong>{title}</strong>'
        f'<svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a></li>'
    )


def main() -> None:
    known = set(BY_SLUG)
    unknown = [slug for slug in [LEAD, *CARD_ORDER, *SECTORS] if slug not in known]
    if unknown:
        raise SystemExit(f"Unknown service slugs: {sorted(set(unknown))}")
    catalogued = {LEAD, *CARD_ORDER}
    if len(catalogued) != len(SERVICES):
        raise SystemExit(
            f"The showcase must carry every service line: catalogue has {len(SERVICES)}, "
            f"showcase has {len(catalogued)} (missing {sorted(known - catalogued)})"
        )
    missing_images = [s["slug"] for s in SERVICES if not (ROOT / s["image"]).exists()]
    if missing_images:
        raise SystemExit(f"Service images not on disk: {missing_images}")

    lead = BY_SLUG[LEAD]
    cards = "\n".join(card(BY_SLUG[slug], number) for number, slug in enumerate(CARD_ORDER, start=2))
    sectors = "\n".join(sector_link(BY_SLUG[slug], number) for number, slug in enumerate(SECTORS, start=1))
    counts = {group: sum(1 for service in SERVICES if service["group"] == group) for group in GROUPS_IN_ORDER}
    tabs = "\n".join(
        f'            <button class="svc-tab" type="button" data-svc-filter="{esc(group)}" aria-pressed="false">{esc(GROUP_TABS[group])} <span>{counts[group]:02d}</span></button>'
        for group in GROUPS_IN_ORDER
    )

    markup = f'''        <div class="svc-toolbar reveal" role="group" aria-label="Filter the service lines by group">
          <div class="svc-tabs" data-svc-tabs role="group" aria-label="Service groups">
            <button class="svc-tab is-active" type="button" data-svc-filter="all" aria-pressed="true">All services <span>{len(SERVICES):02d}</span></button>
{tabs}
          </div>
          <p class="svc-toolbar-note"><svg class="icon" aria-hidden="true"><use href="#i-info"/></svg> Every photograph is from the company archive or supplied by the company for this site.</p>
        </div>
        <p class="sr-only" id="svc-status" role="status" aria-live="polite">Showing all {len(SERVICES)} service lines.</p>

        <div class="svc-grid" data-svc-grid>
{lead_card(lead)}
{cards}
          <article class="svc-card svc-card--cta reveal">
            <div class="svc-card-body">
              <p class="svc-card-meta"><span>23</span> COMPLETE CATALOGUE</p>
              <h3>Every line, in full.</h3>
              <p class="svc-card-copy">What each line covers, what is included, and a request button beside it — on one page, without sending you elsewhere.</p>
              <div class="svc-card-actions">
                <a class="button button--outline" href="services.html">Read all {len(SERVICES)} lines <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>
              </div>
            </div>
          </article>
        </div>

        <div class="svc-sectors reveal">
          <div class="svc-sectors-head">
            <p class="eyebrow">SECTOR DEPLOYMENTS<span class="service-sectors-tag">{len(SECTORS)} DIRECT LINES</span></p>
            <h3>Hired by the site,<br>not by the hour.</h3>
            <p>A bank wants its ATM covered. A warehouse wants its gate and its load. A farm wants its boundary walked. These eight lines carry their own photograph, their own brief and their own request button on the services page.</p>
            <a class="button button--outline" href="services.html">Open the service catalogue <svg class="icon" aria-hidden="true"><use href="#i-arrow"/></svg></a>
          </div>
          <ul class="svc-sectors-grid">
{sectors}
          </ul>
        </div>'''

    source = INDEX.read_text(encoding="utf-8")
    source, replaced = re.subn(
        r"(<!-- SERVICES:START -->).*?(<!-- SERVICES:END -->)",
        lambda match: f"{match.group(1)}\n{markup}\n        {match.group(2)}",
        source,
        flags=re.S,
    )
    if not replaced:
        raise SystemExit("SERVICES:START / SERVICES:END markers not found in index.html")
    INDEX.write_text(source, encoding="utf-8")
    print(f"Wrote services showcase: 1 lead card, {len(CARD_ORDER)} thumbnail cards, {len(SECTORS)} sector links, {len(GROUPS_IN_ORDER)} filter tabs.")


if __name__ == "__main__":
    main()
