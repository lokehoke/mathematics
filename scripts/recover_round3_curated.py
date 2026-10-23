#!/usr/bin/env python3
"""Targeted, source-checked recovery of specific missing editions."""
import hashlib, json, re, subprocess
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from download_russia import ROOT, BASE, fetch, decode, output_path, save_json

def belchonok():
    # Exact published source page, not constructed document URLs.
    page='https://postypashki.ru/олимпиады/университетская-олимпиада-школьнико/'
    result=fetch(page)
    if not result['ok']:raise RuntimeError(result.get('error'))
    soup=BeautifulSoup(decode(result['data'],result['content_type']),'html.parser')
    mf=BASE/'belchonok/manifest.json';m=json.loads(mf.read_text());records={r['url']:r for r in m['documents']}
    count=0
    for tr in soup.select('tr'):
        text=tr.get_text(' ',strip=True);season=re.search(r'\b(20\d{2})[-–](20\d{2})\b',text)
        if not season or int(season[2]) not in [2018,2019,2020,2021]:continue
        for a in tr.select('a[href]'):
            u=urljoin(result['final_url'],a['href'])
            if '.pdf' not in u.lower():continue
            old=records.get(u)
            if old and old.get('status')=='downloaded':continue
            r=dict(url=u,contest=m['contest'],subject='mathematics',year=f'{season[1]}/{season[2]}',stage='final',classes='11',document_type='mathematics_material',source_page=page,source_status='public_secondary_archive',label=a.get_text(' ',strip=True),metadata_evidence='School year from source table row; default grade 11 stated above table')
            rr=fetch(u,35)
            if not rr['ok']:records[u]=dict(r,status='failed',error=rr.get('error'));continue
            if not rr['data'].startswith(b'%PDF'):records[u]=dict(r,status='failed',error='Expected PDF');continue
            p=output_path(BASE/'belchonok/documents',u);p.write_bytes(rr['data'])
            t=subprocess.run(['/usr/bin/pdftotext','-layout',str(p),'-'],capture_output=True,text=True).stdout
            if 'Бельчонок' not in t and 'БЕЛЬЧОНОК' not in t:records[u]=dict(r,status='failed',error='Contest title not verified');continue
            if re.search(r'ОТВЕТЫ И РЕШЕНИЯ|Ответ\s*[.:]|Решение\s*[.:]',t,re.I):r['document_type']='tasks_and_solutions'
            else:r['document_type']='tasks'
            r.update(status='downloaded',local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(rr['data']).hexdigest(),bytes=len(rr['data']),content_validation='PDF title and solution/answer text checked')
            records[u]=r;count+=1
    m['documents']=list(records.values());m['round3_curated_source']=page;save_json(mf,m);print('Belchonok new published PDFs:',count,flush=True)

def bmo2020():
    import download_international as di
    for line in di.MANIFEST.read_text().splitlines():
        r=json.loads(line);di.RECORDS[(r['contest'],str(r['year']),r['type'],r['source'])]=r
    page='https://bmo2020.ssmr.ro/problems';rr=fetch(page)
    if not rr['ok']:
        # Exact iframe target independently verified on the public official page.
        di.register('BMO',2020,'problems_and_solutions','https://bmo2020.ssmr.ro/sites/bmo2020.ssmr.ro/files/BMO_2020_paper_ENG.pdf',page,'en',source_status='official organizer',metadata_evidence='Exact iframe target verified by web index; index request timed out')
        di.run_downloads();di.save_manifest();return
    soup=BeautifulSoup(decode(rr['data'],rr['content_type']),'html.parser')
    for a in soup.select('iframe[src]'):
        u=urljoin(page,a['src'])
        if '.pdf' not in u.lower():continue
        di.register('BMO',2020,'problems_and_solutions',u,page,'en',source_status='official organizer',metadata_evidence='Problems and solutions iframe on official host page; PDF content checked')
    di.run_downloads();di.save_manifest()

if __name__=='__main__':belchonok();bmo2020()
