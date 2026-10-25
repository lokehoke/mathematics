#!/usr/bin/env python3
"""Recover linked mathematics PDFs, retaining source-table disagreements."""
import concurrent.futures, hashlib, json, re, subprocess
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from download_russia import ROOT, BASE, fetch, decode, output_path, save_json

SOURCES={
 'innopolis':('https://postypashki.ru/олимпиады/олимпиада-иннополис/',{2016,2019,2020,2021}),
 'rosatom':('https://postypashki.ru/олимпиады/росатом/',{2011,2012,2015}),
}

def recover(cid,page,years,solutions_only=False,source_cache=None):
    mf=BASE/cid/'manifest.json';m=json.loads(mf.read_text());records={r['url']:r for r in m['documents']}
    if source_cache and (ROOT/source_cache).is_file():
        res=dict(ok=True,data=(ROOT/source_cache).read_bytes(),content_type='text/html; charset=utf-8',final_url=page)
    else:res=fetch(page,25)
    if not res['ok']:raise RuntimeError(res)
    soup=BeautifulSoup(decode(res['data'],res['content_type']),'html.parser');assets={}
    for tr in soup.select('tr'):
        season=re.search(r'\b(20\d{2})[-–](20\d{2})\b',tr.get_text(' ',strip=True))
        if not season or int(season[2]) not in years:continue
        cells=tr.find_all(['td','th'],recursive=False)
        column=0
        for ci,cell in enumerate(cells):
            start_column=column;column+=int(cell.get('colspan',1))
            for a in cell.select('a[href]'):
                u=urljoin(page,a['href']);label=a.get_text(' ',strip=True)
                if '.pdf' not in u.lower():continue
                # Use HTTPS for the same publicly linked host/path.
                if u.startswith('http://postypashki.ru/'):u='https://'+u[7:]
                kind='tasks_and_solutions' if re.search(r'Задания и (?:решения|ответы)',label,re.I) else 'solutions' if re.search(r'Решения|Ответы',label,re.I) else 'tasks'
                if solutions_only and kind=='tasks':continue
                stage=('qualifying' if start_column<=2 else 'final') if cid!='innopolis' else ('qualifying' if ci<=2 else 'final') if int(season[2])==2016 else ('qualifying' if ci==1 else 'qualifying_tour_2' if ci==2 else 'final')
                if cid=='rosatom' and 'все-вместе' in u:stage='qualifying_and_final'
                row=dict(url=u,contest=m['contest'],subject='mathematics',year=f'{season[1]}/{season[2]}',stage=stage,classes='11',document_type=kind,label=label,source_page=page,source_status='public_secondary_archive',metadata_evidence='Source table season and column, default grade 11 stated by archive; subject and year checked against downloaded PDF.')
                assets.setdefault(u,row)
    def one(row):
        old=records.get(row['url'])
        prior_path=(old or {}).get('local_path') or (old or {}).get('unclassified_local_path')
        if old and old.get('content_validation',{}).get('ocr_verified') and prior_path and (ROOT/prior_path).is_file() and hashlib.sha256((ROOT/prior_path).read_bytes()).hexdigest()==old.get('sha256'):
            return dict(old,stage=row['stage'])
        if prior_path and (ROOT/prior_path).is_file():
            rr=dict(ok=True,data=(ROOT/prior_path).read_bytes(),final_url=(old or {}).get('final_url',row['url']))
        else:rr=fetch(row['url'],30)
        if not rr['ok']:return dict(row,status='failed',error=rr.get('error'))
        data=rr['data']
        if not data.startswith(b'%PDF'):return dict(row,status='failed',error='Expected published PDF')
        p=output_path(BASE/cid/'documents',row['url']);p.write_bytes(data)
        text=subprocess.run(['/usr/bin/pdftotext','-layout',str(p),'-'],capture_output=True,text=True,timeout=25,check=True).stdout
        # Some old PDFs map Cyrillic glyphs as Latin-1 bytes. Repair extracted
        # text only for inspection; published PDF bytes remain untouched.
        def repair(match):
            try:return match[0].encode('latin1').decode('cp1251')
            except UnicodeError:return match[0]
        text=re.sub(r'[\u00a0-\u00ff]+',repair,text)
        if re.search(r'отборочного\s+и\s+заключительного',text[:1800],re.I):row['stage']='qualifying_and_final'
        math_terms=set(re.findall(r'уравнени|многоугольник|квадратн|натуральн|cos|sin|log|polynomial|equation',text,re.I))
        subject=bool(re.search(r'математик|матема-\s*тике',text,re.I)) or len(math_terms)>=2
        if not subject:return dict(row,status='failed',error='Mathematics subject not verified from PDF',unclassified_local_path=str(p.relative_to(ROOT)))
        if cid=='rosatom' and re.search(r'олимпиады памяти И.В.Савельева',text,re.I):
            return dict(row,status='failed',error='Source-table mismatch: PDF title is Savelyev memorial olympiad; Rosatom edition attribution unverified.',unclassified_local_path=str(p.relative_to(ROOT)))
        grades=set()
        grade_lines=[]
        for line in text.splitlines():
            if len(line.strip())>160:continue
            if re.match(r'^\s*(?:9|10|11)\s*(?:[-–—\x15\x16]|класс)',line,re.I) or re.search(r'(?:этап|задания|математик|тур).*\bдля\s+(?:9|10|11)\b',line,re.I):grade_lines.append(line)
        for first,last in re.findall(r'\b(9|10|11)\s*(?:[-–—\x15\x16]\s*(9|10|11))?\s*класс','\n'.join(grade_lines),re.I):
            a,b=int(first),int(last or first)
            if a<=b:grades.update(str(n) for n in range(a,b+1))
        grades.update(re.findall(r'(?mi)^\s*Grade\s+(9|10|11)\b',text))
        if grades:row['classes']=', '.join(sorted(grades,key=int))
        header=text[:1800];pair=re.search(r'((?:19|20)\d{2})\s*[-–/—]\s*((?:19|20)?\d{2})(?!\d)',header)
        if pair:
            y1=int(pair[1]);y2=int(pair[2]);y2=y1//100*100+y2 if y2<100 else y2
            if y2==y1+1 and row['year']!=f'{y1}/{y2}':row.update(source_table_year=row['year'],year=f'{y1}/{y2}',year_warning='Source table disagrees with explicit PDF academic-year header; use PDF.')
        heads=len(re.findall(r'(?mi)^\s*(?:Решени[ея]|Ответ(?:ы)?)\s*[.:]',text))
        row.update(status='downloaded',local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),final_url=rr['final_url'],content_validation=dict(mathematics_title=True,solution_answer_headings=heads,header_excerpt=header[:450]),coverage_completeness='Published file only; complete class/round set not asserted.')
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for row in pool.map(one,assets.values()):
            records[row['url']]=row;print(cid,row['year'],row['status'],row['document_type'],row.get('year_warning',''),flush=True)
    m['documents']=list(records.values());m['round4_mirror_source']=page;save_json(mf,m)

if __name__=='__main__':
    for cid,(page,years) in SOURCES.items():recover(cid,page,years)
