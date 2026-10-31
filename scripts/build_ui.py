#!/usr/bin/env python3
"""Rebuild a versioned HTML catalog payload and PWA manifest, without modifying historical records.
Usage: python scripts/build_ui.py --version 1.60.1
This appends a reviewed, offline-only JavaScript enhancement to the existing verified catalog.
"""
import argparse
import gzip
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--version',default='1.60.1')
    parser.add_argument('--base',default='data/katalog-v1.60.0.html.gz')
    args=parser.parse_args()
    if not re.fullmatch(r'\d+\.\d+\.\d+',args.version):
        raise SystemExit('Invalid release version')
    original=(ROOT/args.base)
    if not original.is_file():
        raise SystemExit('Missing baseline payload: '+str(original))
    html=gzip.decompress(original.read_bytes()).decode('utf-8')
    js=(ROOT/'scripts/ui_extensions_v1_60_1.js').read_text(encoding='utf-8')
    if html.count('</body></html>')!=1 or 'const DATA=window.ASM_DATA' not in html:
        raise SystemExit('Unexpected baseline HTML structure')
    if 'sortOrder' in html or 'id="askPanel"' in html:
        raise SystemExit('Baseline already includes these UI controls — reconcile manually before building')
    if '</script>' in js.lower():
        raise SystemExit('Unsafe closing script token in extension file')
    html=html.replace('</body></html>','<script>\n'+js+'\n</script></body></html>')
    dst='data/katalog-v'+args.version+'.html.gz'
    out=(ROOT/dst)
    out.parent.mkdir(parents=True,exist_ok=True)
    content=gzip.compress(html.encode('utf-8'),compresslevel=9,mtime=0)
    out.write_bytes(content)
    digest=hashlib.sha256(content).hexdigest()
    mpath=ROOT/'version.json'
    manifest=json.loads(mpath.read_text(encoding='utf-8'))
    manifest['version']=args.version
    manifest['ui_version']=args.version
    manifest['data_version']='1.60.0'
    manifest['published']=date.today().isoformat()
    manifest['payload']=dst
    manifest['payload_sha256']=digest
    mpath.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    swpath=ROOT/'sw.js'
    sw=swpath.read_text(encoding='utf-8')
    sw=re.sub(r"const CACHE_TAG='[^']+';",f"const CACHE_TAG='asystent-radnego-{args.version}-ui';",sw,count=1)
    sw=re.sub(r'\./data/katalog-v\d+\.\d+\.\d+\.html\.gz','./'+dst,sw,count=1)
    swpath.write_text(sw,encoding='utf-8')
    indexpath=ROOT/'index.html'
    index=indexpath.read_text(encoding='utf-8')
    index=index.replace("'Malbork · baza '+m.version+' · '+(m.published||'')", "'Malbork · aplikacja '+m.version+' · dane '+(m.data_version||m.version)")
    indexpath.write_text(index,encoding='utf-8')
    assert gzip.decompress(out.read_bytes()).decode('utf-8').count('id="sortOrder"')==1
    assert gzip.decompress(out.read_bytes()).decode('utf-8').count("panel.id='askPanel'")==1
    print(json.dumps({'version':args.version,'payload':dst,'bytes':len(content),'sha256':digest,'data_version':manifest['data_version']},ensure_ascii=False))
if __name__=='__main__':main()