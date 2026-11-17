/* ═══════════════════════════════════════════════════════════
   ABI NEXUS — main.js
   Logique globale : thème, reveals, compteurs, audio ambiances,
   SFX, progression de lecture, FAQ, tabs, particules, parallax.
   ═══════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  const ABINexus = (window.ABINexus = window.ABINexus || {});

  /* ── Helpers ── */
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const ROOT = document.body.dataset.root || "";
  ABINexus.root = ROOT;
  ABINexus.url = (p) => ROOT + p;

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ═══ THÈME DARK / LIGHT (F06) ═══ */
  const Theme = {
    KEY: "abinexus-theme",
    init() {
      const saved = localStorage.getItem(this.KEY) || "dark";
      this.set(saved);
      $$("[data-theme-toggle]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
          this.set(next);
          localStorage.setItem(this.KEY, next);
          SFX.play("click");
        });
      });
    },
    set(mode) {
      document.documentElement.dataset.theme = mode;
      $$("[data-theme-toggle]").forEach((b) => {
        b.setAttribute("aria-label", mode === "light" ? "Passer en mode sombre" : "Passer en mode clair");
        const icon = b.querySelector(".theme-icon");
        if (icon) icon.textContent = mode === "light" ? "🌙" : "☀️";
      });
    },
  };

  /* ═══ EFFETS SONORES (SFX) ═══ */
  const SFX = (ABINexus.sfx = {
    enabled: localStorage.getItem("abinexus-sfx") !== "off",
    volume: parseFloat(localStorage.getItem("abinexus-sfx-vol") || "0.55"),
    cache: {},
    _lastHover: 0,
    file(name) {
      if (!this.cache[name]) {
        const a = new Audio(ROOT + "audio/" + name + ".mp3");
        a.volume = this.volume;
        this.cache[name] = a;
      }
      return this.cache[name];
    },
    play(name) {
      if (!this.enabled) return;
      try {
        const base = this.file(name);
        const a = base.cloneNode();
        a.volume = this.volume;
        a.play().catch(() => {});
      } catch (e) { /* audio indisponible */ }
    },
    hover() {
      const now = Date.now();
      if (now - this._lastHover > 90) {
        this._lastHover = now;
        this.play("sfx-hover");
      }
    },
  });

  function bindSFX() {
    // One-shot page alert: zombie pages growl once after load
    if (/zombie/i.test(location.pathname)) {
      setTimeout(() => SFX.play("sfx-zombie-alert"), 700);
    }
    document.addEventListener("click", (e) => {
      const t = e.target.closest("[data-sfx]");
      if (t) SFX.play(t.dataset.sfx);
      else if (e.target.closest("a, button, .tab, .filter-btn")) SFX.play("sfx-click");
    });
    document.addEventListener("mouseover", (e) => {
      if (e.target.closest(".nav-link, .btn, .category-card, .tab")) SFX.hover();
    });
  }

  /* ═══ NAVIGATION : état scrolled ═══ */
  function initNavScroll() {
    const nav = $(".nav");
    if (!nav) return;
    const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ═══ BARRE DE PROGRESSION DE LECTURE (F11) ═══ */
  function initReadingProgress() {
    const bar = $(".reading-progress");
    if (!bar) return;
    const onScroll = () => {
      const h = document.documentElement;
      const max = h.scrollHeight - h.clientHeight;
      bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ═══ RÉVÉLATIONS AU SCROLL (F08) ═══ */
  function initReveals() {
    const els = $$(".reveal");
    if (!els.length) return;
    if (prefersReduced || !("IntersectionObserver" in window)) {
      els.forEach((el) => el.classList.add("visible"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) {
            en.target.classList.add("visible");
            if (en.target.dataset.count !== undefined) animateCount(en.target);
            io.unobserve(en.target);
          }
        });
      },
      { threshold: 0.14, rootMargin: "0px 0px -40px 0px" }
    );
    els.forEach((el) => io.observe(el));
  }

  /* ═══ COMPTEURS ANIMÉS (F14) ═══ */
  function animateCount(el) {
    const target = parseFloat(el.dataset.count || el.dataset.countTo || "0");
    const suffix = el.dataset.suffix || "";
    const dur = 1500;
    const start = performance.now();
    const fmt = (n) => (Number.isInteger(target) ? Math.round(n).toLocaleString("fr-FR") : n.toFixed(1));
    function tick(now) {
      const p = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
  function initCounters() {
    $$("[data-count]").forEach((el) => {
      if (!el.closest(".reveal")) {
        const io = new IntersectionObserver(
          (es) => es.forEach((e) => { if (e.isIntersecting) { animateCount(e.target); io.disconnect(); } }),
          { threshold: 0.4 }
        );
        io.observe(el);
      }
    });
  }

  /* ═══ FAQ ACCORDÉON ═══ */
  function initFAQ() {
    $$(".faq-q").forEach((q) => {
      q.addEventListener("click", () => {
        const item = q.closest(".faq-item");
        const a = item.querySelector(".faq-a");
        const open = item.classList.toggle("open");
        q.setAttribute("aria-expanded", open);
        a.style.maxHeight = open ? a.scrollHeight + "px" : "0";
      });
    });
  }

  /* ═══ TABS INTERACTIFS ═══ */
  function initTabs() {
    $$("[data-tabs]").forEach((group) => {
      const tabs = $$(".tab", group);
      const panels = $$(".tab-panel", group.parentElement || group);
      tabs.forEach((tab, i) => {
        tab.addEventListener("click", () => {
          tabs.forEach((t) => { t.classList.remove("active"); t.setAttribute("aria-selected", "false"); });
          tab.classList.add("active");
          tab.setAttribute("aria-selected", "true");
          panels.forEach((p, j) => p.classList.toggle("active", i === j));
        });
      });
    });
  }

  /* ═══ FILTRES (tier lists, listes armes…) ═══ */
  function initFilters() {
    $$("[data-filter-group]").forEach((group) => {
      const targetSel = group.dataset.filterTarget;
      const target = targetSel ? $$(targetSel) : [];
      $$(".filter-btn", group).forEach((btn) => {
        btn.addEventListener("click", () => {
          $$(".filter-btn", group).forEach((b) => b.classList.remove("active"));
          btn.classList.add("active");
          const f = btn.dataset.filter;
          target.forEach((el) => {
            const cats = (el.dataset.category || "").split(" ");
            el.style.display = f === "all" || cats.includes(f) ? "" : "none";
          });
        });
      });
    });
  }

  /* ═══ PARTICULES (hero) ═══ */
  function initParticles() {
    $$(".particle-field").forEach((field) => {
      if (prefersReduced) return;
      const n = parseInt(field.dataset.particles || "26", 10);
      const frag = document.createDocumentFragment();
      for (let i = 0; i < n; i++) {
        const p = document.createElement("span");
        p.className = "particle" + (Math.random() < 0.3 ? " green" : Math.random() < 0.12 ? " red" : "");
        p.style.left = Math.random() * 100 + "%";
        p.style.bottom = -10 - Math.random() * 30 + "%";
        p.style.setProperty("--p-dur", 7 + Math.random() * 9 + "s");
        p.style.setProperty("--p-delay", Math.random() * 10 + "s");
        p.style.setProperty("--p-drift", (Math.random() * 80 - 40) + "px");
        p.style.width = p.style.height = 2 + Math.random() * 3 + "px";
        frag.appendChild(p);
      }
      field.appendChild(frag);
    });
  }

  /* ═══ PARALLAX HERO ═══ */
  function initParallax() {
    if (prefersReduced) return;
    const bg = $(".hero-bg");
    if (!bg) return;
    let ticking = false;
    window.addEventListener("scroll", () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          const y = window.scrollY;
          if (y < window.innerHeight * 1.2) {
            bg.style.transform = `scale(1.06) translateY(${y * 0.22}px)`;
          }
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  /* ═══ AUDIO PLAYER AMBIANCE (F10) ═══ */
  const Audio = (ABINexus.player = {
    el: null,
    current: null,
    playing: false,
    volume: parseFloat(localStorage.getItem("abinexus-vol") || "0.5"),
    tracks: {
      default: "ambiance-tactical",
      home: "ambiance-menu",
      guides: "ambiance-tactical",
      armes: "ambiance-tactical",
      equipement: "ambiance-tactical",
      maps: "ambiance-tactical",
      s7: "ambiance-zombie",
      zombie: "ambiance-zombie",
      dark: "ambiance-dark-zone",
      items: "ambiance-dark-zone",
      meta: "ambiance-tactical",
      communaut: "ambiance-menu",
      saison7: "ambiance-zombie",
      cosmetiques: "ambiance-menu",
      events: "ambiance-menu",
      univers: "ambiance-dark-zone",
    },
    pick() {
      const zone = document.body.dataset.ambiance || "";
      for (const k of Object.keys(this.tracks)) {
        if (zone.includes(k)) return this.tracks[k];
      }
      return this.tracks.default;
    },
    init() {
      const ui = $(".audio-player");
      if (!ui) return;
      this.el = new Audio(undefined, { preload: "auto" }); // element audio
      this.current = this.pick();
      this.el.src = ROOT + "audio/" + this.current + ".mp3";
      this.el.loop = true;
      this.el.volume = this.volume;
      const playBtn = $(".ap-btn", ui);
      const title = $(".ap-title", ui);
      const state = $(".ap-state", ui);
      const vol = $("input[type=range]", ui);
      if (title) title.textContent = this.current.replace("ambiance-", "Ambiance · ").replace(/-/g, " ");
      if (vol) {
        vol.value = this.volume * 100;
        vol.addEventListener("input", () => {
          this.volume = vol.value / 100;
          this.el.volume = this.volume;
          localStorage.setItem("abinexus-vol", this.volume);
        });
      }
      const toggle = () => {
        this.playing ? this.pause() : this.play();
        if (state) state.textContent = this.playing ? "Lecture" : "Pause";
        if (playBtn) playBtn.innerHTML = this.playing ? ICON_PAUSE : ICON_PLAY;
      };
      if (playBtn) playBtn.addEventListener("click", toggle);
      // Révélation automatique du mini-player après 1,2 s (sans lecture auto — respect autoplay policy)
      setTimeout(() => ui.classList.add("show"), 1200);
      document.addEventListener("visibilitychange", () => {
        if (document.hidden && this.playing) this.el.pause();
        else if (!document.hidden && this.playing) this.el.play().catch(() => {});
      });
    },
    play() {
      if (!this.el) return;
      this.el.play().then(() => { this.playing = true; }).catch(() => { this.playing = false; });
      this.playing = true;
    },
    pause() {
      if (!this.el) return;
      this.el.pause();
      this.playing = false;
    },
  });

  const ICON_PLAY = `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>`;
  const ICON_PAUSE = `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6 5h4v14H6zm8 0h4v14h-4z"/></svg>`;

  /* ═══ TRANSITIONS DE PAGE (F07) ═══ */
  function initPageTransition() {
    const overlay = $(".page-transition");
    if (overlay) requestAnimationFrame(() => overlay.classList.add("done"));
    document.addEventListener("click", (e) => {
      const a = e.target.closest('a[href]');
      if (!a) return;
      const href = a.getAttribute("href");
      if (!href || href.startsWith("#") || href.startsWith("http") || a.target === "_blank" || e.metaKey || e.ctrlKey) return;
      if (overlay && !a.classList.contains("no-transition")) {
        e.preventDefault();
        overlay.classList.remove("done");
        setTimeout(() => { window.location.href = href; }, 340);
      }
    });
  }

  /* ═══ DATE DYNAMIQUE ═══ */
  function initDates() {
    const now = new Date();
    const opts = { day: "numeric", month: "long", year: "numeric" };
    $$("[data-today]").forEach((el) => { el.textContent = now.toLocaleDateString("fr-FR", opts); });
    $$("[data-year]").forEach((el) => { el.textContent = now.getFullYear(); });
  }

  /* ═══ BOOT ═══ */
  document.addEventListener("DOMContentLoaded", () => {
    Theme.init();
    bindSFX();
    initNavScroll();
    initReadingProgress();
    initReveals();
    initCounters();
    initFAQ();
    initTabs();
    initFilters();
    initParticles();
    initParallax();
    initPageTransition();
    initDates();
    Audio.init();
    document.documentElement.classList.add("js-ready");
  });

  /* Service Worker PWA (S21) — HTTP(S) uniquement, échec silencieux */
  if ("serviceWorker" in navigator && /^https?:$/.test(location.protocol)) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("sw.js").catch(function () {});
    });
  }
})();
