#!/usr/bin/env python3
"""Preserve openly published mathematics copies, with explicit secondary provenance."""
import argparse, concurrent.futures, hashlib, json, re
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, parse_qs
from bs4 import BeautifulSoup
from download_russia import ROOT, BASE, CONTESTS, fetch, metadata, output_path, save_json, decode, EXT

ACTIVITIES={'rosatom':411,'lomonosov':348,'pvg':115,'spbu':443,'belchonok':397,'bibn':360,'verchenko':24}

def collect(cid, activity, limit=600):
    folder=BASE/cid; mf=folder/'manifest.json'; m=json.loads(mf.read_text())
    records={r['url']:r for r in m['documents']}
    indexes={r['url']:r for r in m.get('indexes',[])}
    root=f'https://olimpiada.ru/activity/{activity}/tasks'
    queue=deque([root]); queued={root}; seen=set(); assets={}; failures=[]
    def get_index(u):
        old=indexes.get(u)
        if old and (ROOT/old['local_path']).is_file():
            return dict(ok=True,data=(ROOT/old['local_path']).read_bytes(),content_type='text/html',final_url=u)
        return fetch(u)
    while queue and len(seen)<limit:
        batch=[]
        while queue and len(batch)<4:batch.append(queue.popleft())
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:results=list(ex.map(get_index,batch))
        for u,res in zip(batch,results):
            seen.add(u)
            if not res['ok']:failures.append(res);continue
            data=res['data']; p=output_path(folder/'indexes',u,'.html'); p.write_bytes(data)
            indexes[u]=dict(url=u,local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),status='downloaded',role='archive_index')
            soup=BeautifulSoup(decode(data,res['content_type']),'html.parser')
            for a in soup.select('a[href]'):
                v=urljoin(res['final_url'],a['href']).split('#')[0]
                if EXT.search(v):
                    # Only this contest's curated mathematics archive copies.
                    if urlsplit(v).netloc not in ['tasks.olimpiada.ru','rsr-olymp.ru','olimpiada.ru'] or f'/tasks/{activity}/' not in v:continue
                    h=a.find_previous(['h2','h3','h4']); label=a.get_text(' ',strip=True)
                    md=metadata(v,label,h.get_text(' ',strip=True) if h else '','')
                    query=parse_qs(urlsplit(u).query)
                    if query.get('class') and not md['classes']:md['classes']=query['class'][0]
                    # The site's year directory can name the START of a school
                    # year; prefer an explicit two-digit pair in the filename.
                    pairs=re.findall(r'(?<!\d)(\d{2})[-_](\d{2})(?!\d)',urlsplit(v).path.rsplit('/',1)[-1])
                    pair=pairs[-1] if pairs else None
                    if pair and (int(pair[1])-int(pair[0]))%100==1:
                        first=2000+int(pair[0]); md['year']=f'{first}/{first+1}'
                    if re.search(r'taskssol|tasksans',v,re.I):md['document_type']='tasks_and_solutions'
                    if re.search(r'[-_]otbor[-_]',v,re.I):md['stage']='qualifying'
                    assets.setdefault(v,dict(url=v,contest=CONTESTS[cid]['name'],subject='mathematics',source_page=u,source_status='public_secondary_archive_attributing_organizer',**md))
                elif urlsplit(v).netloc=='olimpiada.ru' and re.fullmatch(f'/activity/{activity}/tasks(?:/\d{{4}})?',urlsplit(v).path):
                    if v not in queued:queued.add(v);queue.append(v)
        print(cid,'indexes',len(seen),'queued',len(queue),'documents',len(assets),flush=True)
    def download(item):
        u,row=item
        old=records.get(u)
        if old and old.get('status')=='downloaded' and old.get('local_path'):
            p=ROOT/old['local_path']
            if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==old.get('sha256'):
                old['year']=row['year'];return old
        res=fetch(u,30)
        derived=None
        if not res['ok'] and urlsplit(u).netloc=='rsr-olymp.ru':
            derived='https://tasks.olimpiada.ru'+urlsplit(u).path
            res=fetch(derived,30)
        if not res['ok']:return dict(row,status='failed',error=res.get('error'))
        data=res['data'];ext=Path(urlsplit(u).path).suffix.lower()
        if (ext=='.pdf' and not data.startswith(b'%PDF')) or (ext=='.zip' and not data.startswith(b'PK')):
            return dict(row,status='failed',error='Advertised file signature mismatch')
        p=output_path(folder/'documents',u);p.write_bytes(data)
        return dict(row,derived_retrieval_url=derived,status='downloaded',local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),final_url=res['final_url'],content_type=res['content_type'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for row in ex.map(download,assets.items()):records[row['url']]=row
    m['documents']=list(records.values());m['indexes']=list(indexes.values())
    m['secondary_archive_pass']=dict(source=root,pages=len(seen),remaining_pages=len(queue),discovered_documents=len(assets),failures=failures,updated_at=datetime.now(timezone.utc).isoformat())
    m['pending_documents']=[r for r in m.get('pending_documents',[]) if records.get(r['url'],{}).get('status')!='downloaded']
    save_json(mf,m)
    print(cid,'DONE',len(assets),'links',sum(records[u]['status']=='downloaded' for u in assets),'saved',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--contest',action='append',choices=sorted(ACTIVITIES));p.add_argument('--max-pages',type=int,default=600);args=p.parse_args()
    for cid in args.contest or ACTIVITIES:collect(cid,ACTIVITIES[cid],args.max_pages)
