/* Asystent Radnego — Service Worker. Update CACHE_TAG and DATA_FILENAME with each published dataset. */
const CACHE_TAG='asystent-radnego-1.60.0-20261031';
const ASSETS=['./','./index.html','./manifest.webmanifest','./version.json','./icons/icon-192.png','./icons/icon-512.png','./icons/icon-maskable-512.png','./data/katalog-v1.60.0.html.gz'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE_TAG).then(async c=>{
 await Promise.all(ASSETS.map(async asset=>{let r=await fetch(asset,{cache:'reload'});if(!r.ok)throw Error('Nie można zapisać PWA: '+asset);await c.put(asset,r)}));
 self.skipWaiting();
})));
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 for(const key of await caches.keys()){if(key.startsWith('asystent-radnego-')&&key!==CACHE_TAG)await caches.delete(key)}
 await self.clients.claim();
})()));
self.addEventListener('fetch',event=>{
 const req=event.request;
 if(req.method!=='GET')return;
 const url=new URL(req.url);
 if(url.origin!==self.location.origin||!url.pathname.startsWith(new URL(self.registration.scope).pathname))return;
 if(url.pathname.endsWith('/version.json')){
  event.respondWith((async()=>{
   try{let r=await fetch(req,{cache:'no-store'});if(r.ok){let c=await caches.open(CACHE_TAG);await c.put('./version.json',r.clone());return r}throw Error('HTTP '+r.status)}
   catch(e){return await caches.match('./version.json')||new Response('{}',{status:503})}
  })());return;
 }
 const isPage=req.mode==='navigate'||url.pathname.endsWith('/index.html')||url.pathname.endsWith('/');
 if(isPage){event.respondWith((async()=>{
  try{let r=await fetch(req);if(r.ok){const c=await caches.open(CACHE_TAG);await c.put('./index.html',r.clone());return r}}catch(e){}
  return await caches.match('./index.html')||Response.error();
 })());return}
 event.respondWith((async()=>{
  const hit=await caches.match(req,{ignoreSearch:true});if(hit)return hit;
  try{const r=await fetch(req);if(r.ok){const c=await caches.open(CACHE_TAG);await c.put(req,r.clone())}return r}
  catch(e){return Response.error()}
 })());
});
