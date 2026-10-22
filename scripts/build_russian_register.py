#!/usr/bin/env python3
"""Extract the mathematics register from the saved official RSOSh table.

Requires beautifulsoup4. Reads, never guesses, register IDs/profiles/levels.
Refresh research/legal/official-source-0.html from the source URL to update.
"""
import hashlib, json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT/'research'
SOURCE=RESEARCH/'legal'/'official-source-0.html'
URL='https://rsr-olymp.ru/archive/2026'
ARCHIVES={6:['hse'],11:['vsesib'],12:[],16:['innopolis'],19:['izumrud'],20:['bibn'],21:['verchenko'],26:['mmo','mos_probability'],29:['ommo'],30:['kurchatov'],35:['lomonosov'],37:['pvg'],38:['phystech'],39:['shag'],43:['spbu'],45:['yumsh'],47:['itmo'],52:['rosatom'],55:['petersburg'],58:['turgor'],59:['turlom'],60:['belchonok']}
soup=BeautifulSoup(SOURCE.read_bytes(),'html.parser')
rows=[];related=[];current=None
for tr in soup.select('table.mainTableInfo tbody tr'):
    cells=tr.find_all('td',recursive=False)
    if len(cells)==5:
        current=dict(register_id=int(cells[0].get_text(' ',strip=True)),contest=cells[1].get_text(' ',strip=True),official_url=cells[1].a.get('href','').strip() if cells[1].a else None)
        cells=cells[2:]
    elif len(cells)!=3:
        continue
    row={**current,'profile':cells[0].get_text(' ',strip=True),'subjects':cells[1].get_text(' ',strip=True),'level':int(cells[2].get_text(' ',strip=True)),'source_url':URL}
    subjects=[s.strip() for s in row['subjects'].split(',')]
    if 'математика' in subjects:
        row['mathematics_only']=subjects==['математика']
        row['archive_ids']=ARCHIVES.get(row['register_id'],[])
        if row['register_id']==26:row['archive_ids']=['mos_probability'] if 'вероятность' in row['profile'] else ['mmo']
        row['archive_discovery']=[]
        for cid in row['archive_ids']:
            mf=ROOT/'olympiads'/'russia'/cid/'manifest.json'
            if mf.exists():
                m=json.loads(mf.read_text());good=[d for d in m.get('documents',[]) if d.get('status')=='downloaded']
                status='downloaded_partial' if good else 'discovered_no_successful_downloads'
                row['archive_discovery'].append(dict(id=cid,manifest=str(mf.relative_to(ROOT)),status=status,downloaded_materials=len(good),failed_documents=sum(d.get('status')=='failed' for d in m.get('documents',[])),failed_pages=len(m.get('failures',[]))))
            else:row['archive_discovery'].append(dict(id=cid,status='official_source_discovered_download_pending'))
        if not row['mathematics_only']:row['scope_note']='Mixed official profile. Only separately identifiable mathematics documents may be downloaded; no claim that this profile is a pure mathematics olympiad.'
        if not row['archive_ids']:row['scope_note']='Mixed education/pedagogy profile; official organizer discovered, no separately verified mathematics archive in this run.'
        rows.append(row)
    elif 'математ' in row['subjects'].lower() or 'математ' in row['profile'].lower():
        row['scope_note']='Related to mathematics/mechanics or a broad interdisciplinary degree group; excluded from mathematics-only downloads unless a separate mathematics profile is identified.'
        related.append(row)

legal_sources=[
('register-2026-27','Приказ Минобрнауки России от 31.08.2026 №521, перечень2026/27','http://publication.pravo.gov.ru/file/pdf?eoNumber=0001202609300016','legal/official-source-5.pdf'),
('conduct-2026','Приказ Минобрнауки России от16.01.2026 №16, порядок олимпиад','http://publication.pravo.gov.ru/file/pdf?eoNumber=0001202602240023','legal/order-16-2026.pdf'),
('admissions-821','Приказ Минобрнауки России от27.11.2024 №821, первоначальная официальная публикация','http://publication.pravo.gov.ru/file/pdf?eoNumber=0001202411290031','legal/admissions-order-821-official.pdf'),
('rsr-participants','Памятка РСОШ для участников, обновлена29.05.2026','https://rsr-olymp.ru/part','legal/rsr-part.html'),
('rsr-admissions','РСОШ: проверка дипломов приёмными комиссиями,2026','https://rsr-olymp.ru/pk','legal/rsr-pk.html'),
('msu-example','Пример правил конкретного вуза: ВМК МГУ, приём2026; это не общая федеральная льгота','https://pk.cs.msu.ru/privilege','legal/msu-cs-benefits.html'),
]
sources=[]
for sid,title,url,rel in legal_sources:
    p=RESEARCH/rel;rec=dict(id=sid,title=title,url=url,local_path='research/'+rel,status='downloaded' if p.exists() else 'not_downloaded')
    if p.exists():rec.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    sources.append(rec)

output=dict(verified_date='2026-10-22',academic_year='2026/2027',legal_basis=dict(order_number=521,order_date='2026-08-31',publication_number='0001202609300016',publication_date='2026-09-30',official_publication_url='http://publication.pravo.gov.ru/document/0001202609300016'),table_source=dict(url=URL,local_path=str(SOURCE.relative_to(ROOT)),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),extraction='Official RSOSh HTML table, accounting for row-spanned contest IDs and names; linked original legal PDF saved separately.'),profile_count=len(rows),contest_count=len({r['register_id'] for r in rows}),mathematics_only_profile_count=sum(r['mathematics_only'] for r in rows),mathematics_profiles=rows,related_profiles_excluded_from_pure_math_scope=related,separate_vsosh=dict(contest='Всероссийская олимпиада школьников по математике',archive_id='vsosh',ministry_register_level=None,note='Separate federal olympiad system; school, municipal, regional, final stages. It is not an I/II/III-level entry of the RSOSh ministry register. Admission rights for final-stage winners/prize-winners must be distinguished from the listed olympiads.'),additional_archives_not_asserted_to_be_in_2026_register=['sammat','mekhmat'],legal_sources=sources,admission_rules_notes=[dict(text='Inclusion and level in the federal register do not by themselves determine a university admission benefit; each university publishes its own recognized olympiads, programs, diploma categories, eligible school grades and confirmation thresholds.',source_url='https://rsr-olymp.ru/part'),dict(text='RSOSh participant notice for2026 states that listed-olympiad benefits normally require75EGEpoints or a higher threshold fixed by the university. This condition must not be transferred automatically to the separate final-stage VsOSh right.',source_url='https://rsr-olymp.ru/part'),dict(text='The linked university example is for admission2026, while the register is for academic year2026/27. Do not present the example as the university rules for admission2027.',source_url='https://pk.cs.msu.ru/privilege')])
(RESEARCH/'russian-register.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
(RESEARCH/'legal'/'manifest.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
print('Profiles:',len(rows),'pure mathematics:',sum(r['mathematics_only'] for r in rows),'contests:',output['contest_count'])
