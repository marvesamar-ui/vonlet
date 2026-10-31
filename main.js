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
      group,
      title: card.dataset.title || "Operation",
      brief: card.dataset.brief || "",
      equipment: (card.dataset.equipment || "").split("|").filter(Boolean),
      service: card.dataset.service || "integrated",
      kind: card.dataset.kind || "Showcase imagery",
      category: categoryNode ? categoryNode.textContent.trim() : "FLEET & TECHNOLOGY",
      image: image ? (image.currentSrc || image.src) : "",
      alt: image ? image.alt : ""
    };
  }

  function initGallery(onOpen) {
    const grid = $("#gallery-grid");
    const cards = $$(".mission-card", grid);
    const buttons = $$(".filter-tab");
    const status = $("#gallery-status");
    const count = $("#gallery-count");
    const items = cards.map((card) => readCard(card, "operations"));
    let visibleItems = items.slice();

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
          if (!prefersReducedMotion() && typeof card.animate === "function") {
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
      const label = filter === "all" ? "all" : activeButton.firstChild.textContent.trim();
      status.textContent = `Showing ${visibleItems.length} ${label} operation${visibleItems.length === 1 ? "" : "s"}.`;
      count.textContent = `${pad(visibleItems.length)} VIEW${visibleItems.length === 1 ? "" : "S"} / ${pad(filter === "all" ? 4 : 1)} SPECIALISM${filter === "all" ? "S" : ""}`;
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
      source.textContent = `${item.kind}. Equipment and deployment are confirmed during assessment.`;
      equipment.replaceChildren(...item.equipment.map((label) => {
        const li = document.createElement("li");
        li.textContent = label;
        return li;
      }));
      counter.textContent = `${pad(index + 1)} / ${pad(items.length)}`;
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

  function initServiceLinks() {
    $$('[data-service-link]').forEach((button) => {
      button.addEventListener("click", () => {
        const service = button.dataset.serviceLink;
        const heading = $("h3", button.closest(".service-row"));
        const label = heading ? heading.textContent.trim() : "Security services";
        selectService(service, label, `I'm interested in ${label}. Please advise on coverage options for my site.`);
        navigateToSection("dispatch", "#contact-name");
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
    const addonRates = { cctv: 180, k9: 320, sensors: 120 };
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
      const addonLabels = selectedAddons.map((key) => ({ cctv: "CCTV monitoring", k9: "K-9 patrol support", sensors: "AI perimeter sensors" }[key]));

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

  /* ---------- Dispatch form validation & email handoff ---------- */
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
      sendEmail.href = `mailto:info@vonletsecurity.co.zw?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(requestText)}`;
      form.hidden = true;
      ready.hidden = false;
      status.textContent = "Request prepared. Nothing has been sent yet.";
      ready.focus({ preventScroll: true });
      ready.scrollIntoView({ behavior: scrollBehavior(), block: "center" });
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
        html: "<p>This showcase does not use analytics cookies or submit form data to a server. The details you enter stay in this page until you choose to open your email app or copy them.</p><p>If you send the prepared email, your email provider and Vonlet will handle the message according to their own policies. Avoid including sensitive personal information, access codes or security vulnerabilities in the operational brief.</p><p>For urgent assistance, call the published hotline instead of using the form.</p>"
      },
      licensing: {
        title: "Licensing & compliance",
        html: "<p>Vonlet Security Services operates in Zimbabwe and Zambia. Current company registration, security operating licences, tax clearance and insurance documents should be verified directly with Vonlet during procurement.</p><p>This showcase does not publish a licence number. Request the current compliance pack before contracting:</p><ul><li>Email: info@vonletsecurity.co.zw</li><li>Hotline: +263 772 856 852</li><li>Head office: 9 Blatherwick Road, Queensdale, Harare</li></ul><p>Drone, armed and specialist deployments remain subject to applicable permissions and site-specific approval.</p>"
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

  /* ---------- Boot ---------- */
  function init() {
    initNavigation();
    initTicker();
    initScrollUI();
    initReveal();
    initCounters();
    initEstimator();
    initContact();
    initInfoDialogs();
    initServiceLinks();

    const lightbox = createLightbox((item) => {
      selectService(item.service, item.title, `I'm interested in ${item.title}. Please advise on options for my site.`);
      navigateToSection("dispatch", "#contact-name");
    });
    initGallery(lightbox.open);
    initHardware(lightbox);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
