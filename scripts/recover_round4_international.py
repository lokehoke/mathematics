#!/usr/bin/env python3
"""Recover public Finnish Baltic Way solutions and pinned RMM PDF mirrors."""
import concurrent.futures, json, re, subprocess
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import download_international as di
from download_russia import fetch

REV='830f8bbf36803ba30e092445c8ca47097e79f559'

def main():
    for line in di.MANIFEST.read_text().splitlines():
        r=json.loads(line);di.RECORDS[(r['contest'],str(r['year']),r['type'],r['source'])]=r
    candidates=[]
    index=f'https://huggingface.co/api/datasets/AI-MO/olympiads/tree/{REV}/RMM/raw'
    res=fetch(index,20)
    if not res['ok']:raise RuntimeError(res)
    for item in json.loads(res['data']):
        match=re.fullmatch(r'RMM/raw/en-(2018|2019|2024|2025)-(.+)\.pdf',item['path'])
        if not match:continue
        u=f"https://huggingface.co/datasets/AI-MO/olympiads/resolve/{REV}/{item['path']}"
        candidates.append(dict(contest='RMM',year=int(match[1]),kind='unclassified_mathematics_material',url=u,source_page=index,language='en',source_status='public_secondary_dataset_pdf_mirror',source_script_url=f'https://huggingface.co/datasets/AI-MO/olympiads/raw/{REV}/RMM/download_script/download.py',metadata_evidence='Published dataset file listing; verify PDF solution headings before typing.'))
    page='https://matematiikkakilpailut.fi/Baltian_tie/'
    res=fetch(page,20)
    if res['ok']:
        soup=BeautifulSoup(res['data'],'html.parser')
        for row in soup.select('div[role=listitem]'):
            cells=row.find_all('div',recursive=False)
            if len(cells)<5 or cells[0].get_text(strip=True)!='2009':continue
            # The fifth column is explicitly the solution column, not results.
            for a in cells[4].select('a[href]'):
                if a.get_text(strip=True)!='pdf':continue
                original=urljoin(page,a['href']);mid=re.search(r'/file/d/([^/]+)',original)
                if mid:
                    candidates.append(dict(contest='BalticWay',year=2009,kind='solutions',url=f'https://drive.google.com/uc?export=download&id={mid[1]}',source_page=page,language='fi',published_link=original,source_authority='Finnish Mathematical Society olympiad training archive',source_status='national_mathematics_training_archive',metadata_evidence='Year 2009 row, solution column.'))
    for row in candidates:
        row=dict(row);di.register(**row)
    todo=[r for r in di.RECORDS.values() if r.get('status')!='downloaded' and any(r['source']==c['url'] for c in candidates)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for r in pool.map(di.download,todo):
            oldkey=(r['contest'],str(r['year']),r['type'],r['source'])
            if r['status']=='downloaded':
                parsed=subprocess.run(['/usr/bin/pdftotext','-layout',str(di.ROOT/r['path']),'-'],capture_output=True,text=True,timeout=25,check=True).stdout
                headings=len(re.findall(r'(?mi)^\s*Solution(?:s|\s+\d+)?\s*[.:]',parsed))
                nums=sorted(set(re.findall(r'(?mi)^\s*Problem\s+([1-6])\s*[.:]',parsed)))
                if r['contest']=='RMM':
                    r['type']='problems_and_solutions' if headings else 'problems'
                    r['content_validation']=dict(solution_headings=headings,problem_numbers=nums,year_in_text=str(r['year']) in parsed)
                    day=re.search(r'Day([12])',r['source'])
                    if day:r['round']='day_'+day[1]
                    if r['year']==2019:r['edition_solution_coverage_note']='Mirror has solutions for day 1 only; day 2 PDF contains statements, so the full edition solution set remains incomplete.'
                    r['coverage_completeness']='Only numbered statements and solution headings checked; no independent proof correctness review.'
                else:
                    ids=sorted({int(n) for n in re.findall(r'(?m)^\s*(\d{1,2})\.\s',parsed) if 1<=int(n)<=20})
                    r['content_validation']=dict(numbered_sections=ids,finnish_solution_heading=bool(re.search(r'Ratkaisu',parsed,re.I)))
                    if len(ids)<15:r['type']='unclassified_mathematics_material'
                    r['coverage_completeness']='Numbered solution sections checked; mathematical correctness not independently reviewed.'
            di.RECORDS.pop(oldkey,None);di.RECORDS[(r['contest'],str(r['year']),r['type'],r['source'])]=r
            print(r['contest'],r['year'],r['status'],r['type'],r.get('content_validation'),flush=True)
    # These exact published links are known, but the host times out locally.
    for part in ['Individual','Team']:
        u=f'https://memo2026.dmfa.si/wp-content/uploads/2026/08/MEMO_2026_{part}_en.pdf'
        di.register('MEMO',2026,'problems',u,'https://memo2026.dmfa.si/?page_id=76','en',round=part.lower(),source_status='official_organizer_link',note='Published PDF independently readable via web index, local HTTPS connection timed out on October 25; not counted as downloaded.')
        key=('MEMO','2026','problems',u)
        if di.RECORDS[key]['status']!='downloaded':di.RECORDS[key].update(status='download_error',error='Local connection timed out (curl 28) during exact URL probe.')
    di.save_manifest()

if __name__=='__main__':main()
