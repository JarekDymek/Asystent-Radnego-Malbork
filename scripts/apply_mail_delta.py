"""Append a reviewed Gmail batch (public metadata only) to the operational index.
Does not OCR. Existing records are preserved. Linking is by explicit question ID.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,sqlite3,shutil

def apply(db_path:Path, json_path:Path, *, private:bool):
 batch=json.loads(json_path.read_text(encoding='utf8'))
 c=sqlite3.connect(db_path)
 c.execute('PRAGMA busy_timeout=30000')
 c.execute('''CREATE TABLE IF NOT EXISTS mail_documents (
  document_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, source_sha256 TEXT NOT NULL,
  email_date TEXT, letter_date TEXT, session TEXT, councillor TEXT, topic TEXT,
  page_start INTEGER, page_end INTEGER, source_pdf TEXT,
  source_status TEXT, fulltext_status TEXT, brief_summary TEXT, publication_policy TEXT)''')
 c.execute('''CREATE TABLE IF NOT EXISTS mail_response_links (
  document_id TEXT NOT NULL, interpelacja_id TEXT NOT NULL, answer_id TEXT NOT NULL,
  verification TEXT NOT NULL, PRIMARY KEY(document_id,interpelacja_id))''')
 counts={'documents_added':0,'answers_added':0,'case_links_added':0,'unmatched':0,'existing_skipped':0}
 existing={r[0]:(r[1],r[2],r[3]) for r in c.execute('SELECT interpelacja_id,radny,temat,radny_id FROM op_cases')}
 answers_existing={r[0] for r in c.execute('select odpowiedz_id from op_answers')}
 for item in batch['letters']:
  did=item['id'];links=item['question_ids']; start=min(item['pdf_pages']);end=max(item['pdf_pages']);
  source_id='GMAIL-DOC-20261110-P'+str(start).zfill(2)
  if c.execute('SELECT 1 FROM mail_documents WHERE document_id=?',(did,)).fetchone():counts['existing_skipped']+=1;continue
  c.execute('''INSERT INTO mail_documents VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(
    did,source_id,item['original_pdf_sha256'],item['email_date'],item['letter_date'],
    item['session'],item['councillor'],item['topic'],start,end,item['source_pdf'],
    item['review_status'],item['fulltext_status'],item.get('brief_summary',''),item['publication_policy']))
  counts['documents_added']+=1
  if not links:counts['unmatched']+=1
  for n,qid in enumerate(links,1):
   assert qid in existing,(did,qid)
   assert existing[qid][0]==item['councillor'],(qid,existing[qid][0],item['councillor'])
   answer_id=f'ODP-MAIL-20261110-P{start:02d}-Q{n}'
   c.execute('INSERT INTO mail_response_links VALUES (?,?,?,?)',(did,qid,answer_id,'recipient, session and subject checked visually against scan'))
   counts['case_links_added']+=1
   if answer_id not in answers_existing:
    snippet=item.get('brief_summary') or f"Potwierdzono skan pisemnej odpowiedzi ({start}–{end} strona pakietu z 10.11.2026). Pełna transkrypcja pozostaje do wykonania."
    c.execute('''INSERT INTO op_answers(odpowiedz_id,interpelacja_id,radny_id,radny,data,sesja,temat_interpelacji,autor,tresc_z_rejestru,zrodlo_id,url,status,uwagi) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',(
     answer_id,qid,existing[qid][2],item['councillor'],item['letter_date'],item['session'],existing[qid][1],
     'Burmistrz Miasta Malborka i/lub jednostka wskazana w załączniku',snippet,source_id,'',
     'Pismo zweryfikowane na skanie; brak pełnej transkrypcji',
     f'Dokument {did}, strony {start}-{end} pakietu PDF, mail 10.11.2026. Nie traktować streszczenia jako dosłownego cytatu.'))
    counts['answers_added']+=1
   past=c.execute('SELECT odpowiedzi_id,daty_odpowiedzi FROM op_cases WHERE interpelacja_id=?',(qid,)).fetchone()
   old_ids=(past[0] or '').split(' | ') if past else []
   old_ids=[x for x in old_ids if x]
   if answer_id not in old_ids:old_ids.append(answer_id)
   dates=[x for x in (past[1] or '').split(' | ') if x]
   if item['letter_date'] not in dates:dates.append(item['letter_date'])
   c.execute('UPDATE op_cases SET odpowiedzi_id=?,daty_odpowiedzi=?,kontrola_odpowiedzi=? WHERE interpelacja_id=?',(
    ' | '.join(old_ids),' | '.join(dates),'Odpowiedź pisemna z Gmail 10.11.2026: istnienie potwierdzone, pełna treść do odczytu',qid))
 c.execute('CREATE INDEX IF NOT EXISTS idx_mail_documents_letter_date ON mail_documents(letter_date)')
 c.execute('CREATE INDEX IF NOT EXISTS idx_mail_links_case ON mail_response_links(interpelacja_id)')
 c.execute('CREATE TABLE IF NOT EXISTS data_updates (update_id TEXT PRIMARY KEY, date TEXT, status TEXT, document_count INTEGER, matched_count INTEGER, unmatched_count INTEGER, source_sha256 TEXT, notes TEXT)')
 c.execute('INSERT OR REPLACE INTO data_updates VALUES (?,?,?,?,?,?,?,?)',(
  'MAIL-20261110','2026-11-10','Częściowa walidacja: zweryfikowane przypisanie, pełna treść do transkrypcji',
  len(batch['letters']),sum(bool(d['question_ids']) for d in batch['letters']),
  sum(not d['question_ids'] for d in batch['letters']),batch['source_pdf_sha256'],
  'Pismo wielotematyczne może łączyć kilka interpelacji. Archiwalne PDF-y tylko w prywatnej Bibliotece.'))
 if private:
  # Private archive holds only source locator; public publishing must not include messages or nonpublic PDF scans.
  c.execute('''CREATE TABLE IF NOT EXISTS private_mail_provenance (batch_id TEXT PRIMARY KEY, thread_id TEXT, mail_date TEXT, source_pdf TEXT, sha256 TEXT)''')
  c.execute('INSERT OR REPLACE INTO private_mail_provenance VALUES (?,?,?,?,?)',(
    'MAIL-20261110',batch['source_email_thread_id'],batch['source_email_ts'],
    batch['letters'][0]['source_pdf'],batch['source_pdf_sha256']))
 c.commit()
 out=c.execute('PRAGMA integrity_check').fetchone()[0]
 assert out=='ok',out
 counts['total_op_answers']=c.execute('select count(*) from op_answers').fetchone()[0]
 counts['total_op_cases']=c.execute('select count(*) from op_cases').fetchone()[0]
 counts['total_documents']=c.execute('select count(*) from mail_documents').fetchone()[0]
 c.close()
 return counts

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--sqlite',required=True);p.add_argument('--delta',required=True);p.add_argument('--private',action='store_true');a=p.parse_args()
 print(json.dumps(apply(Path(a.sqlite),Path(a.delta),private=a.private),ensure_ascii=False))