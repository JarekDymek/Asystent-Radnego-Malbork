/* Asystent Radnego — bezplatne rozszerzenia interfejsu, 1.60.1.
   Dziala wyłącznie na wbudowanym, wersjonowanym indeksie. Nie wysyla pytan do serwera. */
(function(){
 'use strict';
 const get=id=>document.getElementById(id);
 if(!get('tabs')||!get('query')||!window.ASM_DATA)return;
 const style=document.createElement('style');
 style.textContent=`
 .filters{grid-template-columns:minmax(195px,1.8fr) repeat(4,minmax(108px,1fr))}
 .ask-panel{background:#fff;border:1px solid #dce5ef;border-radius:13px;padding:15px;margin-bottom:14px}
 .ask-panel h2{margin:0 0 5px;font-size:21px}
 .ask-panel .ask-note{font-size:13px;color:#52677c;margin:8px 0}
 .ask-panel textarea{width:100%;min-height:100px;resize:vertical;border:1px solid #b3c7dc;border-radius:9px;padding:12px;font:inherit;color:#172e44}
 .ask-panel .ask-submit{background:#174e7d;color:white;border:0;border-radius:9px;padding:10px 18px;font-weight:700;margin-top:9px;min-height:43px}
 .ask-panel .ask-chips{display:flex;flex-wrap:wrap;gap:7px;margin:12px 0}
 .ask-panel .ask-chip{background:#edf4fb;border:1px solid #c6d8e9;border-radius:18px;color:#244a72;padding:7px 11px;font-size:13px;text-align:left}
 .ask-result{margin-top:15px;display:grid;gap:11px}
 .ask-result .ask-group{border-top:1px solid #dae4ed;padding-top:12px}
 .ask-result h3{font-size:17px;margin:4px 0 9px}
 .ask-hit{padding:10px 12px;background:#f6f9fc;border:1px solid #dce7f2;border-radius:9px;margin:7px 0}
 .ask-hit p{margin:5px 0 6px;font-size:13px;line-height:1.5;white-space:pre-line}
 .ask-hit small{font-size:12px;color:#53677a}
 .ask-hit a{overflow-wrap:anywhere}
 .ask-result .ask-disclaimer{background:#fff6e5;border-left:3px solid #d6a047;padding:10px;font-size:13px;color:#6d5125}
 .ask-hit .ask-detail{border:0;background:transparent;text-decoration:underline;color:#175c92;padding:4px 0;font-size:13px}
 @media(max-width:780px){.filters{grid-template-columns:repeat(2,minmax(0,1fr))}.filters>div:first-child{grid-column:span 2}}
 `;
 document.head.appendChild(style);
 const sortWrapper=document.createElement('div');
 sortWrapper.innerHTML='<label for="sortOrder">Sortuj według daty</label><select id="sortOrder" aria-label="Sortuj wyniki według daty"><option value="desc">Od najnowszych</option><option value="asc">Od najstarszych</option></select>';
 document.querySelector('.filters').appendChild(sortWrapper);
 const askTab=document.createElement('button');
 askTab.type='button';askTab.className='tab';askTab.dataset.tab='ask';askTab.setAttribute('aria-selected','false');askTab.textContent='Zapytaj o uchwały';
 get('tabs').insertBefore(askTab,get('tabs').querySelector('[data-tab="compare"]'));
 const panel=document.createElement('section');
 panel.id='askPanel';panel.className='ask-panel';panel.hidden=true;
 panel.innerHTML=`<h2>Zapytaj o uchwały</h2>
 <p class="ask-note">Zadaj pytanie własnymi słowami. Wyszukam powiązane akty, paragrafy i ustalenia audytu w lokalnej bazie, z podaniem źródeł. To nie jest czat AI ani automatyczna opinia prawna.</p>
 <form id="askForm"><label for="askText"><strong>Twoje pytanie</strong></label>
 <textarea id="askText" maxlength="550" placeholder="Np. Czy mogę wejść z psem na cmentarz? Jakie uchwały zmieniły regulamin?"></textarea>
 <button type="submit" class="ask-submit">Wyszukaj odpowiedź i źródła</button></form>
 <div class="ask-chips" aria-label="Przykładowe pytania">
 <button type="button" class="ask-chip" data-question="Czy psy i inne zwierzęta mogą wchodzić na cmentarz w Malborku?">Psy na cmentarzu</button>
 <button type="button" class="ask-chip" data-question="Które uchwały uchylają regulamin cmentarza?">Historia uchwał cmentarnych</button>
 <button type="button" class="ask-chip" data-question="Jakie błędy formalne i sprzeczności wykryto w uchwałach o cmentarzu?">Błędy i sprzeczności</button>
 </div><div class="ask-result" id="askResponse" aria-live="polite"><div class="warning">Wybierz przykładowe pytanie albo wpisz własne.</div></div>`;
 get('comparePanel').before(panel);
 const dateOf=o=>{
  const m=String(o.data||o.adopted||o.date||'').match(/(20\d\d)-(\d\d)-(\d\d)/);
  return m?m[0]:'';
 };
 const oldRender=render;
 render=function(){
  if(state.tab==='ask'){
   get('comparePanel').hidden=true;panel.hidden=false;
   get('results').innerHTML='';get('more').hidden=true;
   get('count').textContent='Pytania do uchwał · lokalny indeks';
   return;
  }
  panel.hidden=true;
  oldRender();
  if(state.tab==='compare')return;
  const direction=get('sortOrder').value==='asc'?1:-1;
  state.results.sort((a,b)=>{
   const da=dateOf(a),db=dateOf(b);
   if(!da&&db)return 1;
   if(da&&!db)return -1;
   return da&&db?direction*da.localeCompare(db):0;
  });
  const max=(state.page+1)*state.limit;
  get('results').innerHTML=state.results.slice(0,max).map(resultHtml).join('')||'<div class="empty">Brak pasujących danych w lokalnym indeksie. Zmień filtry lub sprawdź źródła.</div>';
  get('more').hidden=max>=state.results.length;
 };
 get('sortOrder').addEventListener('change',()=>{state.page=0;render()});

 // Pytania służą do wyszukania udokumentowanych wniosków, nie do wymyślania przepisów.
 const stop=new Set(['czy','jak','jaka','jakie','jaki','ktore','ktora','ktory','maja','moze','mozna','jest','sa','oraz','albo','dla','sie','tej','tego','takie','tych','jego','jej','nad','pod','dotyczace','dotyczy','sprawie','malborka','malborku','rady','miasta','uchwal','uchwala','uchwaly','przepisy','regulaminu','regulamin','przez','ktorych','jakich','wprowadzone','zostaly','zostal','nastepnie','roku','lata','obowiazuje','aktualnie']);
 const tokens=q=>{
  const n=normal(q), arr=n.replace(/[^a-z0-9]+/g,' ').split(' ').filter(w=>w.length>2&&!stop.has(w));
  const r=new Set(arr);
  if(/cmentar|grob|pochow|kolumbari/.test(n))['cmentarz','cmentarza','cmentarzu','cmentar','pochow','kolumbar'].forEach(x=>r.add(x));
  if(/pies|psa|psow|zwierz/.test(n))['zwierz','psow','psa','pies','sm c y','smycz'].forEach(x=>r.add(x));
  if(/uchyl|zmien|zastap/.test(n))['uchyl','zmian','poprzednie'].forEach(x=>r.add(x));
  if(/sprzeczn|blad|bled|niezgodn|niewazn/.test(n))['bled','blad','sprzeczn','kolizj','praw'].forEach(x=>r.add(x));
  return [...r].filter(x=>x.length>=3);
 };
 const score=(o,terms,fields,boost=[])=>{
  const text=normal(fields.map(k=>o[k]||'').join(' '));
  let n=0;
  for(const term of terms)if(text.includes(term))n+= boost.includes(term)?4:1;
  return n;
 };
 const rank=(collection,terms,fields,limit,min=1)=>collection.map(o=>({o,s:score(o,terms,fields)})).filter(x=>x.s>=min).sort((a,b)=>b.s-a.s||dateOf(b.o).localeCompare(dateOf(a.o))).slice(0,limit).map(x=>x.o);
 const fmtLink=(url,label)=>legalSource(url,label);
 const short=(text,max=650)=>{const str=t(text);return esc(str.length>max?str.slice(0,max)+'…':str)};
 const hit=(heading,description,meta,url,label,extra='')=>'<article class="ask-hit"><strong>'+esc(heading)+'</strong><p>'+short(description)+'</p>'+(meta?'<small>'+esc(meta)+'</small><div>':'<div>')+fmtLink(url,label||'Oficjalny dokument')+'</div>'+extra+'</article>';
 const renderAnswer=(question)=>{
  const output=get('askResponse');
  const terms=tokens(question);
  if(!terms.length){output.innerHTML='<div class="warning">Wpisz bardziej szczegółowe pytanie: temat, zakaz, nazwę uchwały albo numer.</div>';return;}
  const findings=rank(DATA.audit||[],terms,['topic','headline','explanation','evidence','finding_type','action'],5);
  const provisions=rank(DATA.audit_provisions||[],terms,['subject','summary','modality','ref'],7);
  const acts=rank(DATA.audit_acts||[],terms,['title','number','topic','kind'],7);
  const pairIds=new Set([...findings.flatMap(f=>[f.act_a,f.act_b]),...provisions.map(p=>p.act_id),...acts.map(a=>a.act_id)]);
  const relations=(DATA.audit_relations||[]).filter(r=>pairIds.has(r.older_id)&&pairIds.has(r.newer_id)&&/uchyl|zmian|zastap/i.test(normal(r.relation_type))).slice(0,6);
  const total=findings.length+provisions.length+acts.length+relations.length;
  let result='<div class="ask-disclaimer"><strong>Wyszukiwanie w bazie, nie opinia prawna.</strong> Podane informacje są streszczeniami zarejestrowanych źródeł. Brak wyniku nie potwierdza braku sprzeczności; legalność i aktualne obowiązywanie wymagają kontroli oficjalnych tekstów.</div>';
  if(!total){output.innerHTML=result+'<div class="warning">Nie znaleziono wystarczających danych w aktualnym indeksie. Spróbuj innego sformułowania albo zadaj pytanie w projekcie „Asystent Radnego” w ChatGPT.</div>';return;}
  result+='<p class="ask-note">Odnaleziono: '+findings.length+' ustaleń audytu, '+provisions.length+' przepisów, '+acts.length+' aktów, '+relations.length+' powiązań. Zobacz źródła poniżej.</p>';
  if(provisions.length){
   result+='<section class="ask-group"><h3>Zapisy odnalezione w dokumentach</h3>';
   for(const p of provisions){const a=(DATA.audit_acts||[]).find(a=>a.act_id===p.act_id);result+=hit((a?.number||p.act_id)+' · '+p.ref,p.summary,'Rodzaj: '+p.modality+' · '+(a?.adopted||'data nieustalona')+' · '+p.certainty,p.source_url,'Dokument źródłowy')}
   result+='</section>';
  }
  if(findings.length){
   result+='<section class="ask-group"><h3>Ustalenia audytu — w tym zastrzeżenia</h3>';
   for(const f of findings){result+=hit(f.headline,f.explanation, 'Status: '+f.status+' · '+f.finding_type,f.source_a,'Pierwsze źródło urzędowe','<div>'+fmtLink(f.source_b,'Drugie źródło urzędowe')+'</div><button type="button" class="ask-detail" data-audit-id="'+esc(f.finding_id)+'">Otwórz szczegóły audytu</button>')}
   result+='</section>';
  }
  if(relations.length){
   result+='<section class="ask-group"><h3>Powiązania i uchylenia</h3>';
   for(const r of relations)result+=hit(r.older_id+' → '+r.newer_id,r.evidence,r.relation_type+' · '+r.verification,r.source_url,'Źródło urzędowe');
   result+='</section>';
  }
  if(acts.length){
   result+='<section class="ask-group"><h3>Powiązane uchwały</h3>';
   for(const a of acts)result+=hit(a.number||a.act_id,a.title,a.adopted+' · '+a.fulltext_status+' · '+a.legal_status,a.source_url,'Otwórz akt');
   result+='</section>';
  }
  output.innerHTML=result;
 };
 get('askForm').addEventListener('submit',e=>{e.preventDefault();renderAnswer(get('askText').value.trim())});
 panel.querySelectorAll('[data-question]').forEach(b=>b.addEventListener('click',()=>{get('askText').value=b.dataset.question;renderAnswer(b.dataset.question)}));
 get('askResponse').addEventListener('click',e=>{const b=e.target.closest('[data-audit-id]');if(b)showDetail('audit',b.dataset.auditId)});
 // Aktualizacja początkowej listy i wyników po sortowaniu.
 render();
})();