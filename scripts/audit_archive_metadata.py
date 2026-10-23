#!/usr/bin/env python3
"""Add conservative content evidence to selected Russian archive manifests.

Original documents are not modified. Only explicit solution headings and
academic-year headers on the first two PDF pages are used for corrections.
"""
from pathlib import Path
import argparse,json,re,subprocess
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--contest',action='append',required=True);ap.add_argument('--report',required=True);args=ap.parse_args()
 changes=[];errors=[]
 for cid in args.contest:
  mf=ROOT/f'olympiads/russia/{cid}/manifest.json';m=json.loads(mf.read_text())
  for r in m.get('documents',[]):
   if r.get('status')!='downloaded' or not r.get('local_path','').lower().endswith('.pdf'):continue
   p=ROOT/r['local_path']
   try:
    proc=subprocess.run(['/usr/bin/pdftotext','-f','1','-l','2','-layout',str(p),'-'],capture_output=True,timeout=20)
    if proc.returncode:raise ValueError('pdftotext could not read the document')
    text=proc.stdout.decode('utf-8','replace')
   except Exception as exc:errors.append(dict(path=r['local_path'],error=str(exc)));continue
   edits={}
   # Grade headings can occur later in annual collections. Read all pages before
   # assigning the list; never label a multi-grade booklet by its first grade.
   if not r.get('classes'):
    try:
     full=subprocess.run(['/usr/bin/pdftotext','-layout',str(p),'-'],capture_output=True,timeout=20)
     if full.returncode==0:
      grade_text=full.stdout.decode('utf-8','replace')
      grades=set()
      for a,b in re.findall(r'(?mi)^\s*(1[01]|[1-9])\s*(?:[-–—]\s*(1[01]|[1-9]))?\s*класс',grade_text):
       lo=int(a);hi=int(b) if b else lo
       if lo<=hi<=11:grades.update(range(lo,hi+1))
      if grades:edits['classes']=', '.join(map(str,sorted(grades)))
    except subprocess.TimeoutExpired:pass
   joined=bool(re.search(r'зада(?:чи|ния)\s+и\s+(?:решения|ответы)',text[:1400],re.I))
   headings=re.findall(r'(?mi)^\s*(?:решени[ея]|ответ(?:ы)?)\s*(?:[.:]|\n|$)',text)
   if joined or len(headings)>=2:
    if r.get('document_type') not in ('solutions','tasks_and_solutions'):
     edits['document_type']='tasks_and_solutions'
   # Generic score rubrics and diploma thresholds are not worked solutions.
   if re.search(r'Критерии\s+определения\s+победителей',text[:400],re.I):
    edits['document_type']='administrative';edits['document_role']='administrative'
   elif cid=='spbu' and re.search(r'критери',text[:300],re.I) and re.search(r'общую.*схему оценивания|по следующим принципам|различные темы в рамках программ',text,re.I|re.S):
    if not joined and len(headings)<2:edits['document_type']='marking_scheme'
   for match in re.finditer(r'\b((?:19|20)\d{2})\s*[-/–—]\s*(\d{4}|\d{2})(?!\d)',text[:650]):
    first=int(match[1]);second=int(match[2]);second=first//100*100+second if second<100 else second
    context=text[max(0,match.start()-180):match.end()+100]
    if second==first+1 and re.search(r'олимпиад|учебн|год',context,re.I):
     year=f'{first}/{second}'
     if r.get('year')!=year:edits['year']=year
     break
   if edits:
    previous={k:r.get(k) for k in edits}
    evidence=dict(date=datetime.now(timezone.utc).isoformat(),method='pdftotext, first two pages',previous=previous,updated=edits,
     solution_evidence='Explicit tasks-and-solutions title' if joined else f'{len(headings)} explicit answer/solution headings',
     year_evidence='Consecutive academic-year pair in a contest header' if 'year' in edits else None)
    if 'classes' in edits:evidence['grade_evidence']='Explicit grade headings in full PDF text'
    r.setdefault('metadata_audit',[]).append(evidence);r.update(edits)
    changes.append(dict(contest=cid,path=r['local_path'],**evidence))
  temp=mf.with_suffix('.json.tmp');temp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');temp.replace(mf)
 report=ROOT/args.report
 prior=json.loads(report.read_text()) if report.exists() else {}
 report.write_text(json.dumps(dict(changes=prior.get('changes',[])+changes,errors=prior.get('errors',[])+errors),ensure_ascii=False,indent=2)+'\n')
 print('Metadata corrections:',len(changes),'unreadable PDFs:',len(errors))

if __name__=='__main__':main()
