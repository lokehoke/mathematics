#!/usr/bin/env python3
"""Recover mathematics-only papers from the historical organizer archive.

Follow published annual/task links. Never ingest whole multidisciplinary books,
participant scripts, result lists or unrelated subject papers.
"""
import concurrent.futures, datetime, hashlib, json, re
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from download_russia import ROOT, BASE, fetch, decode, output_path, save_json

ROOT_URL='https://old.turlom.olimpiada.ru/old'
MATH=re.compile(r'(?:math|(?:tl\d{4}|[/_-])mat(?:[._-]|$)|математик)',re.I)
ADMIN=re.compile(r'spis|rezult|protokol|protocol|priz|diplom|nagraz|result|списк|награж',re.I)

def main():
    folder=BASE/'turlom';mf=folder/'manifest.json';m=json.loads(mf.read_text())
    records={r['url']:r for r in m['documents']};indexes={r['url']:r for r in m.get('indexes',[])}
    queue=deque([(ROOT_URL,None,None,0)]);seen=set();assets={};failures=[];html_material={}
    def index(item):
        u,year,stage,depth=item
        p=output_path(folder/'indexes',u,'.html')
        old=indexes.get(u,{})
        # Relative links on redirecting directory indexes need their actual
        # trailing-slash base. A cache without it must be refreshed once.
        if p.exists() and (old.get('final_url') or not re.search(r'/(?:zadanija|html)$',u)):
            return item,dict(ok=True,data=p.read_bytes(),content_type='text/html',final_url=old.get('final_url',u))
        return item,fetch(u,20)
    while queue and len(seen)<200:
        batch=[]
        while queue and len(batch)<4:
            item=queue.popleft()
            if item[0] not in seen:seen.add(item[0]);batch.append(item)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(index,batch))
        for (u,year,stage,depth),res in results:
            if not res['ok']:failures.append(dict(url=u,error=res.get('error')));continue
            data=res['data'];p=output_path(folder/'indexes',u,'.html');p.write_bytes(data)
            indexes[u]=dict(url=u,final_url=res['final_url'],local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),status='downloaded',role='archive_index')
            soup=BeautifulSoup(decode(data,res['content_type']),'html.parser')
            text=soup.get_text(' ',strip=True)
            if year in [1978,1979,1980,1981,1983,1990] and len(text)>1000 and re.search(r'Математика',text) and not re.search(r'Физика|Химия|Биология|Астрономия|Лингвистика|Литература|История',text):
                kind='tasks_and_solutions' if re.search(r'Решени[ея]|Ответ[ы:]',text) else 'tasks'
                assets[u]=dict(url=u,contest=m['contest'],subject='mathematics',year=str(year),stage='autumn',classes=None,document_type=kind,source_page=ROOT_URL,source_status='official_historical_organizer_archive',metadata_evidence='Original annual HTML contains mathematics statements, not just archive links; no other subject sections found.')
                html_material[u]=data
            for a in soup.select('a[href]'):
                v=urljoin(res['final_url'],a['href']).split('#')[0];label=a.get_text(' ',strip=True)
                if urlsplit(v).netloc not in ['old.turlom.olimpiada.ru','turlom.olimpiada.ru','olympiads.mccme.ru']:continue
                if v.startswith('http://'):v='https://'+v[7:]
                # The organizer moved the historic site; absolute links in the
                # preserved pages still point at the now-empty current host.
                published=v
                if urlsplit(v).netloc=='turlom.olimpiada.ru':v=v.replace('https://turlom.olimpiada.ru/','https://old.turlom.olimpiada.ru/',1)
                path=urlsplit(v).path
                if path.lower().endswith('.pdf'):
                    if not MATH.search(path) or ADMIN.search(path):continue
                    explicit=re.search(r'(?:tl|turlom)[-_]?((?:19|20)\d{2})',path,re.I)
                    y=int(explicit[1]) if explicit else year
                    if not y:continue
                    kind='solutions' if re.search(r'sol|otv|решени|ответ',path+' '+label,re.I) else 'marking_scheme' if re.search(r'crit|krit|критер',path+' '+label,re.I) else 'tasks'
                    assets.setdefault(v,dict(url=v,published_link=published,contest=m['contest'],subject='mathematics',year=str(y),stage=stage or 'autumn',classes=None,document_type=kind,label=label,source_page=u,source_status='official_historical_organizer_archive',metadata_evidence='Mathematics-specific filename on linked annual task page; calendar year of round, not academic season.'))
                    continue
                if depth>=3 or ADMIN.search(path) or re.search(r'adresa|raboty',path,re.I):continue
                if Path(path).suffix.lower() not in ['', '.html','.htm']:continue
                yr=year;st=stage
                if u==ROOT_URL:
                    if not (re.search(r'/\d+turnir(?:-final)?$',path) or re.search(r'/turlom/\d{4}/index\.html?$',path) or re.search(r'Заключительный Тур',label)):continue
                    ym=re.search(r'(?:19|20)\d{2}',label)
                    if not ym:continue
                    yr=int(ym[0]);st='final' if 'Заключительный' in label else 'autumn'
                elif not re.search(r'zadan|tasks|final|/html/?$|(?:math|mat)\.html?$',path,re.I):continue
                if v not in seen:queue.append((v,yr,st,depth+1))
        print('indexes',len(seen),'queued',len(queue),'math documents',len(assets),flush=True)
    def download(row):
        old=records.get(row['url'])
        if old and old.get('status')=='downloaded' and old.get('local_path') and (ROOT/old['local_path']).is_file():
            return dict(old,**{k:v for k,v in row.items() if k not in ['label']})
        res=dict(ok=True,data=html_material[row['url']],final_url=row['url'],content_type='text/html') if row['url'] in html_material else fetch(row['url'],25)
        if not res['ok']:return dict(row,status='failed',error=res.get('error'))
        data=res['data']
        if row['url'] not in html_material and not data.startswith(b'%PDF'):return dict(row,status='failed',error='Invalid PDF signature')
        p=output_path(folder/'documents',row['url'],'.html' if row['url'] in html_material else None);p.write_bytes(data)
        return dict(row,status='downloaded',local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),final_url=res['final_url'],content_type=res['content_type'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for row in pool.map(download,assets.values()):records[row['url']]=row
    m['documents']=list(records.values());m['indexes']=list(indexes.values())
    m['historical_math_pass']=dict(source=ROOT_URL,index_pages=len(seen),pending_index_pages=[x[0] for x in queue],discovered_math_documents=len(assets),downloaded=sum(records[u].get('status')=='downloaded' for u in assets),failures=failures,updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save_json(mf,m);print(m['historical_math_pass'],flush=True)

if __name__=='__main__':main()
