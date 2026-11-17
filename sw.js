/* ABI NEXUS — Service Worker (S21) */
/* Stratégie : cache-first sur les assets statiques (cache versionnée),
   network-first sur les pages HTML avec repli cache. */
const CACHE = "abinexus-v1";
const ASSETS = [
  "./",
  "index.html",
  "css/variables.css",
  "css/main.css",
  "css/animations.css",
  "css/components.css",
  "css/responsive.css",
  "css/interactivity.css",
  "js/main.js",
  "js/navigation.js",
  "js/search.js",
  "js/interactivity.js",
  "js/data-search-index.json",
  "manifest.json",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ASSETS).catch(() => undefined)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;

  // Pages HTML : network-first, repli cache
  if (e.request.mode === "navigate" || url.pathname.endsWith(".html")) {
    e.respondWith(
      fetch(e.request)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => undefined);
          return res;
        })
        .catch(() => caches.match(e.request).then((m) => m || caches.match("index.html")))
    );
    return;
  }

  // Assets : cache-first, puis réseau + mise en cache
  e.respondWith(
    caches.match(e.request).then(
      (hit) =>
        hit ||
        fetch(e.request).then((res) => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => undefined);
          }
          return res;
        })
    )
  );
});
