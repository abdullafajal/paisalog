// const CACHE_NAME = 'paisalog-v1';
// const urlsToCache = [
//     '/',
//     '/static/css/tabler.min.css',
//     '/static/js/tabler.min.js',
//     '/static/js/chart.min.js',
//     '/static/img/icon-192x192.png',
//     '/static/img/icon-512x512.png',
//     '/static/manifest.json'
// ];

// self.addEventListener('install', event => {
//     event.waitUntil(
//         caches.open(CACHE_NAME)
//             .then(cache => {
//                 console.log('Opened cache');
//                 // Cache each URL individually to handle failures gracefully
//                 return Promise.allSettled(
//                     urlsToCache.map(url => 
//                         fetch(url)
//                             .then(response => {
//                                 if (!response.ok) {
//                                     throw new Error(`Failed to fetch ${url}`);
//                                 }
//                                 return cache.put(url, response);
//                             })
//                             .catch(error => {
//                                 console.warn(`Failed to cache ${url}:`, error);
//                             })
//                     )
//                 );
//             })
//     );
// });

// self.addEventListener('fetch', event => {
//     event.respondWith(
//         caches.match(event.request)
//             .then(response => {
//                 if (response) {
//                     return response;
//                 }
//                 return fetch(event.request)
//                     .then(response => {
//                         // Don't cache if not a valid response
//                         if (!response || response.status !== 200 || response.type !== 'basic') {
//                             return response;
//                         }
                        
//                         // Clone the response
//                         const responseToCache = response.clone();
                        
//                         // Cache the response
//                         caches.open(CACHE_NAME)
//                             .then(cache => {
//                                 cache.put(event.request, responseToCache);
//                             })
//                             .catch(error => {
//                                 console.warn('Failed to cache response:', error);
//                             });
                            
//                         return response;
//                     })
//                     .catch(error => {
//                         console.warn('Fetch failed:', error);
//                         // Return a fallback response if needed
//                         return new Response('Network error occurred', {
//                             status: 408,
//                             headers: new Headers({
//                                 'Content-Type': 'text/plain'
//                             })
//                         });
//                     });
//             })
//     );
// });

// self.addEventListener('activate', event => {
//     const cacheWhitelist = [CACHE_NAME];
//     event.waitUntil(
//         caches.keys().then(cacheNames => {
//             return Promise.all(
//                 cacheNames.map(cacheName => {
//                     if (cacheWhitelist.indexOf(cacheName) === -1) {
//                         return caches.delete(cacheName);
//                     }
//                 })
//             );
//         })
//     );
// }); 

var staticCacheName = "paisalog-v1";

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(staticCacheName).then(function (cache) {
      return cache.addAll(["/"]);
    })
  );
});

self.addEventListener("fetch", function (event) {
  var requestUrl = new URL(event.request.url);
  if (requestUrl.origin === location.origin) {
    if (requestUrl.pathname === "/") {
      event.respondWith(caches.match("/"));
      return;
    }
  }
  event.respondWith(
    caches.match(event.request).then(function (response) {
      return response || fetch(event.request);
    })
  );
});
