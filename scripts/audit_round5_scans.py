#!/usr/bin/env python3
"""Verify selected scanned solution pages, leaving original PDFs unchanged."""
import hashlib,json,re,subprocess
from pathlib import Path
from download_russia import ROOT,BASE,fetch,save_json

SPECS=[
 ('лом-1213-закл-решения.pdf','2012/2013','final','11',[1,2,4]),
 ('лом-заочка-1516-условия-решения.pdf','2015/2016','qualifying',None,[1,3,15]),
 ('Ломоносов-1516-закл.pdf','2015/2016','final','10, 11',[2]),
]

def main():
    cache=ROOT/'research/international_cache/round5';td=cache/'tessdata';td.mkdir(parents=True,exist_ok=True)
    language=td/'rus.traineddata';source='https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/rus.traineddata'
    if not language.exists():
        res=fetch(source,30)
        if not res['ok']:raise RuntimeError(res)
        language.write_bytes(res['data'])
    mf=BASE/'lomonosov/manifest.json';m=json.loads(mf.read_text());audit=[]
    for filename,year,stage,classes,pages in SPECS:
        r=next(r for r in m['documents'] if r.get('source_status')=='public_secondary_archive' and r['url'].endswith(filename))
        path=r.get('local_path') or r['unclassified_local_path'];pdf=ROOT/path;texts=[]
        for n in pages:
            stem=cache/f'ocr-{hashlib.sha256(path.encode()).hexdigest()[:12]}-{n}';sidecar=stem.with_suffix('.txt')
            if not sidecar.exists():
                subprocess.run(['/usr/bin/pdftoppm','-f',str(n),'-l',str(n),'-r','110','-singlefile','-png',str(pdf),str(stem)],capture_output=True,check=True,timeout=30)
                result=subprocess.run(['/usr/bin/tesseract',str(stem)+'.png','stdout','--tessdata-dir',str(td),'-l','rus'],capture_output=True,text=True,check=True,timeout=30)
                sidecar.write_text(result.stdout)
            texts.append(sidecar.read_text())
        combined='\n'.join(texts);heads=len(re.findall(r'решени[ея]',combined,re.I))
        if not heads:raise ValueError(f'No scanned solution text verified: {filename}')
        if filename.startswith('лом-1213') and not re.search(r'2012/2013',combined):raise ValueError('Wrong edition header')
        r.update(status='downloaded',local_path=path,sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),bytes=pdf.stat().st_size,year=year,stage=stage,classes=classes,document_type='tasks_and_solutions')
        r.pop('error',None);r.pop('unclassified_local_path',None)
        r['content_validation']=dict(ocr_verified=True,checked_pdf_pages=pages,solution_word_count=heads,header_excerpt=texts[0][:250],method='System pdftoppm + Tesseract Russian; inspected sample pages. OCR is evidence only, never replacement for published PDF.',ocr_language_source=source,ocr_language_sha256=hashlib.sha256(language.read_bytes()).hexdigest())
        r['coverage_completeness']='Sampled scan pages establish solution content; completeness of all grades/variants is not asserted.'
        audit.append(dict(path=path,year=year,stage=stage,classes=classes,**r['content_validation']))
    save_json(mf,m)
    (ROOT/'research/archive-round5-scan-verification-2026-10-25.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    print('Verified scanned solution documents:',len(audit))

if __name__=='__main__':main()
