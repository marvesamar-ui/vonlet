/* ==========================================================================
   Vonlet Security — vanilla ES6 interactions
   Modules: navigation, ticker, gallery, lightbox, counters, estimator,
   contact validation, information dialogs and scroll UI.
   ========================================================================== */
(() => {
  "use strict";

  document.documentElement.classList.add("js");

  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));
  const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const prefersReducedMotion = () => motionQuery.matches;
  const pad = (value) => String(value).padStart(2, "0");
  const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  const scrollBehavior = () => (prefersReducedMotion() ? "auto" : "smooth");

  /* ---------- Shared overlay / focus utilities ---------- */
  let overlayCount = 0;
  const lockScroll = () => {
    overlayCount += 1;
    document.documentElement.classList.add("has-overlay");
  };
  const unlockScroll = () => {
    overlayCount = Math.max(0, overlayCount - 1);
    if (overlayCount === 0) document.documentElement.classList.remove("has-overlay");
  };
  const focusableSelector = [
    "a[href]", "button:not([disabled])", "input:not([disabled])", "select:not([disabled])",
    "textarea:not([disabled])", "summary", '[tabindex]:not([tabindex="-1"])'
  ].join(",");

  function trapFocus(dialog, event) {
    if (event.key !== "Tab") return;
    const items = $$(focusableSelector, dialog).filter((el) => el.getClientRects().length > 0 && !el.hidden);
    if (!items.length) { event.preventDefault(); return; }
    const first = items[0];
    const last = items[items.length - 1];
    const active = document.activeElement;
    if (event.shiftKey && (active === first || !dialog.contains(active))) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && (active === last || !dialog.contains(active))) {
      event.preventDefault(); first.focus();
    }
  }

  function isBackdropClick(dialog, event) {
    if (event.target !== dialog) return false;
    const rect = dialog.getBoundingClientRect();
    return event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom;
  }

  function openDialog(dialog, trigger) {
    if (dialog.open) return;
    dialog.__trigger = trigger || document.activeElement;
    dialog.__restoreFocus = true;
    dialog.showModal();
    lockScroll();
    const initial = $("[data-autofocus]", dialog) || $("button", dialog) || dialog;
    initial.focus({ preventScroll: true });
  }

  function closeDialog(dialog, restoreFocus = true) {
    if (!dialog.open) return;
    dialog.__restoreFocus = restoreFocus;
    dialog.close();
  }

  function wireDialog(dialog, onClose) {
    dialog.addEventListener("cancel", (event) => { event.preventDefault(); closeDialog(dialog); });
    dialog.addEventListener("click", (event) => { if (isBackdropClick(dialog, event)) closeDialog(dialog); });
    dialog.addEventListener("keydown", (event) => trapFocus(dialog, event));
    dialog.addEventListener("close", () => {
      unlockScroll();
      if (typeof onClose === "function") onClose();
      if (dialog.__restoreFocus && dialog.__trigger && document.contains(dialog.__trigger)) {
        dialog.__trigger.focus({ preventScroll: true });
      }
    });
  }

  function navigateToSection(id, focusSelector) {
    const target = document.getElementById(id);
    if (!target) return;
    if (window.history && window.history.pushState) window.history.pushState(null, "", `#${id}`);
    target.scrollIntoView({ behavior: scrollBehavior(), block: "start" });
    const focusTarget = focusSelector ? $(focusSelector) : target;
    if (focusTarget) {
      if (!focusTarget.hasAttribute("tabindex") && !/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(focusTarget.tagName)) {
        focusTarget.setAttribute("tabindex", "-1");
      }
      window.setTimeout(() => focusTarget.focus({ preventScroll: true }), prefersReducedMotion() ? 0 : 420);
    }
  }

  let toastTimer;
  function showToast(message) {
    const toast = $("#toast");
    if (!toast) return;
    window.clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add("is-visible");
    toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 3400);
  }

  async function copyText(text, successMessage) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const area = document.createElement("textarea");
        area.value = text;
        area.setAttribute("readonly", "");
        area.style.cssText = "position:fixed;left:-9999px;top:0;opacity:0;";
        document.body.appendChild(area);
        area.select();
        const ok = document.execCommand("copy");
        area.remove();
        if (!ok) throw new Error("Copy command unavailable");
      }
      showToast(successMessage);
    } catch (error) {
      showToast("Copy is unavailable in this browser. Please select and copy the text manually.");
    }
  }

  /* ---------- Sticky header, mobile drawer & active navigation ---------- */
  function initNavigation() {
    const header = $("#site-header");
    const toggle = $("#menu-toggle");
    const drawer = $("#mobile-menu");
    const closeBtn = $("#drawer-close");
    if (!header || !toggle || !drawer) return;

    const setDrawer = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
      if (open) openDialog(drawer, toggle); else closeDialog(drawer);
    };

    toggle.addEventListener("click", () => setDrawer(drawer.open === false));
    closeBtn.addEventListener("click", () => setDrawer(false));
    wireDialog(drawer, () => {
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open navigation menu");
    });

    $$('a[href^="#"]', drawer).forEach((link) => {
      link.addEventListener("click", (event) => {
        const id = link.getAttribute("href").slice(1);
        if (!document.getElementById(id)) return;
        event.preventDefault();
        closeDialog(drawer, false);
        navigateToSection(id);
      });
    });

    const navLinks = $$(".desktop-nav .nav-link");
    const sectionIds = navLinks.map((link) => link.getAttribute("href").slice(1));
    const sections = sectionIds.map((id) => document.getElementById(id)).filter(Boolean);
    if ("IntersectionObserver" in window && sections.length) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          navLinks.forEach((link) => {
            const active = link.getAttribute("href") === `#${entry.target.id}`;
            link.classList.toggle("is-active", active);
            if (active) link.setAttribute("aria-current", "location");
            else link.removeAttribute("aria-current");
          });
        });
      }, { rootMargin: "-18% 0px -62% 0px", threshold: 0 });
      sections.forEach((section) => observer.observe(section));
    }
  }

  /* ---------- Operations ticker ---------- */
  function initTicker() {
    const track = $("#ticker-track");
    const button = $("#ticker-pause");
    if (!track || !button) return;
    const icon = $("use", button);
    const setState = (paused) => {
      track.classList.toggle("is-paused", paused);
      button.setAttribute("aria-pressed", String(paused));
      button.setAttribute("aria-label", paused ? "Play operations reel" : "Pause operations reel");
      if (icon) icon.setAttribute("href", paused ? "#i-play" : "#i-pause");
    };
    setState(prefersReducedMotion());
    button.addEventListener("click", () => setState(!track.classList.contains("is-paused")));
    if (typeof motionQuery.addEventListener === "function") {
      motionQuery.addEventListener("change", () => setState(prefersReducedMotion()));
    }
  }

  /* ---------- Gallery filtering ---------- */
  function readCard(card, group) {
    const image = $("img", card);
    const categoryNode = $(".mission-category", card);
    return {
      card,
      group: card.dataset.group || group,
      title: card.dataset.title || "Operation",
      brief: card.dataset.brief || "",
      equipment: (card.dataset.equipment || "").split("|").filter(Boolean),
      service: card.dataset.service || "integrated",
      kind: card.dataset.kind || "Showcase imagery",
      category: categoryNode ? categoryNode.textContent.trim() : "FLEET & TECHNOLOGY",
      image: card.dataset.full || (image ? (image.currentSrc || image.src) : ""),
      alt: image ? image.alt : ""
    };
  }

  function initGallery(onOpen) {
    const grid = $("#gallery-grid");
    if (!grid) return; // pages without an archive grid (services.html)
    const cards = $$(".mission-card", grid);
    const buttons = $$(".filter-tab");
    const status = $("#gallery-status");
    const count = $("#gallery-count");
    const items = cards.map((card) => readCard(card, "operations"));
    let visibleItems = items.slice();

    const collectionCount = items.length;
    const collectionTotal = new Set(items.map((item) => item.category)).size;

    cards.forEach((card, index) => {
      const button = $(".mission-open", card);
      button.addEventListener("click", () => onOpen(visibleItems, visibleItems.indexOf(items[index]), button));
    });

    function applyFilter(filter) {
      visibleItems = [];
      cards.forEach((card, index) => {
        const match = filter === "all" || card.dataset.category === filter;
        card.hidden = !match;
        if (match) {
          visibleItems.push(items[index]);
          card.classList.add("is-visible");
          // Only animate the first rows; a 150+ card archive would otherwise queue seconds of motion.
          if (!prefersReducedMotion() && typeof card.animate === "function" && visibleItems.length <= 12) {
            card.getAnimations().forEach((animation) => animation.cancel());
            card.animate(
              [{ opacity: 0, transform: "translateY(12px) scale(.985)" }, { opacity: 1, transform: "translateY(0) scale(1)" }],
              { duration: 320, delay: visibleItems.length * 45, easing: "cubic-bezier(.22,.61,.36,1)", fill: "backwards" }
            );
          }
        }
      });
      grid.classList.toggle("is-filtered", filter !== "all");
      grid.classList.toggle("is-single", visibleItems.length === 1);
      const activeButton = buttons.find((button) => button.dataset.filter === filter);
      const label = filter === "all" ? "archive" : activeButton.firstChild.textContent.trim();
      status.textContent = filter === "all"
        ? `Showing all ${visibleItems.length} photographs from the company archive.`
        : `Showing ${visibleItems.length} photograph${visibleItems.length === 1 ? "" : "s"} from the ${label} collection.`;
      const collections = filter === "all" ? collectionTotal : 1;
      count.textContent = `${visibleItems.length} PHOTOGRAPH${visibleItems.length === 1 ? "" : "S"} / ${pad(collections)} COLLECTION${collections === 1 ? "" : "S"}`;
    }

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        buttons.forEach((item) => {
          const active = item === button;
          item.classList.toggle("is-active", active);
          item.setAttribute("aria-pressed", String(active));
        });
        applyFilter(button.dataset.filter);
      });
    });
  }

  /* ---------- Shared lightbox ---------- */
  function createLightbox(onInquire) {
    const dialog = $("#lightbox");
    if (!dialog) return { open: () => {} };
    const image = $("#lightbox-image");
    const category = $("#lightbox-category");
    const title = $("#lightbox-title");
    const brief = $("#lightbox-brief");
    const equipment = $("#lightbox-equipment");
    const source = $("#lightbox-source");
    const counter = $("#lightbox-counter");
    const prev = $("#lightbox-prev");
    const next = $("#lightbox-next");
    const closeBtn = $("#lightbox-close");
    const inquire = $("#lightbox-inquire");
    let items = [];
    let index = 0;

    function render() {
      const item = items[index];
      if (!item) return;
      image.src = item.image;
      image.alt = item.alt;
      category.textContent = item.category;
      title.textContent = item.title;
      brief.textContent = item.brief;
      source.textContent = item.group === "archive"
        ? `${item.kind}. The caption describes what is visible in the frame.`
        : `${item.kind}. Equipment and deployment are confirmed during assessment.`;
      equipment.replaceChildren(...item.equipment.map((label) => {
        const li = document.createElement("li");
        li.textContent = label;
        return li;
      }));
      counter.textContent = `${index + 1} / ${items.length}`;
      [items[(index + 1) % items.length], items[(index - 1 + items.length) % items.length]].forEach((neighbour) => {
        if (!neighbour || neighbour === item) return;
        const preload = new Image();
        preload.src = neighbour.image;
      });
      const multiple = items.length > 1;
      prev.disabled = !multiple;
      next.disabled = !multiple;
      prev.style.visibility = multiple ? "visible" : "hidden";
      next.style.visibility = multiple ? "visible" : "hidden";
    }

    function step(direction) {
      if (items.length < 2) return;
      index = (index + direction + items.length) % items.length;
      render();
    }

    function open(list, startIndex, trigger) {
      items = list;
      index = Math.max(0, Math.min(startIndex, items.length - 1));
      render();
      openDialog(dialog, trigger);
    }

    prev.addEventListener("click", () => step(-1));
    next.addEventListener("click", () => step(1));
    closeBtn.addEventListener("click", () => closeDialog(dialog));
    inquire.addEventListener("click", () => {
      const item = items[index];
      closeDialog(dialog, false);
      if (item) onInquire(item);
    });
    dialog.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft") { event.preventDefault(); step(-1); }
      if (event.key === "ArrowRight") { event.preventDefault(); step(1); }
    });
    wireDialog(dialog);
    return { open };
  }

  /* ---------- Service selection handoff ---------- */
  function selectService(service, label, message) {
    const select = $("#contact-service");
    const chip = $("#selected-service");
    const messageField = $("#contact-message");
    if (select) {
      const hasOption = Array.from(select.options).some((option) => option.value === service);
      select.value = hasOption ? service : "integrated";
      select.dispatchEvent(new Event("change", { bubbles: true }));
    }
    if (chip) {
      chip.hidden = false;
      $("span", chip).textContent = `Requested capability: ${label}`;
    }
    if (messageField && message) {
      const isPlan = message.includes("VONLET SECURITY — SAMPLE SERVICE ESTIMATE");
      if (!messageField.value.trim() || messageField.dataset.generated === "true") {
        messageField.value = message;
      } else if (!messageField.value.includes(message)) {
        messageField.value = `${messageField.value.trim()}\n\n${message}`;
      }
      if (isPlan) messageField.dataset.generated = "true";
      messageField.dispatchEvent(new Event("input", { bubbles: true }));
    }
    showDispatchForm();
  }

  /* ---------- Service showcase filters ----------
     The landing page renders all twenty-three service cards statically so the
     grid is complete without JavaScript. This only narrows what is on screen. */
  function initServiceFilters() {
    const grid = $("[data-svc-grid]");
    const tabs = $$(".svc-tab");
    if (!grid || !tabs.length) return;
    // The closing tile is a route to the catalogue, not a service line: it is
    // shown with "all" and hidden the moment a group is filtered.
    const cards = $$(".svc-card", grid);
    const cta = $(".svc-card--cta", grid);
    const status = $("#svc-status");

    // The lead card spans two columns; the bento only balances when it leads a
    // filtered set, so a filter that matches a single card centres it instead.
    const apply = (filter) => {
      let shown = 0;
      if (cta) cta.hidden = filter !== "all";
      cards.forEach((card) => {
        if (card === cta) return; // handled above
        const match = filter === "all" || card.dataset.group === filter;
        card.hidden = !match;
        if (!match) return;
        shown += 1;
        if (!prefersReducedMotion() && typeof card.animate === "function" && shown <= 9) {
          card.animate(
            [{ opacity: 0, transform: "translateY(10px)" }, { opacity: 1, transform: "none" }],
            { duration: 300, delay: shown * 30, easing: "cubic-bezier(.22,.61,.36,1)", fill: "backwards" }
          );
        }
      });
      grid.classList.toggle("is-filtered", filter !== "all");
      grid.classList.toggle("is-single", shown === 1);
      const total = cards.filter((card) => card !== cta).length;
      if (status) {
        status.textContent = filter === "all"
          ? `Showing all ${total} service lines.`
          : `Showing ${shown} service line${shown === 1 ? "" : "s"} in ${filter}.`;
      }
    };

    const activate = (tab) => {
      tabs.forEach((item) => {
        const active = item === tab;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-pressed", String(active));
        item.tabIndex = active ? 0 : -1;
      });
      apply(tab.dataset.svcFilter);
    };

    tabs.forEach((tab, index) => {
      tab.tabIndex = tab.classList.contains("is-active") ? 0 : -1;
      tab.addEventListener("click", () => activate(tab));
      // Roving arrow keys across the tab row, matching the filter tabs above.
      tab.addEventListener("keydown", (event) => {
        const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
        if (!step) return;
        event.preventDefault();
        const next = tabs[(index + step + tabs.length) % tabs.length];
        next.focus();
        activate(next);
      });
    });
  }

  /* ---------- Animated metrics ---------- */
  function initCounters() {
    const nodes = $$("[data-counter]");
    if (!nodes.length) return;
    const format = (node, value) => {
      const type = node.dataset.counter;
      const suffix = node.dataset.suffix || "";
      if (type === "time") {
        const seconds = Math.round(value);
        return `${pad(Math.floor(seconds / 60))}:${pad(seconds % 60)}`;
      }
      if (type === "decimal") return `${value.toFixed(1)}${suffix}`;
      if (type === "dispatch") return `${Math.round(value)}/7`;
      if (type === "text") return node.dataset.target || "";
      return `${Math.round(value).toLocaleString("en-US")}${suffix}`;
    };
    const run = () => {
      const duration = 1600;
      const start = performance.now();
      const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        nodes.forEach((node) => { node.textContent = format(node, Number(node.dataset.target) * eased); });
        if (progress < 1) window.requestAnimationFrame(tick);
      };
      window.requestAnimationFrame(tick);
    };
    if (prefersReducedMotion() || !("IntersectionObserver" in window)) return;
    // Keep final values in markup until the section is actually viewed.
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        nodes.forEach((node) => { node.textContent = format(node, 0); });
        run();
        obs.disconnect();
      });
    }, { threshold: 0.3 });
    observer.observe(nodes[0].closest(".metrics-grid"));
  }

  /* ---------- Live service estimator ---------- */
  function initEstimator() {
    const form = $("#estimator-form");
    if (!form) return;
    const property = $("#property-type");
    const hours = $("#operational-hours");
    const guards = $("#guard-count");
    const guardOutput = $("#guard-output");
    const config = $("#quote-config");
    const personnelNode = $("#quote-personnel");
    const addonsNode = $("#quote-addons");
    const totalNode = $("#quote-total");
    const requestButton = $("#request-plan");
    const copyButton = $("#copy-estimate");

    // Demonstration rates only. Replace with approved tariffs before commercial use.
    const rates = { residential: 420, commercial: 520, industrial: 640, construction: 580, event: 680 };
    const shifts = { day: 1, night: 1.15, full: 1.85 };
    const addonRates = { cctv: 180, k9: 320, monitoring: 120 };
    let current = null;

    function calculate() {
      const count = Math.max(1, Math.min(12, Math.round(Number(guards.value) || 1)));
      guards.value = String(count);
      const progress = ((count - Number(guards.min)) / (Number(guards.max) - Number(guards.min))) * 100;
      guards.style.setProperty("--range-progress", `${progress}%`);
      guardOutput.textContent = `${pad(count)} guard${count === 1 ? "" : "s"}`;

      const selectedAddons = $$('input[name="addon"]:checked', form).map((input) => input.value);
      const personnel = Math.round(count * (rates[property.value] || rates.commercial) * (shifts[hours.value] || 1));
      const addons = selectedAddons.reduce((sum, key) => sum + (addonRates[key] || 0), 0);
      const total = personnel + addons;
      const propertyLabel = property.options[property.selectedIndex].textContent;
      const hoursLabel = hours.options[hours.selectedIndex].textContent;
      const addonLabels = selectedAddons.map((key) => ({ cctv: "CCTV monitoring", k9: "K-9 patrol support", monitoring: "Guard monitoring" }[key]));

      current = { count, propertyLabel, hoursLabel, addonLabels, personnel, addons, total };
      config.textContent = `${propertyLabel} · ${hoursLabel} · ${count} guard${count === 1 ? "" : "s"}`;
      personnelNode.textContent = money.format(personnel);
      addonsNode.textContent = money.format(addons);
      totalNode.innerHTML = `${money.format(total)}<span>/month</span>`;
    }

    function estimateText() {
      if (!current) calculate();
      return [
        "VONLET SECURITY — SAMPLE SERVICE ESTIMATE",
        `Property: ${current.propertyLabel}`,
        `Coverage: ${current.hoursLabel}`,
        `Guard posts: ${current.count}`,
        `Add-ons: ${current.addonLabels.length ? current.addonLabels.join(", ") : "None"}`,
        `Personnel & response: ${money.format(current.personnel)}/month`,
        `Technology & add-ons: ${money.format(current.addons)}/month`,
        `Estimated monthly total: ${money.format(current.total)} USD`,
        "",
        "Planning estimate only. Demonstration rates, not a binding quote. Excludes installation, equipment purchase, VAT and site-specific requirements."
      ].join("\n");
    }

    form.addEventListener("input", calculate);
    form.addEventListener("change", calculate);
    form.addEventListener("submit", (event) => event.preventDefault());
    requestButton.addEventListener("click", () => {
      const message = `Please review this sample coverage plan:\n\n${estimateText()}\n\nSite location and preferred start date: [add details]`;
      selectService("integrated", "Custom coverage plan", message);
      navigateToSection("dispatch", "#contact-name");
      showToast("Your sample plan has been added to the dispatch request.");
    });
    copyButton.addEventListener("click", () => copyText(estimateText(), "Sample estimate copied to clipboard."));
    calculate();
  }

  /* ---------- Dispatch form validation & WhatsApp handoff ---------- */

  // Vonlet's published dispatch line, in international format without "+".
  // wa.me needs the country code and digits only.
  const WHATSAPP_NUMBER = "263772856852";
  const WHATSAPP_TEXT_LIMIT = 1500;
  function showDispatchForm() {
    const form = $("#dispatch-form");
    const ready = $("#request-ready");
    if (form && ready) { form.hidden = false; ready.hidden = true; }
  }

  function initContact() {
    const form = $("#dispatch-form");
    if (!form) return;
    const ready = $("#request-ready");
    const status = $("#form-status");
    const message = $("#contact-message");
    const messageCount = $("#message-count");
    const sendWhatsApp = $("#send-whatsapp");
    const sendEmail = $("#send-email");
    const copyRequest = $("#copy-request");
    const editRequest = $("#edit-request");
    let requestText = "";

    const fields = {
      name: {
        node: $("#contact-name"),
        validate: (value) => value.trim().length >= 2 ? "" : "Enter your full name (at least 2 characters)."
      },
      email: {
        node: $("#contact-email"),
        validate: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim()) ? "" : "Enter a valid email address."
      },
      phone: {
        node: $("#contact-phone"),
        validate: (value) => {
          const trimmed = value.trim();
          if (!trimmed) return "";
          const digits = trimmed.replace(/\D/g, "");
          return /^[+\d\s().-]+$/.test(trimmed) && digits.length >= 7 && digits.length <= 15 ? "" : "Enter a valid phone number, or leave this field empty.";
        }
      },
      service: {
        node: $("#contact-service"),
        validate: (value) => value ? "" : "Select the service you need."
      },
      message: {
        node: message,
        validate: (value) => value.trim().length >= 20 ? "" : "Add a short operational brief (at least 20 characters)."
      },
      consent: {
        node: $("#contact-consent"),
        validate: (_, node) => node.checked ? "" : "Please confirm that we may contact you about this request."
      }
    };

    function setError(key, error) {
      const field = fields[key];
      const errorNode = $(`#${field.node.id}-error`);
      field.node.setAttribute("aria-invalid", error ? "true" : "false");
      if (errorNode) errorNode.textContent = error;
      return !error;
    }

    function validateField(key) {
      const field = fields[key];
      return setError(key, field.validate(field.node.value, field.node));
    }

    Object.keys(fields).forEach((key) => {
      const node = fields[key].node;
      node.addEventListener("blur", () => validateField(key));
      node.addEventListener("input", () => {
        if (node.getAttribute("aria-invalid") === "true") validateField(key);
      });
      node.addEventListener("change", () => {
        if (node.getAttribute("aria-invalid") === "true" || node.tagName === "SELECT" || node.type === "checkbox") validateField(key);
      });
    });

    function updateCount() { messageCount.textContent = `${message.value.length} / 3000`; }
    message.addEventListener("input", (event) => {
      updateCount();
      // A real user edit protects the text from being replaced by a later plan handoff.
      if (event.isTrusted && message.dataset.generated === "true") delete message.dataset.generated;
    });
    updateCount();

    function buildRequest() {
      const serviceSelect = fields.service.node;
      const serviceLabel = serviceSelect.options[serviceSelect.selectedIndex].textContent;
      const lines = [
        "VONLET SECURITY — DISPATCH REQUEST",
        "",
        `Name: ${fields.name.node.value.trim()}`,
        `Email: ${fields.email.node.value.trim()}`,
        `Phone: ${fields.phone.node.value.trim() || "Not provided"}`,
        `Service: ${serviceLabel}`,
        "",
        "Operational brief:",
        message.value.trim(),
        "",
        "Consent: I agree to be contacted about this security request."
      ];
      return { serviceLabel, text: lines.join("\n") };
    }

    // wa.me carries the message in the query string, so keep it well inside
    // practical URL limits; very long briefs are trimmed with a pointer back
    // to the copy button, which always carries the full text.
    function whatsappHref(text) {
      let body = text;
      if (body.length > WHATSAPP_TEXT_LIMIT) {
        body = `${body.slice(0, WHATSAPP_TEXT_LIMIT).trimEnd()}\n\n[...brief continues — copy the full request from the Vonlet site]`;
      }
      return `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(body)}`;
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if ($("#contact-website").value) return; // Honeypot: ignore automated submissions.
      const invalid = Object.keys(fields).filter((key) => !validateField(key));
      if (invalid.length) {
        status.textContent = `Please correct ${invalid.length} field${invalid.length === 1 ? "" : "s"} before preparing your request.`;
        fields[invalid[0]].node.focus();
        return;
      }
      const request = buildRequest();
      requestText = request.text;
      const subject = `Security request — ${request.serviceLabel}`;
      const href = whatsappHref(requestText);
      if (sendWhatsApp) sendWhatsApp.href = href;
      if (sendEmail) {
        sendEmail.href = `mailto:info@vonletsecurity.co.zw?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(requestText)}`;
      }
      form.hidden = true;
      ready.hidden = false;
      status.textContent = "Request prepared. Opening WhatsApp with the details filled in.";
      ready.focus({ preventScroll: true });
      ready.scrollIntoView({ behavior: scrollBehavior(), block: "center" });
      // Called directly inside the submit gesture, so the tab is not blocked.
      // window.open() returns null when the noopener flag is requested, so the
      // opener link is severed on the returned handle instead.
      const opened = window.open(href, "_blank");
      if (opened) opened.opener = null;
      if (opened) {
        showToast("WhatsApp opened — press send there to reach the dispatch line.");
      } else {
        status.textContent = "Request prepared. Use Open WhatsApp to send it — your browser blocked the new tab.";
      }
    });

    copyRequest.addEventListener("click", () => copyText(requestText, "Dispatch request copied to clipboard."));
    editRequest.addEventListener("click", () => {
      showDispatchForm();
      fields.name.node.focus({ preventScroll: true });
    });
  }

  /* ---------- Hardware previews ---------- */
  function initHardware(lightbox) {
    const cards = $$(".gear-card");
    const items = cards.map((card) => readCard(card, "hardware"));
    cards.forEach((card, index) => {
      $$(".gear-image, .gear-spec-button", card).forEach((button) => {
        button.addEventListener("click", () => lightbox.open(items, index, button));
      });
    });
  }

  /* ---------- Privacy / licensing dialogs ---------- */
  function initInfoDialogs() {
    const dialog = $("#info-dialog");
    if (!dialog) return;
    const title = $("#info-title");
    const content = $("#info-content");
    const closeBtn = $("#info-close");
    const pages = {
      privacy: {
        title: "Privacy notice",
        html: "<p>This site does not use analytics cookies and does not submit form data to a server. The details you enter stay in the page until you choose to open WhatsApp or copy them.</p><p>Preparing a request hands the text to WhatsApp on your own device: nothing leaves the browser until you press send there, and from that point the message is handled under WhatsApp terms and Vonlet&rsquo;s own policies. Avoid putting access codes, passwords or security vulnerabilities in the operational brief.</p><p>For urgent assistance, call the published hotline instead of using the form.</p>"
      },
      licensing: {
        title: "Licensing & compliance",
        html: "<p>Vonlet Security Services operates in Zimbabwe and Zambia. Current company registration, security operating licences, tax clearance and insurance documents should be verified directly with Vonlet during procurement.</p><p>This showcase does not publish a licence number. Request the current compliance pack before contracting:</p><ul><li>Email: info@vonletsecurity.co.zw</li><li>Hotline: +263 772 856 852</li><li>Head office: 9 Blatherwick Road, Queensdale, Harare</li></ul><p>Armed guarding, cash-in-transit, K-9 deployment and electronic security work remain subject to applicable firearm, transport and site-specific approvals.</p>"
      }
    };
    $$("[data-info-dialog]").forEach((button) => {
      button.addEventListener("click", () => {
        const page = pages[button.dataset.infoDialog];
        if (!page) return;
        title.textContent = page.title;
        content.innerHTML = page.html; // Static, trusted copy only; no user input is interpolated.
        openDialog(dialog, button);
      });
    });
    closeBtn.addEventListener("click", () => closeDialog(dialog));
    wireDialog(dialog);
  }

  /* ---------- Scroll UI & reveal ---------- */
  function initScrollUI() {
    const header = $("#site-header");
    const backToTop = $("#back-to-top");
    let ticking = false;
    const update = () => {
      const y = window.scrollY;
      if (header) header.classList.toggle("is-scrolled", y > 50);
      if (backToTop) backToTop.classList.toggle("is-visible", y > 600);
      ticking = false;
    };
    window.addEventListener("scroll", () => {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();
    if (backToTop) backToTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: scrollBehavior() }));
    const year = $("#copyright-year");
    if (year) year.textContent = String(new Date().getFullYear());
  }

  function initReveal() {
    const nodes = $$(".reveal");
    if (prefersReducedMotion() || !("IntersectionObserver" in window)) {
      nodes.forEach((node) => node.classList.add("is-visible"));
      return;
    }
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        obs.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -30px 0px" });
    nodes.forEach((node) => observer.observe(node));
  }

  /* ---------- Guided assistant ----------
     A scripted intake, not a model. Every reply below is written from this
     site's own pages: nothing is fetched, nothing is sent anywhere, and the
     only thing kept is the thread itself, in this tab's sessionStorage, so it
     survives a jump to the services page. Each path ends in a WhatsApp
     handoff the visitor sends themselves. To teach it a new question, add an
     entry to ASSISTANT_ANSWERS. */
  const ASSISTANT_STORE = "vonlet:assistant";
  const ASSISTANT_SEEN = "vonlet:assistant-seen";
  const ASSISTANT_HOTLINE = "+263772856852";
  const ASSISTANT_HOTLINE_LABEL = "+263 772 856 852";
  const ASSISTANT_EMAIL = "info@vonletsecurity.co.zw";
  const onLandingPage = !/(?:services|archive)\.html$/.test(window.location.pathname);
  // Sections live on the landing page; the other two pages have to cross over.
  const siteHref = (hash) => (onLandingPage ? `#${hash}` : `index.html#${hash}`);

  // What the visitor is protecting. Each answer names the lines that would be
  // scoped for it, and the two written up in full.
  const ASSISTANT_SITES = [
    {
      id: "residence",
      chip: "Home or residence",
      match: ["home", "house", "residential", "residence", "flat", "apartment", "estate", "cottage", "domestic", "durawall"],
      reply: "A home is normally a static post at the gate — unarmed for access control and the register, armed where the risk calls for it — with CCTV, an intruder alarm and a panic link to the response team behind it.",
      links: [
        { href: "services.html#residential-security", label: "Residential security" },
        { href: "services.html#armed-guards", label: "Armed & unarmed guards" }
      ]
    },
    {
      id: "business",
      chip: "Shop, office or bank",
      match: ["shop", "retail", "store", "office", "bank", "branch", "supermarket", "mall", "corporate", "hotel", "restaurant", "clinic", "school"],
      reply: "Customer-facing premises usually run a visible officer at the door and a second post inside, backed by CCTV over the till, the safe or the terminal and access control on the staff doors. Banking and ATM duty is a line of its own.",
      links: [
        { href: "services.html#retail-security", label: "Retail security" },
        { href: "services.html#bank-and-atm-security", label: "Bank & ATM posts" }
      ]
    },
    {
      id: "warehouse",
      chip: "Warehouse or yard",
      match: ["warehouse", "yard", "depot", "storage", "logistics", "factory", "industrial", "plant", "bond"],
      reply: "A warehouse is a gate-and-book problem before it is a patrolling one: an officer on the gate checking loads in and out, patrols through the yard, and cameras covering the loading bays.",
      links: [
        { href: "services.html#warehouse-security", label: "Warehouse security" },
        { href: "services.html#access-control-systems", label: "Access control" }
      ]
    },
    {
      id: "remote",
      chip: "Farm, mine or remote site",
      match: ["farm", "mine", "mining", "remote", "plot", "agricultur", "quarry", "rural", "borehole", "shaft"],
      reply: "Farms and mines are what the electronic side is built for — a long perimeter, approaches you cannot watch from one point, and power or network that cannot be assumed. Guarding, dog patrols and monitoring are scoped together; a single officer on a large boundary is not a plan.",
      links: [
        { href: "services.html#farms-and-mines-security", label: "Farms & mines security" },
        { href: "services.html#dog-services", label: "Dog services" }
      ]
    },
    {
      id: "event",
      chip: "Event or function",
      match: ["event", "function", "wedding", "conference", "concert", "match", "party", "crowd", "festival"],
      reply: "Functions are covered by a short-term team — access control at the entrances, a visible presence in the room, and a response plan agreed with the organisers beforehand.",
      links: [
        { href: "services.html#functions-security", label: "Functions security" }
      ]
    },
    {
      id: "cash",
      chip: "Cash movement",
      match: ["cash", "transit", "convoy", "bullion", "collection", "deposit", "payroll", "armoured", "armored"],
      reply: "Cash-in-transit covers task assignment, route selection and accounting for every book, run by officers in the armoured fleet. It is normally paired with a banking-hall or ATM post at the other end of the run.",
      links: [
        { href: "services.html#cash-in-transit", label: "Cash-in-transit" },
        { href: "services.html#bank-and-atm-security", label: "Bank & ATM posts" }
      ]
    },
    {
      id: "other",
      chip: "Something else",
      match: [],
      reply: "That is fine — the desk scopes from the risk rather than the service name. Describe the site or the problem in a sentence below, or go straight to the request form with what you have.",
      links: []
    }
  ];

  const ASSISTANT_TIMINGS = [
    { label: "Today or tomorrow", match: ["today", "tomorrow", "tonight", "now", "urgent", "asap", "immediately", "emergency"] },
    { label: "This week", match: ["week", "days", "soon", "fortnight"] },
    { label: "Planning ahead", match: ["plan", "planning", "month", "later", "next year", "budget", "considering", "exploring", "no rush", "quote"] }
  ];

  const ASSISTANT_PLACES = [
    { label: "Harare", match: ["harare", "queensdale", "borrowdale", "avondale", "mount pleasant"] },
    { label: "Bulawayo", match: ["bulawayo", "byo"] },
    { label: "Elsewhere in Zimbabwe", match: ["zimbabwe", "gweru", "mutare", "masvingo", "chinhoyi", "kwekwe", "kadoma", "hwange", "vic falls", "elsewhere"] },
    { label: "Zambia", match: ["zambia", "lusaka", "kitwe", "ndola", "livingstone"] }
  ];

  // Free-text questions. Order matters: emergencies and contact come before
  // the service lines, so "I need help now" never answers as a guard inquiry.
  const ASSISTANT_ANSWERS = [
    {
      match: ["emergency", "urgent", "immediately", "right now", "break-in", "break in", "broke in", "intruder", "stolen", "robbery", "robbed", "attack", "attacked", "help now", "help me now"],
      reply: `If something is happening now, do not type — call the 24/7 dispatch line on ${ASSISTANT_HOTLINE_LABEL} and the response team will take it from there. This assistant is scripted and cannot dispatch anyone.`,
      links: [{ href: `tel:${ASSISTANT_HOTLINE}`, label: "Call the hotline now" }]
    },
    {
      match: ["contact", "phone", "number", "call", "whatsapp", "email", "e-mail", "address", "office", "speak", "talk to", "human", "person", "manager", "reach you"],
      reply: `The dispatch line is ${ASSISTANT_HOTLINE_LABEL}, answered 24/7, and ${ASSISTANT_EMAIL} reaches the office at 9 Blatherwick Road, Queensdale, Harare. The contact section of the site has the same details.`,
      links: [
        { href: `tel:${ASSISTANT_HOTLINE}`, label: "Call the hotline" },
        { href: `mailto:${ASSISTANT_EMAIL}`, label: "Email the office" }
      ]
    },
    {
      match: ["price", "pricing", "cost", "how much", "rate", "rates", "quote", "quotation", "estimate", "budget", "cheap", "expensive", "afford"],
      reply: "Rates move with the site, the hours, the officer grade and the equipment, so there is no single figure to give you. The estimator on the home page returns an indicative monthly number in USD and says plainly that it uses demonstration rates; a firm quotation comes from the desk after an assessment.",
      links: [{ href: siteHref("estimator"), label: "Open the estimator" }]
    },
    {
      match: ["where", "cover", "coverage", "area", "areas", "zimbabwe", "zambia", "harare", "bulawayo", "branch", "branches", "operate", "region", "based"],
      reply: "Vonlet operates in Zimbabwe and Zambia. The head office is at 9 Blatherwick Road, Queensdale, Harare, with branches in both countries, and the desk deploys from there.",
      links: [{ href: siteHref("dispatch"), label: "Contact the desk" }]
    },
    {
      match: ["guard", "guards", "guarding", "manned", "static", "patrol", "patrols", "officer", "officers", "sentry", "manned guarding"],
      reply: "Guarding is the core of the service: unarmed officers for access control, registers and visitor handling; armed officers for higher-risk posts; roving patrols and supervisory visits over the top. Every officer is trained before deployment and posted to a written site brief.",
      links: [{ href: "services.html#armed-guards", label: "Armed & unarmed guards" }]
    },
    {
      match: ["dog", "dogs", "k9", "k-9", "canine", "handler", "handlers"],
      reply: "Service dogs and handlers work perimeter sweeps, vehicle and cargo checks, and events. Dog handling is one of the training lines as well, so a client team can be taught to work with a dog properly.",
      links: [
        { href: "services.html#dog-services", label: "Dog services" },
        { href: "services.html#dog-handling-training", label: "Dog handling training" }
      ]
    },
    {
      match: ["cctv", "camera", "cameras", "surveillance", "monitor", "monitoring", "alarm", "alarms", "biometric", "access control", "electric fence", "electronic", "sensor", "sensors"],
      reply: "Electronic security is CCTV, intruder alarms, access control and guard monitoring — specified per site, and normally supplied with the guarding rather than instead of it. Nothing here is sold off a shelf: the camera positions follow the risk.",
      links: [
        { href: "services.html#close-circuit-television-cctv", label: "CCTV" },
        { href: "services.html#intruder-alarm-systems", label: "Alarm systems" },
        { href: "services.html#access-control-systems", label: "Access control" }
      ]
    },
    {
      match: ["rapid", "response", "panic", "backup", "back-up", "back up", "alarm response"],
      reply: "Rapid response is the armed team dispatched when an alarm or panic signal is raised. The response time agreed for a site is part of its assessment, not a claim made on a web page.",
      links: [{ href: "services.html#rapid-response-systems", label: "Rapid response" }]
    },
    {
      match: ["investigat", "escort", "escorts", "vip", "close protection", "bodyguard", "undercover", "secret service", "discreet", "protection"],
      reply: "Close protection, private escorts, undercover posts and investigations sit under the protection line and are kept off the uniformed roster, so they do not read as a guard post.",
      links: [
        { href: "services.html#close-protection", label: "Close protection" },
        { href: "services.html#private-investigations", label: "Investigations" }
      ]
    },
    {
      match: ["training", "train", "course", "courses", "firearm", "fire arm", "first aid", "drill", "certificate", "accredited"],
      reply: "The training side covers basic guard training, firearm handling, first aid, fire drill and dog handling, run for company staff and, by arrangement, for client teams.",
      links: [
        { href: "services.html#basic-security-guard-training", label: "Guard training" },
        { href: "services.html#firearm-handling", label: "Firearm handling" }
      ]
    },
    {
      match: ["licence", "license", "registered", "registration", "legal", "compliant", "compliance", "insurance", "permit", "authorised", "authorized"],
      reply: "Licensing, insurance and compliance documents are not published on this site. Procurement should verify current documents with Vonlet directly — the footer's Licensing & compliance note says the same rather than quoting credentials that cannot be cited here.",
      links: [{ href: `mailto:${ASSISTANT_EMAIL}`, label: "Request the documents" }]
    },
    {
      match: ["hours", "open", "opening", "24", "night", "nights", "weekend", "weekends", "holiday", "always", "around the clock"],
      reply: "The dispatch line runs 24/7, including nights, weekends and public holidays. Office hours for administration and quotations are normal Harare business hours.",
      links: [{ href: `tel:${ASSISTANT_HOTLINE}`, label: "Call the hotline" }]
    },
    {
      match: ["photo", "photos", "archive", "picture", "pictures", "gallery", "frames", "images"],
      reply: "The company archive holds 51 published frames, one per scene, each with the brief it was taken for. The cash-in-transit images are separately labelled as generated concept art, not company photographs.",
      links: [{ href: "archive.html", label: "Open the archive" }]
    },
    {
      match: ["service", "services", "what do you do", "what can you do", "offer", "capabilities", "list", "catalogue", "catalog"],
      reply: "Twenty-three lines in seven groups: guarding by sector, sector security, protection and investigation, K-9, electronic security, training and cash-in-transit. The catalogue page carries every one of them with its brief.",
      links: [{ href: "services.html", label: "All 23 service lines" }]
    },
    {
      match: ["hello", "hi there", "hey", "good day", "good morning", "good afternoon", "good evening", "howzit"],
      reply: "Good day. Ask me about a service line, coverage or how a request works — or tell me what you are protecting and I will narrow it down.",
      links: []
    },
    {
      match: ["thank", "thanks", "cheers", "appreciate", "great", "perfect"],
      reply: "Pleasure. If you would rather speak to someone, the dispatch line is the fastest route — it is answered 24/7.",
      links: [{ href: `tel:${ASSISTANT_HOTLINE}`, label: "Call the hotline" }]
    }
  ];

  function initAssistant() {
    const launcher = $("#assistant-launcher");
    const panel = $("#assistant-panel");
    if (!launcher || !panel) return;
    const log = $("#assistant-log");
    const chipRow = $("#assistant-chips");
    const form = $("#assistant-composer");
    const input = $("#assistant-input");
    const closeButton = $("#assistant-close");
    const barAsk = $("#action-bar-ask");

    const state = { step: "site", site: null, timing: null, place: null, notes: "" };
    let transcript = [];
    let opened = false;
    let lastTrigger = launcher;

    const svgIcon = (id) => {
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("class", "icon");
      svg.setAttribute("aria-hidden", "true");
      const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
      use.setAttribute("href", `#${id}`);
      svg.appendChild(use);
      return svg;
    };

    const persist = () => {
      try {
        sessionStorage.setItem(ASSISTANT_STORE, JSON.stringify({ transcript, state }));
      } catch (error) {
        /* storage can be blocked; the thread then lives only on this page */
      }
    };

    const render = (message) => {
      const row = document.createElement("div");
      row.className = `assistant-msg assistant-msg--${message.role}`;
      const bubble = document.createElement("div");
      bubble.className = "assistant-bubble";
      bubble.textContent = message.text;
      (message.links || []).forEach((link) => {
        const anchor = document.createElement("a");
        anchor.className = "assistant-link";
        anchor.href = link.href;
        if (/^https?:/.test(link.href)) { anchor.target = "_blank"; anchor.rel = "noopener"; }
        anchor.textContent = link.label;
        anchor.appendChild(svgIcon("i-arrow"));
        bubble.appendChild(anchor);
      });
      row.appendChild(bubble);
      log.appendChild(row);
      log.scrollTop = log.scrollHeight;
    };

    const push = (role, text, links) => {
      const message = { role, text, links: links || [] };
      transcript.push(message);
      render(message);
      persist();
    };

    const say = (text, links, after) => {
      const row = document.createElement("div");
      row.className = "assistant-msg assistant-msg--bot";
      const bubble = document.createElement("div");
      bubble.className = "assistant-bubble assistant-bubble--typing";
      bubble.innerHTML = '<span class="assistant-dots" aria-hidden="true"><i></i><i></i><i></i></span>';
      row.appendChild(bubble);
      log.appendChild(row);
      log.scrollTop = log.scrollHeight;
      window.setTimeout(() => {
        row.remove();
        push("bot", text, links);
        if (typeof after === "function") after();
      }, prefersReducedMotion() ? 60 : 420);
    };

    const clearChips = () => { chipRow.innerHTML = ""; };

    const setChips = (items) => {
      clearChips();
      (items || []).forEach((item) => {
        const node = document.createElement(item.href ? "a" : "button");
        node.className = item.primary ? "assistant-chip assistant-chip--primary" : "assistant-chip";
        if (item.href) {
          node.href = item.href;
          if (/^https?:/.test(item.href)) { node.target = "_blank"; node.rel = "noopener"; }
        } else {
          node.type = "button";
          node.addEventListener("click", () => {
            clearChips();
            item.onSelect();
          });
        }
        node.textContent = item.label;
        chipRow.appendChild(node);
      });
    };

    const siteById = (id) => ASSISTANT_SITES.find((site) => site.id === id) || ASSISTANT_SITES[ASSISTANT_SITES.length - 1];
    const whatsappHref = (text) => `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;

    const handoffText = () => [
      "Vonlet Security — website assistant enquiry",
      `Site: ${siteById(state.site).chip}`,
      `Timing: ${state.timing || "Not given"}`,
      `Location: ${state.place || "Not given"}`,
      `Notes: ${state.notes || "Nothing added"}`,
      "",
      "Please advise on cover for this site."
    ].join("\n");

    const handoffChips = () => [
      { label: "Send on WhatsApp", href: whatsappHref(handoffText()), primary: true },
      { label: "Call the hotline", href: `tel:${ASSISTANT_HOTLINE}` },
      { label: "Open the estimator", href: siteHref("estimator") },
      { label: "Start over", onSelect: reset }
    ];

    const followUpChips = () => [
      { label: "Narrow it down for my site", onSelect: askSite },
      { label: "Message the desk", href: whatsappHref("Hello Vonlet — I have a question from the website.") }
    ];

    // One chip set per step, so a thread restored from storage can be re-asked
    // without replaying the questions.
    const chipSets = {
      site: () => ASSISTANT_SITES.map((site) => ({ label: site.chip, onSelect: () => chooseSite(site) })),
      timing: () => ASSISTANT_TIMINGS.map((timing) => ({ label: timing.label, onSelect: () => chooseTiming(timing.label) })),
      place: () => ASSISTANT_PLACES.map((place) => ({ label: place.label, onSelect: () => choosePlace(place.label) })),
      notes: () => [{ label: "Skip — send what I have", onSelect: () => finish("") }],
      done: handoffChips
    };

    const askSite = () => {
      state.step = "site";
      persist();
      setChips(chipSets.site());
    };

    const applyTiming = (label) => {
      state.timing = label;
      state.step = "place";
      persist();
      say("Where is the site? Coverage and the response arrangement are planned per branch.", null, () => setChips(chipSets.place()));
    };

    const applyPlace = (label) => {
      state.place = label;
      state.step = "notes";
      persist();
      say("Last one: anything specific for the desk — access hours, a weak point, an incident you have had? Type it, or skip.", null, () => setChips(chipSets.notes()));
    };

    const finish = (note) => {
      state.notes = note || "";
      state.step = "done";
      persist();
      const site = siteById(state.site);
      const summary = `Noted: ${site.chip.toLowerCase()}, ${(state.timing || "timing to confirm").toLowerCase()}, ${(state.place || "location to confirm").toLowerCase()}.${note ? " Your note goes with it." : ""} Send it to the desk on WhatsApp — the message is written for you, and nothing leaves this page until you press send there.`;
      say(summary, null, () => setChips(chipSets.done()));
    };

    const reset = () => {
      transcript = [];
      state.step = "site";
      state.site = null;
      state.timing = null;
      state.place = null;
      state.notes = "";
      log.innerHTML = "";
      clearChips();
      try { sessionStorage.removeItem(ASSISTANT_STORE); } catch (error) { /* ignore */ }
      greet();
    };

    const greet = () => {
      state.step = "site";
      persist();
      say("Good day. I am the Vonlet assistant — scripted, not a person. Tell me what you are protecting and I will narrow it down, or ask me a question about any service line.", null, () => setChips(chipSets.site()));
    };

    const applySite = (site) => {
      state.site = site.id;
      persist();
      say(site.reply, site.links, () => {
        state.step = "timing";
        persist();
        say("How soon do you need cover? The desk triages on this — an urgent site goes to the duty officer first.", null, () => setChips(chipSets.timing()));
      });
    };

    const chooseSite = (site) => {
      push("user", site.chip);
      applySite(site);
    };

    const chooseTiming = (label) => {
      push("user", label);
      applyTiming(label);
    };

    const choosePlace = (label) => {
      push("user", label);
      applyPlace(label);
    };

    const answerFor = (text) => ASSISTANT_ANSWERS.find((answer) => answer.match.some((needle) => text.includes(needle)));

    const handleInput = (raw) => {
      const value = raw.trim();
      if (!value) return;
      clearChips();
      push("user", value);
      const text = ` ${value.toLowerCase()} `;

      // A typed answer to the question on screen is treated as that answer, so
      // the guided run is not lost the moment someone types instead of tapping.
      if (state.step === "notes") { finish(value); return; }
      if (state.step === "site") {
        const site = ASSISTANT_SITES.find((candidate) => candidate.match.some((needle) => text.includes(needle)));
        if (site) { applySite(site); return; }
      }
      if (state.step === "timing") {
        const timing = ASSISTANT_TIMINGS.find((candidate) => candidate.match.some((needle) => text.includes(needle)));
        if (timing) { applyTiming(timing.label); return; }
      }
      if (state.step === "place") {
        const place = ASSISTANT_PLACES.find((candidate) => candidate.match.some((needle) => text.includes(needle)));
        if (place) { applyPlace(place.label); return; }
      }

      const answer = answerFor(text);
      if (answer) {
        say(answer.reply, answer.links, () => setChips(followUpChips()));
        return;
      }

      say("That one is not on file. The replies here are written from this site's own pages, so I would rather hand you to a person than guess. Put it to the desk on WhatsApp, or run the three questions and it will carry the shape of the job across.", null, () =>
        setChips([
          { label: "Put it to the desk", href: whatsappHref(`Hello Vonlet — a question from the website: ${value}`), primary: true },
          { label: "Call the hotline", href: `tel:${ASSISTANT_HOTLINE}` },
          { label: "Answer three questions", onSelect: askSite }
        ]));
    };

    const setExpanded = (value) => {
      const flag = value ? "true" : "false";
      launcher.setAttribute("aria-expanded", flag);
      if (barAsk) barAsk.setAttribute("aria-expanded", flag);
    };

    const restore = () => {
      let saved = null;
      try { saved = JSON.parse(sessionStorage.getItem(ASSISTANT_STORE) || "null"); } catch (error) { saved = null; }
      if (!saved || !Array.isArray(saved.transcript) || !saved.transcript.length) return false;
      transcript = saved.transcript;
      Object.assign(state, saved.state || {});
      transcript.forEach(render);
      return true;
    };

    const open = (trigger) => {
      if (opened) return;
      opened = true;
      lastTrigger = trigger || launcher;
      panel.hidden = false;
      panel.classList.add("is-open");
      setExpanded(true);
      try { sessionStorage.setItem(ASSISTANT_SEEN, "1"); } catch (error) { /* ignore */ }
      if (!transcript.length && !restore()) {
        greet();
      } else {
        setChips((chipSets[state.step] || chipSets.site)());
      }
      window.setTimeout(() => input.focus({ preventScroll: true }), 80);
    };

    const close = (restoreFocus = true) => {
      if (!opened) return;
      opened = false;
      panel.hidden = true;
      panel.classList.remove("is-open");
      setExpanded(false);
      if (restoreFocus && lastTrigger && document.contains(lastTrigger)) lastTrigger.focus({ preventScroll: true });
    };

    launcher.addEventListener("click", () => (opened ? close() : open(launcher)));
    if (barAsk) barAsk.addEventListener("click", () => (opened ? close() : open(barAsk)));
    if (closeButton) closeButton.addEventListener("click", () => close());
    panel.addEventListener("keydown", (event) => {
      if (event.key === "Escape") { event.stopPropagation(); close(); }
    });
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const value = input.value;
      input.value = "";
      handleInput(value);
    });

    // The launcher shows a short "starting" state first, once per tab.
    let seen = false;
    try { seen = sessionStorage.getItem(ASSISTANT_SEEN) === "1"; } catch (error) { seen = false; }
    const ready = () => {
      launcher.dataset.state = "ready";
      launcher.removeAttribute("aria-busy");
    };
    if (seen || prefersReducedMotion()) ready();
    else window.setTimeout(ready, 1500);
  }

  /* ---------- Boot ---------- */
  function restorePendingRequest() {
    let pending = null;
    try {
      pending = JSON.parse(sessionStorage.getItem("vonlet:request") || "null");
      if (pending) sessionStorage.removeItem("vonlet:request");
    } catch (error) {
      return;
    }
    if (!pending || !$("#contact-service")) return;
    selectService(pending.service || "integrated", pending.title || "Security services", pending.message || "");
    window.setTimeout(() => navigateToSection("dispatch", "#contact-name"), 120);
  }

  // A service page links here as index.html?service=cit&label=Cash-in-transit#dispatch.
  function applyServiceFromQuery() {
    if (!$("#contact-service")) return;
    const params = new URLSearchParams(window.location.search);
    const service = params.get("service");
    if (!service) return;
    const label = params.get("label") || "Security services";
    selectService(service, label, `I'm interested in ${label}. Please advise on options for my site.`);
    window.setTimeout(() => navigateToSection("dispatch", "#contact-name"), 120);
  }

  function init() {
    restorePendingRequest();
    applyServiceFromQuery();
    initNavigation();
    initTicker();
    initScrollUI();
    initReveal();
    initCounters();
    initEstimator();
    initContact();
    initInfoDialogs();
    initServiceFilters();
    initAssistant();

    const lightbox = createLightbox((item) => {
      const message = `I'm interested in ${item.title}. Please advise on options for my site.`;
      if ($("#contact-service")) {
        selectService(item.service, item.title, message);
        navigateToSection("dispatch", "#contact-name");
        return;
      }
      // The archive page has no dispatch form: carry the choice across to the site.
      try {
        sessionStorage.setItem("vonlet:request", JSON.stringify({ service: item.service, title: item.title, message }));
      } catch (error) {
        /* storage can be blocked; the fallback still lands on the contact form */
      }
      window.location.href = "index.html#dispatch";
    });
    initGallery(lightbox.open);
    initHardware(lightbox);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
