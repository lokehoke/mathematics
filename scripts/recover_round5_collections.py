#!/usr/bin/env python3
"""Preserve published solution collections with explicit per-problem coverage.

PDFs remain byte-for-byte unchanged. Page ranges below were checked against the
published collection's edition/day headers; no year is inferred from file age.
"""
import hashlib,json,re,subprocess
from collections import defaultdict
from pathlib import Path
import download_international as di
from download_russia import fetch

PAGE='https://imogeometry.blogspot.com/p/romanian-master-of-mathematics-geometry.html'
SPECS=[('IMO','1959-2003','0B2qYu535vGeQbUZmemJHQTJrWWs'),('RMM','2019-2025','0B2qYu535vGeQb1FNaGYxdGFzOTQ')]

def solution_ids(text,pattern):
    heads=list(re.finditer(pattern,text,re.M));out=set()
    for i,m in enumerate(heads):
        part=text[m.end():heads[i+1].start() if i+1<len(heads) else len(text)]
        if re.search(r'\bSolution(?:s|\s+\d+)?\b',part):out.add(m[1])
    return sorted(out)

def main():
    for line in di.MANIFEST.read_text().splitlines():
        r=json.loads(line);di.RECORDS[(r['contest'],str(r['year']),r['type'],r['source'])]=r
    checks=[]
    for contest,year,mid in SPECS:
        u=f'https://drive.google.com/uc?export=download&id={mid}'
        di.register(contest,year,'problems_and_solutions',u,PAGE,'en',published_link=f'https://drive.google.com/file/d/{mid}/view',source_status='public_secondary_solution_collection',source_authority='John Scholes (IMO) / collected contest solution PDFs (RMM)',coverage_completeness='See per-year, per-problem content evidence; correctness not independently proved.')
        key=(contest,year,'problems_and_solutions',u);r=di.RECORDS[key]
        if r['status']!='downloaded':
            cache=di.ROOT/'research/international_cache/round5'/hashlib.sha256(u.encode()).hexdigest()
            if cache.exists() and cache.read_bytes().startswith(b'%PDF'):
                p=di.OUT/contest/year/f'published_collection_{mid}.pdf';p.parent.mkdir(parents=True,exist_ok=True);data=cache.read_bytes();p.write_bytes(data)
                r.update(status='downloaded',path=str(p.relative_to(di.ROOT)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),mime='application/pdf',pdf_signature_valid=True)
            else:r=di.download(r)
        if r['status']!='downloaded':di.RECORDS[key]=r;continue
        text=subprocess.run(['/usr/bin/pdftotext','-layout',str(di.ROOT/r['path']),'-'],capture_output=True,text=True,check=True,timeout=30).stdout
        pages=text.split('\f');coverage={}
        if contest=='IMO':
            by_year=defaultdict(list);page_numbers=defaultdict(list);current=None
            for n,t in enumerate(pages,1):
                h=re.search(r'(?m)^\s*(?:\d+(?:st|nd|rd|th)\s+)?IMO\s+((?:19|20)\d{2})\b',t[:600])
                if h:current=int(h[1])
                if current and current!=1980:by_year[current].append(t);page_numbers[current].append(n)
            for y,parts in sorted(by_year.items()):
                ids=solution_ids('\n'.join(parts),r'^\s*Problem\s+([AB][1-3])\b')
                if ids:coverage[str(y)]=dict(solution_problem_ids=ids,expected_problem_ids=['A1','A2','A3','B1','B2','B3'],all_six_headings_verified=len(ids)==6,pages=page_numbers[y],naming='A1-A3 = day 1; B1-B3 = day 2')
        else:
            ranges={2019:(11,109,118),2020:(12,119,127),2024:(15,145,157),2025:(16,158,168)}
            for y,(edition,start,end) in ranges.items():
                first=pages[start-1][:600]
                if not re.search(rf'\b{edition}(?:st|nd|rd|th)\s+Romanian Master',first,re.I) or not re.search(r'Solutions',first,re.I):raise ValueError(f'Collection page/header shifted: {y}')
                part='\n'.join(pages[start-1:end]);ids=solution_ids(part,r'^\s*Problem\s+([1-6])\b')
                coverage[str(y)]=dict(solution_problem_ids=ids,expected_problem_ids=list('123456'),all_six_headings_verified=ids==list('123456'),pages=list(range(start,end+1)),edition=edition)
        if not coverage:raise ValueError(f'No verified solution coverage: {contest}')
        r.update(covers_years=sorted(map(int,coverage)),solution_problem_coverage_by_year=coverage,content_validation='Explicit edition headers, numbered problem headings followed by Solution text. Page numbers are 1-based PDF pages.',solution_status='Published author/collection solutions; mathematical correctness not independently reviewed.')
        if contest=='IMO':r['original_text_source']='http://www.kalva.demon.co.uk/imo.html'
        di.RECORDS[key]=r;checks.append(dict(contest=contest,path=r['path'],sha256=r['sha256'],coverage=coverage))
        print(contest,'verified years',r['covers_years'],'all-six years',[y for y,c in coverage.items() if c['all_six_headings_verified']],flush=True)
    di.save_manifest()
    (di.ROOT/'research/archive-round5-collection-coverage-2026-10-25.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
