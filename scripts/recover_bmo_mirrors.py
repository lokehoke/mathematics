#!/usr/bin/env python3
"""Preserve published BMO PDF mirrors and verify their contents before typing."""
import json,re,subprocess
import download_international as di
from download_russia import fetch

def main():
    for line in di.MANIFEST.read_text().splitlines():
        r=json.loads(line);di.RECORDS[(r['contest'],str(r['year']),r['type'],r['source'])]=r
    revision='d6036eaac665a22cf04fd1c872202ccac7414b83'
    index=f'https://huggingface.co/api/datasets/AI-MO/olympiads/tree/{revision}/Balkan_MO/raw'
    response=fetch(index)
    if not response['ok']:raise RuntimeError(response.get('error'))
    paths=json.loads(response['data'])
    for entry in paths:
        match=re.fullmatch(r'Balkan_MO/raw/en-(2008|2009|2013|2015|2020)-BMO.pdf',entry['path'])
        if not match:continue
        url=f"https://huggingface.co/datasets/AI-MO/olympiads/resolve/{revision}/{entry['path']}"
        di.register('BMO',int(match[1]),'unclassified_mathematics_material',url,index,'en',source_status='public_secondary_dataset_pdf_extract',original_collection_url='https://drive.google.com/file/d/0B2qYu535vGeQYUtUTzlOTldkR3c',source_script_url=f'https://huggingface.co/datasets/AI-MO/olympiads/raw/{revision}/Balkan_MO/download_script/download.py',note='Third-party published PDF slices, preserved unchanged. Verify solution text before classifying; not an organizer-hosted original.')
    di.register('BMO',2015,'problems_and_solutions','https://umks.pmf.unsa.ba/wp-content/uploads/2021/07/BMO_2015.pdf','https://umks.pmf.unsa.ba/','en',source_status='public institutional mathematics archive',metadata_evidence='Published PDF explicitly contains Problem 1–4 and Solution headings')
    di.run_downloads()
    for key,r in list(di.RECORDS.items()):
        if r['contest']!='BMO' or r['status']!='downloaded' or 'huggingface.co' not in r['source']:continue
        text=subprocess.run(['/usr/bin/pdftotext','-layout',str(di.ROOT/r['path']),'-'],capture_output=True,text=True,timeout=30).stdout
        headings=len(re.findall(r'(?mi)^\s*(?:Solution(?:s)?(?:\s+\d+)?|Proof)\s*[.:]',text))
        ids=sorted(set(re.findall(r'(?mi)^\s*(?:Problem\s*)?([1-4])\s*[.)]',text)))
        kind='problems_and_solutions' if headings else 'problems'
        di.RECORDS.pop(key)
        r.update(type=kind,content_check=dict(solution_headings=headings,problem_numbers=ids,contest_year_in_text=str(r['year']) in text),solution_status='Published secondary solutions; completeness and correctness not independently proven' if headings else 'No explicit solution headings verified')
        di.RECORDS[('BMO',str(r['year']),kind,r['source'])]=r
        print(r['year'],kind,'solution headings',headings,'problem identifiers',ids,flush=True)
    di.save_manifest()

if __name__=='__main__':main()
