/* ═══════════════════════════════════════════════════════════
   ABI NEXUS — map-explorer.js (S15)
   Explorateur Leaflet hors-ligne : image overlay (CRS.Simple,
   aucun tile server) + marqueurs exfils/clés/hotspots/boss.
   Montage auto sur pages map-*.html (après le 1ᵉʳ <figure>).
   ═══════════════════════════════════════════════════════════ */
(function () {
  "use strict";
  if (typeof L === "undefined") return;

  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));

  const page = decodeURIComponent(location.pathname.split("/").pop() || "");
  if (!page.startsWith("map-")) return;
  const key = page.replace(/^map-/, "").replace(/\.html$/, "");
  if (key === "no-mans-land") return; // page modes, pas de carte physique

  const ROOT = document.body.dataset.root || "../";
  const dataUrl = ROOT + "js/data-maps.json";

  const TYPE_META = {
    exfil: { cls: "exfil", label: "Exfil", icon: "E" },
    key: { cls: "key", label: "Clé / salle forte", icon: "K" },
    hot: { cls: "hot", label: "Hotspot", icon: "H" },
    boss: { cls: "boss", label: "Boss / event", icon: "B" },
  };

  fetch(dataUrl)
    .then((r) => r.json())
    .then((all) => {
      const data = all[key];
      if (!data) return;
      mount(data);
    })
    .catch(() => {});

  function mount(data) {
    // Cible : tout en haut du guide-content (visible immédiatement),
    // sinon avant le 1er figure, sinon fin du guide-content
    const content = $(".guide-content") || $("#contenu");
    if (!content) return;
    const anchor = $("figure", content) || content.firstElementChild;

    const wrap = document.createElement("div");
    wrap.className = "map-explorer widget-mount";
    wrap.setAttribute("data-widget", "map-explorer");
    wrap.innerHTML =
      '<div class="me-bar"><strong>⬢ EXPLORATEUR — ' +
      data.title +
      '</strong>' +
      '<button class="me-chip active" data-type="all">Tout</button>' +
      '<button class="me-chip" data-type="exfil">Exfils</button>' +
      '<button class="me-chip" data-type="key">Clés</button>' +
      '<button class="me-chip" data-type="hot">Hotspots</button>' +
      '<button class="me-chip" data-type="boss">Boss</button>' +
      "</div>" +
      '<div id="me-map" role="application" aria-label="Carte interactive ' +
      data.title +
      '"></div>' +
      '<div class="me-legend">' +
      '<span><i style="background:#2EFF8F"></i>Exfil</span>' +
      '<span><i style="background:#C8A84B"></i>Clé/salle forte</span>' +
      '<span><i style="background:#FF5C5C"></i>Hotspot</span>' +
      '<span><i style="background:#B44BFF"></i>Boss/event</span>' +
      "</div>" +
      '<div class="me-note">Clique un marqueur pour le détail · zoom molette / double-clic · positions indicatives — croise avec les tableaux de la page.</div>';

    if (anchor) content.insertBefore(wrap, anchor);
    else content.appendChild(wrap);

    const img = new Image();
    img.onload = () => buildMap(data, img.naturalWidth, img.naturalHeight);
    img.onerror = () => {
      $("#me-map", wrap).innerHTML =
        '<div class="me-note">Carte indisponible — consulte les tableaux ci-dessous.</div>';
    };
    img.src = data.img;
  }

  function buildMap(data, W, H) {
    const map = L.map("me-map", {
      crs: L.CRS.Simple,
      minZoom: -2,
      maxZoom: 2,
      zoomSnap: 0.25,
      attributionControl: false,
      zoomControl: true,
    });

    // Bounds en coordonnées pixel (y inversé pour CRS.Simple)
    const southWest = map.unproject(L.point(0, H), map.getMaxZoom());
    const northEast = map.unproject(L.point(W, 0), map.getMaxZoom());
    const bounds = L.latLngBounds(southWest, northEast);

    L.imageOverlay(data.img, bounds).addTo(map);
    map.fitBounds(bounds);
    map.setMaxBounds(bounds.pad(0.25));

    const layers = {};
    data.markers.forEach((m) => {
      const meta = TYPE_META[m.type] || TYPE_META.hot;
      const latlng = map.unproject(L.point(m.x * W, m.y * H), map.getMaxZoom());
      const icon = L.divIcon({
        className: "",
        html: '<div class="me-pin ' + meta.cls + '"><span>' + meta.icon + "</span></div>",
        iconSize: [26, 26],
        iconAnchor: [13, 26],
        popupAnchor: [0, -24],
      });
      const mk = L.marker(latlng, { icon }).addTo(map);
      mk.bindPopup(
        "<b>" +
          m.name +
          "</b><br><span style='opacity:.85'>" +
          meta.label +
          "</span><br>" +
          (m.note || "")
      );
      (layers[m.type] = layers[m.type] || L.layerGroup()).addLayer(mk);
    });

    // Filtres
    $$(".me-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        $$(".me-chip").forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        const t = chip.dataset.type;
        Object.keys(layers).forEach((type) => {
          const on = t === "all" || type === t;
          if (on && !map.hasLayer(layers[type])) map.addLayer(layers[type]);
          if (!on && map.hasLayer(layers[type])) map.removeLayer(layers[type]);
        });
        // "all" : ajouter aussi les types sans layer déjà présent
        if (t === "all") {
          Object.keys(layers).forEach((type) => {
            if (!map.hasLayer(layers[type])) map.addLayer(layers[type]);
          });
        }
      });
    });
  }
})();
