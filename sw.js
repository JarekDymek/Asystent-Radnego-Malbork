/* Asystent Radnego — Service Worker. Update CACHE_TAG and DATA_FILENAME with each published dataset. */
const CACHE_TAG='asystent-radnego-1.64.0-20261124';
const ASSETS=['./','./index.html','./manifest.webmanifest','./version.json','./icons/icon-192.png','./icons/icon-512.png','./icons/icon-maskable-512.png','./data/katalog-v1.63.0.html.gz','./data/katalog-operacyjny-v1.63.0.sqlite.gz','./data/odpowiedzi_2026-11-10_public.json','./analiza-uchwal.html','./data/analiza-uchwal.json'];
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
 if(url.pathname.endsWith('/version.json')||url.pathname.endsWith('/data/analiza-uchwal.json')){
  const key=url.pathname.endsWith('/version.json')?'./version.json':'./data/analiza-uchwal.json';
  event.respondWith((async()=>{
   try{let r=await fetch(req,{cache:'no-store'});if(r.ok){let c=await caches.open(CACHE_TAG);await c.put(key,r.clone());return r}throw Error('HTTP '+r.status)}
   catch(e){return await caches.match(key)||new Response('{}',{status:503})}
  })());return;
 }
 const isAnalysis=url.pathname.endsWith('/analiza-uchwal.html');
 const pageKey=isAnalysis?'./analiza-uchwal.html':'./index.html';
 const isPage=req.mode==='navigate'||isAnalysis||url.pathname.endsWith('/index.html')||url.pathname.endsWith('/');
 if(isPage){event.respondWith((async()=>{
  try{let r=await fetch(req);if(r.ok){const c=await caches.open(CACHE_TAG);await c.put(pageKey,r.clone());return r}}catch(e){}
  return await caches.match(pageKey)||Response.error();
 })());return}
 event.respondWith((async()=>{
  const hit=await caches.match(req,{ignoreSearch:true});if(hit)return hit;
  try{const r=await fetch(req);if(r.ok){const c=await caches.open(CACHE_TAG);await c.put(req,r.clone())}return r}
  catch(e){return Response.error()}
 })());
});
