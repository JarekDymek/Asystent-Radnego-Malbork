import hashlib, json, gzip, sqlite3, tempfile
from pathlib import Path

r=Path(__file__).resolve().parent.parent
m=json.loads((r/'version.json').read_text(encoding='utf-8'))
for name,digest in [(m['payload'],m['payload_sha256']),(m['database'],m['database_sha256'])]:
    blob=(r/name).read_bytes()
    assert hashlib.sha256(blob).hexdigest()==digest, f'Błędny SHA256: {name}'
    data=gzip.decompress(blob)
    if name.endswith('html.gz'):assert b'Asystent Radnego' in data and b'</html>' in data
    else:
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'data.sqlite';p.write_bytes(data)
            c=sqlite3.connect(p)
            assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
            actual={table:c.execute(f'SELECT count(*) FROM {table}').fetchone()[0] for table in ['op_cases','op_answers','op_ballots','op_named_votes','au_acts']}
            c.close()
            assert actual['op_cases']==m['statistics']['interpelacje']
            assert actual['op_answers']==m['statistics']['odpowiedzi']
            assert actual['op_ballots']==m['statistics']['glosowania']
            assert actual['op_named_votes']==m['statistics']['glosy_imienne']
            assert actual['au_acts']==m['statistics']['akty_audytu']
            print('Kontrola SQLite:',actual)
print('Manifest, gzip, SHA256 i integralność SQLite: OK')
