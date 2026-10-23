#!/usr/bin/env python3
"""Recover official mathematics papers after the SFU domain migration.

Exclude results and participant scripts. Keep only linked mathematics sections.
"""
import concurrent.futures, hashlib, json, re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from download_russia import ROOT, BASE, fetch, decode, metadata, output_path, save_json, EXT

def main():
    root='https://dovuz.sfu.ru/abiturientu-sfu/olimpiady/belchonok/arkhiv/'
    mf=BASE/'belchonok/manifest.json';m=json.loads(mf.read_text());records={r['url']:r for r in m['documents']};indexes={r['url']:r for r in m['indexes']}
    res=fetch(root)
    if not res['ok']:raise RuntimeError(res.get('error'))
    soup=BeautifulSoup(decode(res['data'],res['content_type']),'html.parser');pages=set()
    excluded=r'raboty|rezultat|pobedit|prizer|rabot[_/-]|rez[_/-]'
    for a in soup.select('a[href]'):
        u=urljoin(root,a['href'])
        if not u.startswith(root) or re.search(excluded,u,re.I):continue
        if 'matematik' in u.lower():pages.add(u)
    print('Mathematics pages:',len(pages),flush=True)
    jobs={};failures=[]
    def page(u):return u,fetch(u)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for u,r in ex.map(page,sorted(pages)):
            if not r['ok']:failures.append(dict(url=u,error=r.get('error')));continue
            p=output_path(BASE/'belchonok/indexes',u,'.html');p.write_bytes(r['data']);indexes[u]=dict(url=u,local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(r['data']).hexdigest(),status='downloaded',role='archive_index')
            s=BeautifulSoup(decode(r['data'],r['content_type']),'html.parser')
            pair=re.search(r'((?:19|20)\d{2})-((?:19|20)\d{2})',u)
            year=f'{pair[1]}/{pair[2]}' if pair else None
            if not year:
                match=re.search(r'/((?:19|20)\d{2})-god/',u)
                if match:year=int(match[1])
            for a in s.select('a[href]'):
                v=urljoin(r['final_url'],a['href'])
                if not EXT.search(v) or '/upload/' not in v:continue
                if urlsplit(v).netloc not in ['dovuz.sfu.ru','dovuz.sfu-kras.ru']:continue
                h=a.find_previous(['h2','h3','h4']);heading=h.get_text(' ',strip=True) if h else ''
                md=metadata(v,a.get_text(' ',strip=True),heading,'')
                md['year']=year;md['stage']='final' if re.search(r'zak|заключ',u,re.I) else 'qualifying' if re.search(r'otb|отбор',u,re.I) else None
                jobs.setdefault(v,dict(url=v,contest=m['contest'],subject='mathematics',source_page=u,source_status='official organizer; migrated SFU domain',**md))
    def one(item):
        u,row=item
        old=records.get(u)
        if old and old.get('status')=='downloaded' and (ROOT/old['local_path']).is_file():return old
        r=fetch(u,40)
        if not r['ok']:return dict(row,status='failed',error=r.get('error'))
        if u.lower().endswith('.pdf') and not r['data'].startswith(b'%PDF'):return dict(row,status='failed',error='Expected PDF signature')
        if u.lower().endswith('.zip') and not r['data'].startswith(b'PK'):return dict(row,status='failed',error='Expected ZIP signature')
        p=output_path(BASE/'belchonok/documents',u);p.write_bytes(r['data'])
        return dict(row,status='downloaded',local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(r['data']).hexdigest(),bytes=len(r['data']),final_url=r['final_url'],content_type=r['content_type'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        for r in ex.map(one,jobs.items()):records[r['url']]=r
    m['documents']=list(records.values());m['indexes']=list(indexes.values());m['migrated_domain_pass']=dict(source=root,pages=len(pages),discovered_documents=len(jobs),failures=failures)
    save_json(mf,m);print('Documents',len(jobs),'downloaded',sum(records[u]['status']=='downloaded' for u in jobs),flush=True)

if __name__=='__main__':main()
