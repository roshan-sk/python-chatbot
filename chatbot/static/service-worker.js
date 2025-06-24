self.addEventListener('install', function (e) {
  console.log('[ServiceWorker] Install');
  self.skipWaiting();
});

self.addEventListener('activate', function (e) {
  console.log('[ServiceWorker] Activate');
});

self.addEventListener('fetch', function (e) {
  e.respondWith(fetch(e.request));
});
