"""Publish a new curated dataset as two versioned .gz files.

This command only prepares/validates local files. It does NOT fetch BIP, change GitHub,
or assert that documents were legally verified. Run scripts/verify.py, then commit/push.
"""
import argparse, datetime, gzip, hashlib, json, re, sqlite3, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
TABLES=['op_councillors','op_cases','op_answers','op_resolutions','op_ballots','op_named_votes',
 'op_party_votes','op_club_votes_historical','op_link_proofs','op_issues','op_session_coverage',
 'au_acts','au_provisions','au_relations','au_findings','incoming_sources',
 'incoming_link_candidates','incoming_visual_review']
KEYS=[('op_councillors','radny_id'),('op_cases','radny_id'),('op_cases','interpelacja_id'),
 ('op_answers','interpelacja_id'),('op_ballots','glosowanie_id'),('op_named_votes','glosowanie_id'),
 ('op_named_votes','radny_id'),('op_resolutions','numer_uchwaly'),('au_acts','act_id'),
 ('au_acts','topic'),('au_provisions','act_id'),('au_relations','newer_id'),
 ('au_relations','older_id'),('au_findings','act_a'),('au_findings','act_b'),
 ('incoming_sources','sha256')]
def gzbytes(data):return gzip.compress(data,compresslevel=9,mtime=0)
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser(description='Budowa nowej wersji katalogu PWA')
 p.add_argument('--html',required=True,type=Path,help='Sprawdzony HTML z indeksem')
 p.add_argument('--sqlite',required=True,type=Path,help='Oryginalny, zweryfikowany centralny SQLite')
 p.add_argument('--version',required=True,help='Numer SemVer, np. 1.60.1')
 p.add_argument('--date',default=datetime.date.today().isoformat(),help='Data YYYY-MM-DD')
 args=p.parse_args()
 if not re.fullmatch(r'\d+\.\d+\.\d+',args.version):p.error('Wymagany numer X.Y.Z')
 if args.version==json.loads((ROOT/'version.json').read_text(encoding='utf-8'))['version']:
  p.error('Nowa wersja nie może mieć tego samego numeru co poprzednia')
 payload_name=f'data/katalog-v{args.version}.html.gz'
 database_name=f'data/katalog-operacyjny-v{args.version}.sqlite.gz'
 html=args.html.read_bytes()
 if b'Asystent Radnego' not in html or b'</html>' not in html:p.error('Niepoprawny dokument HTML')
 # Isolation: never mutate the original source SQL database.
 with tempfile.TemporaryDirectory() as t:
  db=Path(t)/'operational.sqlite'
  connection=sqlite3.connect(db)
  connection.execute('ATTACH DATABASE ? AS src',(str(args.sqlite.resolve()),))
  for table in TABLES:
   connection.execute(f'CREATE TABLE "{table}" AS SELECT * FROM src."{table}"')
  for table,key in KEYS:
   connection.execute(f'CREATE INDEX "idx_{table}_{key}" ON "{table}"("{key}")')
  connection.execute('CREATE TABLE build_meta (key TEXT PRIMARY KEY,value TEXT)')
  for k,v in [('snapshot_version',args.version),('snapshot_date',args.date),
               ('origin',args.sqlite.name)]:connection.execute('INSERT INTO build_meta VALUES (?,?)',(k,v))
  connection.commit()
  assert connection.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
  counts={table:connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] for table in TABLES}
  connection.close()
  sqlite_data=db.read_bytes()
 pl_data=gzbytes(html); db_data=gzbytes(sqlite_data)
 (ROOT/payload_name).write_bytes(pl_data)
 (ROOT/database_name).write_bytes(db_data)
 manifest={'version':args.version,'revision':args.date,'published':args.date,
  'dataset':'IX kadencja Rady Miasta Malborka · Audyt Uchwał',
  'payload':payload_name,'payload_sha256':sha(pl_data),
  'database':database_name,'database_sha256':sha(db_data),
  'statistics':{'interpelacje':counts['op_cases'],'odpowiedzi':counts['op_answers'],
    'glosowania':counts['op_ballots'],'glosy_imienne':counts['op_named_votes'],
    'uchwaly':counts['op_resolutions'],'akty_audytu':counts['au_acts']}}
 (ROOT/'version.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 sw=(ROOT/'sw.js').read_text(encoding='utf-8')
 sw=re.sub(r"const CACHE_TAG='[^']+'",f"const CACHE_TAG='asystent-radnego-{args.version}-{args.date.replace('-','')}'",sw,count=1)
 sw=re.sub(r"'\./data/katalog-v[^']+html.gz'",f"'./{payload_name}'",sw,count=1)
 (ROOT/'sw.js').write_text(sw,encoding='utf-8')
 print('Gotowe:',args.version,counts,'— uruchom scripts/verify.py i wykonaj git push')
if __name__=='__main__':main()