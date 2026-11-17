/* ═══════════════════════════════════════════════════════════
   ABI NEXUS — navigation.js
   Hamburger mobile, mega-menu, lien actif, recherche (Ctrl+K),
   raccourcis clavier, smooth anchors.
   ═══════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  /* ── Menu hamburger (mobile) ── */
  function initHamburger() {
    const burger = $(".hamburger");
    const links = $(".nav-links");
    if (!burger || !links) return;
    burger.addEventListener("click", () => {
      const open = links.classList.toggle("open");
      burger.classList.toggle("open", open);
      burger.setAttribute("aria-expanded", open);
      document.body.style.overflow = open ? "hidden" : "";
    });
    // Fermeture après clic sur un lien
    links.addEventListener("click", (e) => {
      if (e.target.closest("a") && links.classList.contains("open")) {
        links.classList.remove("open");
        burger.classList.remove("open");
        burger.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      }
    });
  }

  /* ── Mega-menu : ouverture tactile ── */
  function initMegaTouch() {
    $$(".nav-item.has-mega").forEach((item) => {
      const link = $(".nav-link", item);
      if (!link) return;
      link.addEventListener("click", (e) => {
        if (window.matchMedia("(max-width: 639px)").matches) {
          e.preventDefault();
          item.classList.toggle("open");
        }
      });
    });
  }

  /* ── Lien actif selon l'URL courante ── */
  function initActiveLink() {
    const path = decodeURIComponent(location.pathname.split("/").pop() || "index.html");
    $$(".nav-link, .mega-link a, .footer-col a").forEach((a) => {
      const href = (a.getAttribute("href") || "").split("/").pop();
      if (href && href === path) {
        a.classList.add("active");
        const parentItem = a.closest(".nav-item");
        if (parentItem) parentItem.classList.add("active");
      }
    });
  }

  /* ── Recherche globale (F01) — délègue à search.js si présent ── */
  function initSearch() {
    const modal = $(".search-modal");
    const openers = $$("[data-search-open]");
    const input = modal ? $("input", modal) : null;

    const open = () => {
      if (!modal) return;
      modal.classList.add("open");
      document.body.style.overflow = "hidden";
      setTimeout(() => input && input.focus(), 60);
    };
    const close = () => {
      if (!modal) return;
      modal.classList.remove("open");
      document.body.style.overflow = "";
    };

    openers.forEach((b) => b.addEventListener("click", open));
    if (modal) {
      modal.addEventListener("click", (e) => { if (e.target === modal) close(); });
      const closeBtn = $(".search-close", modal);
      if (closeBtn) closeBtn.addEventListener("click", close);
    }

    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        modal && modal.classList.contains("open") ? close() : open();
      }
      if (e.key === "Escape") close();
      // "/" ouvre la recherche quand on n'est pas dans un champ
      if (e.key === "/" && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
        e.preventDefault();
        open();
      }
    });

    // Instant search : délègue à ABINexusSearch (search.js)
    if (input) {
      input.addEventListener("input", () => {
        const q = input.value.trim();
        if (window.ABINexusSearch && typeof window.ABINexusSearch.query === "function") {
          window.ABINexusSearch.query(q);
        }
      });
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && window.ABINexusSearch && window.ABINexusSearch.gotoFirst) {
          window.ABINexusSearch.gotoFirst();
        }
      });
    }
  }

  /* ── Smooth anchors + offset ── */
  function initAnchors() {
    document.addEventListener("click", (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      const id = a.getAttribute("href");
      if (id.length < 2) return;
      const target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        history.replaceState(null, "", id);
      }
    });
  }

  /* ── TOC : surlignage de la section courante ── */
  function initTocHighlight() {
    const toc = $(".toc");
    if (!toc || !("IntersectionObserver" in window)) return;
    const links = $$("a[href^='#']", toc);
    const sections = links
      .map((l) => document.querySelector(l.getAttribute("href")))
      .filter(Boolean);
    if (!sections.length) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) {
            links.forEach((l) =>
              l.classList.toggle("active", l.getAttribute("href") === "#" + en.target.id)
            );
          }
        });
      },
      { rootMargin: "-30% 0px -60% 0px" }
    );
    sections.forEach((s) => io.observe(s));
  }

  document.addEventListener("DOMContentLoaded", () => {
    initHamburger();
    initMegaTouch();
    initActiveLink();
    initSearch();
    initAnchors();
    initTocHighlight();
  });
})();
