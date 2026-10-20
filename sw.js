/* PROPESA · service worker mínimo (v1.12.0): solo sirve para que la app se pueda instalar en Android y en computadora.
   No guarda nada en caché: cada vez se pide la página al servidor, igual que sin service worker. */
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{if(e.request.mode==='navigate')e.respondWith(fetch(e.request))});
