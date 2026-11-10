#!/usr/bin/env python3
"""Publish reviewed *public metadata only*, keep Gmail scans in private Library.
Builds a new immutable PWA HTML+SQLite snapshot from last verified release.
Never reaches Gmail and never uploads private PDF or Gmail messages to GitHub.
"""
import argparse,gzip,hashlib,json,re,sqlite3,tempfile
from pathlib import Path
from datetime import date
from apply_mail_delta import apply

ROOT=Path(__file__).resolve().parent.parent

def sha(b):return hashlib.sha256(b).hexdigest()
def gz(b):return gzip.compress(b,compresslevel=9,mtime=0)
def fileversion(path):return re.search(r'v(\d+\.\d+\.\d+)',str(path)).group(1)

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--version',default='1.61.0')
 p.add_argument('--payload-baseline',default='data/katalog-v1.60.1.html.gz')
 p.add_argument('--sqlite-baseline',default='data/katalog-operacyjny-v1.60.0.sqlite.gz')
 p.add_argument('--delta',default='data/odpowiedzi_2026-11-10_public.json')
 a=p.parse_args()
 assert re.fullmatch(r'\d+\.\d+\.\d+',a.version)
 source=json.loads((ROOT/a.delta).read_text(encoding='utf8'))
 assert source['letters_count']==len(source['letters']) and source['verified_case_links']>=1
 assert all('thread_id' not in json.dumps(d) and 'gmail.com' not in json.dumps(d) for d in source['letters'])
 # The baseline is an independently verified release; never mutate it.
 with tempfile.TemporaryDirectory() as t:
  dbfile=Path(t)/'stage.sqlite'
  dbfile.write_bytes(gzip.decompress((ROOT/a.sqlite_baseline).read_bytes()))
  stats=apply(dbfile,ROOT/a.delta,private=False)
  assert stats['documents_added']==source['letters_count'] or stats['existing_skipped']==source['letters_count'],stats
  assert stats['total_op_cases']==817,stats
  con=sqlite3.connect(dbfile)
  dbmeta={row[0]:row[1] for row in con.execute('select key,value from build_meta')}
  con.execute("INSERT OR REPLACE INTO build_meta(key,value) VALUES('snapshot_version',?)",(a.version,))
  con.execute("INSERT OR REPLACE INTO build_meta(key,value) VALUES('snapshot_date',?)",(source['revision'],))
  con.commit()
  assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
  def rows(t):
   cur=con.execute('SELECT * FROM '+t)
   names=[x[0] for x in cur.description]
   return [dict(zip(names,r)) for r in cur.fetchall()]
  cases=rows('op_cases');answers=rows('op_answers');mail=rows('mail_documents')
  assert len(mail)==source['letters_count'] and len(answers)==677+source['verified_links_total'],(len(mail),len(answers))
  con.close()
  dbbytes=dbfile.read_bytes()
 # Replace only the source JSON in the existing, tested HTML+JS; retain date sorting and Q&A.
 html=gzip.decompress((ROOT/a.payload_baseline).read_bytes()).decode('utf8')
 tag='window.ASM_DATA='
 pos=html.index(tag)+len(tag)
 decoder=json.JSONDecoder()
 bundle,end=decoder.raw_decode(html[pos:])
 assert len(bundle['cases'])==817 and len(bundle['answers'])==677
 bundle['cases']=cases;bundle['answers']=answers
 bundle['mail_updates']=source['letters']
 bundle['snapshot_version']=a.version
 bundled=json.dumps(bundle,ensure_ascii=False,separators=(',',':'))
 html=html[:pos]+bundled+html[pos+end:]
 assert 'id="sortOrder"' in html and "panel.id='askPanel'" in html
 assert html.count('window.ASM_DATA=')==1
 assert '<!-- app-end -->' not in html
 data_name=f'data/katalog-v{a.version}.html.gz'
 db_name=f'data/katalog-operacyjny-v{a.version}.sqlite.gz'
 htmlcompressed=gz(html.encode('utf8'));dbcompressed=gz(dbbytes)
 (ROOT/data_name).write_bytes(htmlcompressed)
 (ROOT/db_name).write_bytes(dbcompressed)
 # Manifest and change log may be publicly consumed; never include Gmail URLs or PDF scans.
 manifest=json.loads((ROOT/'version.json').read_text(encoding='utf8'))
 manifest.update(version=a.version,ui_version=a.version,data_version=a.version,revision=source['revision'],published=source['revision'],payload=data_name,payload_sha256=sha(htmlcompressed),database=db_name,database_sha256=sha(dbcompressed))
 manifest['statistics']['odpowiedzi']=len(answers)
 manifest['recent_update']={
  'id':'MAIL-20261110', 'date':'2026-11-10','heading':'Nowe odpowiedzi na interpelacje',
  'new_letters':len(mail),'linked_letters':source['verified_case_links'],
  'linked_cases':source['verified_links_total'],'unmatched_letters':source['unmatched_letters'],
  'summary':'Z poczty Rady Miasta dodano metadane 32 nowych pism; 30 przypisano do konkretnych interpelacji. Pełne teksty 55 zeskanowanych stron wymagają dalszej transkrypcji.',
  'notice':'Baza zaktualizowana. Do pełnego zamknięcia potrzebna jest transkrypcja i rozstrzygnięcie 2 nieprzypisanych pism.',
  'samples':[{'person':'Marta Dorobek','topic':'RedLight i spotkania o autyzmie'},
             {'person':'Jarosław Dymek','topic':'Bezpieczeństwo przy szkołach i Park Kieszonkowy'},
             {'person':'Małgorzata Sobczak','topic':'Zadłużenie zasobu komunalnego'}]}
 (ROOT/'version.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 # UI update panel, visible and dismissible. Use safe textContent, not HTML with source fields.
 ipath=ROOT/'index.html'
 index=ipath.read_text(encoding='utf8')
 if 'id="newDataButton"' not in index:
  index=index.replace('<button type="button" class="btn" id="updateButton"', '<button type="button" class="btn new" id="newDataButton" hidden>Nowe dane</button>\n <button type="button" class="btn" id="updateButton"')
  index=index.replace('<div id="message" role="status" hidden></div>','<div id="message" role="status" hidden></div>\n<section id="newDataPanel" class="new-data-panel" hidden role="region" aria-label="Informacje o aktualizacji bazy"><div class="new-data-inner"><button type="button" id="closeNews" class="btn">Zamknij / przeczytane</button><h2 id="newsTitle"></h2><p id="newsSummary"></p><p id="newsNotice"></p><ul id="newsSamples"></ul><small>Oryginały źródeł są w prywatnej Bibliotece. Tu udostępniane są tylko metadane.</small></div></section>')
  index=index.replace('</style>','\n.new-data-panel{position:fixed;z-index:50;top:65px;left:0;right:0;max-height:75vh;overflow-y:auto;background:#ebf5ff;color:#14314c;border-bottom:3px solid #2b739d;box-shadow:0 8px 28px #0004;padding:14px}\n.new-data-inner{max-width:780px;margin:auto;line-height:1.5}.new-data-inner h2{margin:.2em 0}.new-data-inner #closeNews{float:right}.new-data-inner p{margin:8px 0}.new-data-inner ul{padding-left:22px}.new-data-inner small{color:#48647b}\n@media(max-width:450px){#newDataButton{font-size:11px;padding:6px}.brand strong{font-size:11px}.new-data-panel{top:65px}}\n</style>')
  injection='''\nfunction showLatestNews(m){
 const a=m.recent_update;const b=q('newDataButton');
 if(!a)return;
 b.hidden=false;b.textContent='Nowe dane ('+a.new_letters+')';
 q('newsTitle').textContent=a.heading+' · '+a.date;
 q('newsSummary').textContent=a.summary;
 q('newsNotice').textContent=a.notice;
 const list=q('newsSamples');list.textContent='';
 for(const x of a.samples||[]){const li=document.createElement('li');li.textContent=x.person+': '+x.topic;list.appendChild(li)}
 if(localStorage.getItem('asm_read_update')!==a.id){q('newDataPanel').hidden=false;b.classList.add('new')}
 b.onclick=()=>{q('newDataPanel').hidden=!q('newDataPanel').hidden};
 q('closeNews').onclick=()=>{q('newDataPanel').hidden=true;localStorage.setItem('asm_read_update',a.id);b.classList.remove('new');b.textContent='Zmiany bazy'};
}
'''
  index=index.replace('async function loadData(m){',injection+'\nasync function loadData(m){')
  index=index.replace('q(\'placeholder\').hidden=true;label(m);','q(\'placeholder\').hidden=true;label(m);showLatestNews(m);')
 assert index.count('showLatestNews(m);')==1
 ipath.write_text(index,encoding='utf8')
 # SW must precache the new immutable dataset and revision manifest; keep older files for rollback.
 swpath=ROOT/'sw.js'
 sw=swpath.read_text(encoding='utf8')
 sw=re.sub(r"const CACHE_TAG='[^']+'",f"const CACHE_TAG='asystent-radnego-{a.version}-mail-20261110'",sw,count=1)
 sw=re.sub(r"'\./data/katalog-v\d+\.\d+\.\d+\.html.gz'",f"'./{data_name}'",sw,count=1)
 if f"'./{db_name}'" not in sw:
  sw=sw.replace(f"'./{data_name}'",f"'./{data_name}','./{db_name}','./{a.delta}'",1)
 swpath.write_text(sw,encoding='utf8')
 # public README tracks exactly what has changed and what remains unverified.
 (ROOT/'CHANGELOG.md').write_text('''# Asystent Radnego — zmiany\n\n## 1.61.0 (2026-11-10)\n\n- Zapisano **32 pisma** z pakietu odpowiedzi Biura Rady (55 stron PDF, oryginały w Bibliotece prywatnej).\n- **30 pism** powiązano z interpelacjami sesji XXXVI; **32 relacje** (jedno pismo obejmuje trzy pytania).\n- **2 pisma** pozostały w kolejce do ustalenia numeru sprawy.\n- Uzupełniono bazę operacyjną: 709 powiązanych rekordów odpowiedzi łącznie (677 wcześniej + 32 powiązania).\n- W aplikacji dodano widoczne powiadomienie „Nowe dane” i wykaz zmian.\n- **Ograniczenie:** skany nie zawierają warstwy tekstowej; poza jawnie sprawdzonymi fragmentami nie deklaruje się pełnych transkrypcji.\n- Nie publikowano plików z Gmaila ani korespondencji prywatnej.\n\n## 1.60.1 (2026-10-31)\n\n- Sortowanie po dacie i lokalne zadawanie pytań do audytu uchwał.\n''',encoding='utf8')
 print(json.dumps({'version':a.version,'import':stats,'html_bytes':len(htmlcompressed),'sqlite_bytes':len(dbcompressed),'source_mail_attachments_public':False,'sha':manifest['payload_sha256']},ensure_ascii=False))

if __name__=='__main__': main()