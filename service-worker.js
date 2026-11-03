/* Cache only application shell; always attempt latest content when online. */
const CACHE='ios27-ui-demo-v1.0.0';
const ASSETS=['./','./index.html','./manifest.webmanifest','./css/showcase.css','./css/tokens.css','./css/typography.css','./css/glass.css','./css/ui-library.css','./js/showcase.js','./js/catalog.js','./js/type-data.js','./assets/icone-192.png','./assets/icone-512.png','./assets/icone-180.png'];
self.addEventListener('install',ev=>ev.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',ev=>ev.waitUntil(caches.keys().then(all=>Promise.all(all.filter(name=>name!==CACHE).map(name=>caches.delete(name)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',ev=>{if(ev.request.method!=='GET'||new URL(ev.request.url).origin!==self.location.origin)return;ev.respondWith(fetch(ev.request).then(res=>{if(res.ok){let copy=res.clone();caches.open(CACHE).then(c=>c.put(ev.request,copy)).catch(()=>{})}return res}).catch(()=>caches.match(ev.request).then(v=>v||caches.match('./index.html'))))});
