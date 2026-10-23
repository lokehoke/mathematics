#!/usr/bin/env python3
"""Download actually linked author-hosted variants for selected gap years."""
import concurrent.futures,hashlib,json,re,subprocess
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from download_russia import ROOT,BASE,fetch,decode,metadata,output_path,save_json

def main():
    page='https://mathus.ru/math/';res=fetch(page)
    if not res['ok']:raise RuntimeError(res.get('error'))
    soup=BeautifulSoup(decode(res['data'],res['content_type']),'html.parser')
    targets={'phystech':{2022},'pvg':{2010,2012,2015,2020,2026},'rosatom':{2011,2012,2015,2026}}
    jobs={}
    for a in soup.select('a[href]'):
        u=urljoin(page,a['href']);match=re.search(r'/(Phystech|PVG|Rosatom)(20\d{2})[^/]*\.pdf$',u,re.I)
        if not match:continue
        cid=match[1].lower();year=int(match[2])
        if year not in targets[cid]:continue
        row=metadata(u,a.get_text(' ',strip=True),'','');row['year']=year
        jobs[u]=(cid,row)
    manifests={cid:json.loads((BASE/cid/'manifest.json').read_text()) for cid in targets}
    records={cid:{r['url']:r for r in m['documents']} for cid,m in manifests.items()}
    def one(item):
        u,(cid,md)=item
        old=records[cid].get(u)
        if old and old['status']=='downloaded':return cid,old
        row=dict(url=u,contest=manifests[cid]['contest'],subject='mathematics',source_page=page,source_status='public author-maintained educational archive',**md);r=fetch(u,35)
        if not r['ok']:return cid,dict(row,status='failed',error=r.get('error'))
        if not r['data'].startswith(b'%PDF'):return cid,dict(row,status='failed',error='Expected PDF')
        p=output_path(BASE/cid/'documents',u);p.write_bytes(r['data'])
        text=subprocess.run(['/usr/bin/pdftotext','-layout',str(p),'-'],capture_output=True,text=True,timeout=30).stdout
        row['document_type']='tasks_and_solutions' if re.search(r'(?mi)^\s*(?:Ответ(?:ы)?|Решение)\s*[.:]',text) else 'tasks'
        row.update(status='downloaded',local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(r['data']).hexdigest(),bytes=len(r['data']),final_url=r['final_url'],solution_status='Short numerical answers may be embedded; no full worked-solution set asserted')
        return cid,row
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        for cid,row in ex.map(one,jobs.items()):records[cid][row['url']]=row
    for cid,m in manifests.items():
        m['documents']=list(records[cid].values());m['mathus_gap_pass']=dict(source=page,target_years=sorted(targets[cid]),downloaded=sum(r['status']=='downloaded' for u,(c,_) in jobs.items() if c==cid for r in [records[cid][u]]));save_json(BASE/cid/'manifest.json',m)
        print(cid,m['mathus_gap_pass'],flush=True)

if __name__=='__main__':main()
