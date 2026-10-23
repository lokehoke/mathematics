#!/usr/bin/env python3
"""Reproducible inventory of real downloaded mathematics contest materials.

Keeps originals and source manifests intact. Counts indexes, administrative
resources, unrelated profiles, uncertain material types and duplicate bytes
separately. The baseline is captured before any resumed network requests.
"""
from pathlib import Path
from collections import Counter, defaultdict
from urllib.parse import unquote, urlsplit
import argparse, datetime, hashlib, json, re
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/'research/archive-resume-baseline-2026-10-22.json'
TYPES={'tasks':'problems','tasks_and_solutions':'problems_and_solutions',
       'tasks_or_solutions_html':'unclassified_mathematics_html',
       'mathematics_material':'unclassified_mathematics_material'}
ADMIN=re.compile(r'competitionrules|protocol|protokol|(?:^|[/_-])prots|jury\.pdf|program(?:ma|m|_)|программ|положени|регламент|согласие|персональн|список\s+(?:побед|приз|участ)|регистрац|результат|winners|statistic|poster|flyer|logo|/doc/norm/|/diplom',re.I)
POS=re.compile(r'задач|задани|услов|решени|ответ|problem|solution|question|marking',re.I)

def loads(p): return json.loads(p.read_text())
def records_now():
    out=[]
    for p in sorted((ROOT/'olympiads/russia').glob('*/manifest.json')):
        m=loads(p)
        for r in m.get('documents',[]):
            path=r.get('local_path',r.get('path'))
            out.append(dict(region='russia',contest_id=p.parent.name,manifest=str(p.relative_to(ROOT)),record=r,file_exists=bool(path and (ROOT/path).is_file())))
    for region in ['international','university']:
        p=ROOT/f'olympiads/{region}/manifest.jsonl';d={}
        for line in p.read_text().splitlines():
            if line.strip():
                r=json.loads(line);d[(r.get('contest'),r.get('source',r.get('url')),r.get('type'))]=r
        for r in d.values():
            path=r.get('path',r.get('local_path'))
            out.append(dict(region=region,contest_id=r['contest'],manifest=str(p.relative_to(ROOT)),record=r,file_exists=bool(path and (ROOT/path).is_file())))
    return out

def normalized(x):
    r=x['record'];region=x['region'];path=r.get('local_path',r.get('path'))
    cid=x.get('contest_id') or (Path(x['manifest']).parent.name if region=='russia' else r['contest'])
    typ=r.get('document_type',r.get('type','unknown'));typ=TYPES.get(typ,typ)
    url=r.get('url',r.get('source',''))
    label=r.get('label','');s=unquote(url+' '+label).replace('\xad','')
    category='material';reason=None
    if typ=='administrative' or r.get('document_role')=='administrative':category='administrative'
    elif typ=='index' or r.get('document_role')=='archive_index': category='index'
    elif typ in ('leader_report_candidate','leader_report_without_verified_papers'):
        category='supplementary_reading';reason='Delegation report not verified to reproduce contest statements.'
    elif re.search(r'\.xlsx?(?:\.zip)?$',urlsplit(url).path,re.I):
        category='needs_subject_review';reason='Spreadsheet resource; not established as contest tasks or solutions.'
    elif cid=='turgor' and typ=='unclassified_mathematics_html' and re.search(r'/problems/\d+/(?:index\.(?:php|html?))?$',urlsplit(url).path,re.I):
        category='index';reason='Annual Tournament of Towns archive landing page: links to papers, not the paper itself.'
    elif cid=='spbu' and re.search(r'modeling|моделирован|механик',s,re.I):
        category='excluded_other_profile';reason='Mathematical modelling/artificial intelligence is a separate profile, not the requested pure mathematics profile.'
    elif cid=='lomonosov' and re.search(r'механик|mechanic|моделирован',s,re.I):
        category='excluded_other_profile';reason='Mechanics and mathematical modelling is a separate profile.'
    elif re.search(r'unknotting\.pdf',url,re.I):
        category='needs_subject_review';reason='Ambiguous PDF from a multi-subject RMM host; not counted as verified mathematics.'
    elif ADMIN.search(s) and not (POS.search(label) and not re.search(r'программ|положени|регламент|согласие|персональн',label,re.I)):
        category='administrative';reason='Administrative/resource filename or label, not a contest paper.'
    elif region=='russia' and cid=='turgor' and re.search(r'/free-books/matpros/articles/|/papers[^/]*\.(?:ps|pdf)|/circles/oim/|/TOPICS/|arxiv\.org',url,re.I):
        category='supplementary_reading';reason='Related mathematical reading/training, not an annual contest paper.'
    elif region=='russia' and cid=='mos_probability':
        source=r.get('source_page','');title='';manifest=ROOT/x['manifest']
        try:
            for ind in loads(manifest).get('indexes',[]):
                if ind['url']==source:
                    soup=BeautifulSoup((ROOT/ind['local_path']).read_bytes(),'html.parser')
                    h=soup.find('h1');title=h.get_text(' ',strip=True) if h else ''
                    break
        except (OSError,ValueError):pass
        if source.rstrip('/')!='https://ptlab.mccme.ru/node/2904' and not re.search(r'олимпиад|пригласительн|отборочн|очный этап',title,re.I):
            category='supplementary_reading';reason='General probability curriculum/lesson page rather than an olympiad archive page.'
    success=r.get('status')=='downloaded' and x.get('file_exists',False)
    return dict(region=region,contest=cid,source_contest=r.get('contest'),source_url=url,
        source_page=r.get('source_page'),source_status=r.get('source_status'),source_authority=r.get('source_authority'),final_url=r.get('final_url'),derived_retrieval_url=r.get('derived_retrieval_url'),manifest=x['manifest'],path=path,
        sha256=r.get('sha256'),year=r.get('year'),covers_years=r.get('covers_years',[]),
        covers_contests=r.get('covers_contests',[]),stage=r.get('stage',r.get('round')),
        classes=r.get('classes',r.get('age_group')),document_type=typ,
        status=r.get('status'),file_exists=x.get('file_exists'),category=category,
        exclusion_reason=reason,accepted_material=bool(success and category=='material'),
        solution_bearing=bool(success and category=='material' and re.search(r'solut|solution',typ)),
        error=r.get('error',r.get('note')))

def counts(rows):
    success=[r for r in rows if r['status']=='downloaded' and r['file_exists']]
    accepted=[r for r in rows if r['accepted_material']]
    distinct={r['sha256'] for r in accepted if r['sha256']}
    sols=[r for r in accepted if r['solution_bearing']]
    return dict(records=len(rows),downloaded_records_with_files=len(success),
        downloaded_categories=dict(Counter(r['category'] for r in success)),
        material_records=len(accepted),distinct_material_file_paths=len({r['path'] for r in accepted}),
        unique_material_documents_by_sha256=len(distinct),
        unique_classified_task_or_solution_documents=len({r['sha256'] for r in accepted if not r['document_type'].startswith('unclassified_')}),
        duplicate_material_copies_by_sha256=len(accepted)-len(distinct),
        solution_bearing_records=len(sols),unique_solution_documents_by_sha256=len({r['sha256'] for r in sols}),
        document_types=dict(Counter(r['document_type'] for r in accepted)),
        statuses=dict(Counter(r['status'] for r in rows)))

def years_of(rows):
    ys=set()
    for r in rows:
        ys.update(r.get('covers_years',[]))
        if r.get('covers_years'):continue
        text=str(r.get('year',''))
        match=re.fullmatch(r'((?:19|20)\d{2})(?:[/-]((?:19|20)?\d{2}))?',text)
        if match:
            first=int(match[1]);ys.add(first)
            if match[2]:
                second=int(match[2]);second=second if second>100 else first//100*100+second
                if first<=second<=2026:ys.update(range(first,second+1))
    return sorted(ys)

def main():
    import argparse
    global BASELINE
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', default='2026-10-22', help='Date label for this pass; historical reports are preserved.')
    parser.add_argument('--baseline', help='Baseline JSON captured from pre-pass manifests.')
    parser.add_argument('--suffix', default='', help='Distinct report label, preserving earlier passes.')
    args=parser.parse_args()
    if args.suffix and not re.fullmatch(r'[a-z0-9-]+',args.suffix):parser.error('Invalid suffix')
    stamp=datetime.date.fromisoformat(args.date).isoformat()
    stamp += ('-'+args.suffix) if args.suffix else ''
    BASELINE=ROOT/(args.baseline or f'research/archive-resume-baseline-{stamp}.json')
    previous_path=ROOT/f'research/archive-resume-summary-{stamp}.json'
    previous=loads(previous_path) if previous_path.exists() else None
    base=loads(BASELINE);old=[normalized(r) for r in base['records']];now=[normalized(r) for r in records_now()]
    # Check actual bytes, not merely the status or existence of a path.
    checked={};integrity_failures=[];accepted_count=0
    for r in now:
        if not r['accepted_material']:continue
        accepted_count+=1;p=ROOT/r['path']
        if r['path'] not in checked:
            h=hashlib.sha256()
            with p.open('rb') as f:
                for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
            checked[r['path']]=h.hexdigest()
        r['integrity_sha256_verified']=checked[r['path']]==r['sha256']
        if not r['integrity_sha256_verified']:
            integrity_failures.append(dict(path=r['path'],expected=r['sha256'],actual=checked[r['path']]))
            r['accepted_material']=False;r['solution_bearing']=False;r['category']='integrity_failure'
    old_hash={r['sha256'] for r in old if r['accepted_material']};old_sol={r['sha256'] for r in old if r['solution_bearing']}
    fresh=[r for r in now if r['accepted_material'] and r['sha256'] not in old_hash]
    stats={}
    for region in ['russia','international','university']:
        a=[r for r in old if r['region']==region];b=[r for r in now if r['region']==region]
        ah={r['sha256'] for r in a if r['accepted_material']};bh={r['sha256'] for r in b if r['accepted_material']}
        stats[region]=dict(before=counts(a),after=counts(b),new_unique_material_documents=len(bh-ah))
    contests=[]
    for region,cid in sorted({(r['region'],r['contest']) for r in now}):
        rows=[r for r in now if r['region']==region and r['contest']==cid];accepted=[r for r in rows if r['accepted_material']]
        shared=[r for r in now if r['accepted_material'] and r['solution_bearing'] and cid in r.get('covers_contests',[]) and r['contest']!=cid]
        ys=years_of(accepted+shared);solyears=years_of([r for r in accepted if r['solution_bearing']]+shared)
        contests.append(dict(region=region,contest=cid,counts=counts(rows),years_with_materials=ys,
            years_with_classified_solutions=solyears,
            shared_solution_collections=[dict(source_url=r['source_url'],path=r['path'],covers_years=r['covers_years']) for r in shared],
            years_without_classified_solution_document=sorted(set(ys)-set(solyears)),
            undated_material_records=sum(r['year'] is None for r in accepted),
            source_hosts=sorted({urlsplit(r['source_url']).netloc for r in rows}),
            manifests=sorted({r['manifest'] for r in rows}),
            coverage_status='partial; all published years/rounds not independently reconciled'))
    index_errors=[];pending_discovered=[]
    for p in sorted((ROOT/'olympiads/russia').glob('*/manifest.json')):
        m=loads(p)
        index_errors.extend(dict(contest=p.parent.name,**r) for r in m.get('failures',[]))
        index_errors.extend(dict(contest=p.parent.name,**r) for r in m.get('public_api_failures',[]))
        index_errors.extend(dict(contest=p.parent.name,**r) for r in m.get('secondary_archive_pass',{}).get('failures',[]))
        pending_discovered.extend(dict(contest_id=p.parent.name,**r) for r in m.get('pending_documents',[]))
    queue=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        active_download_processes=[],failed_or_unavailable_records=[r for r in now if r['status']!='downloaded'],
        missing_local_files=[r for r in now if r['status']=='downloaded' and not r['file_exists']],
        russian_index_errors=index_errors,russian_pending_documents=pending_discovered,
        resume_commands=['python3 scripts/download_russia.py --max-pages 2400 --max-depth 6 --workers 8',
         'python3 scripts/download_international.py --contests MEMO BMO supplements SKMO society RMM APMO IMO EGMO BalticWay',
         'python3 scripts/download_university.py --resume',
         'python3 scripts/download_itmo_public.py',
         'python3 scripts/audit_archive_metadata.py --contest bibn --contest itmo --contest verchenko'],
        notes=['Downloaded originals are preserved; existing verified files are reused.',
         'A missing classified solution is a metadata/coverage gap, not proof that no solution was published.',
         'IMO 1980 was not held; Putnam 2026 takes place in December and is not yet expected.',
         'Russian olympiad school-year 2026/27 is in progress; do not label future rounds missing.',
         'Finish reconciliation of the existing source list before adding more contests.'])
    qpath=ROOT/f'research/archive-continuation-queue-{stamp}.json';qpath.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
    after=counts(now);before=counts(old)
    hashes={r['sha256'] for r in now if r['accepted_material']};solhash={r['sha256'] for r in now if r['solution_bearing']}
    summary=dict(created_at=queue['created_at'],baseline=str(BASELINE.relative_to(ROOT)),
        counting_rules=['Counts documents, not individual problems; PDF/ZIP/source/HTML versions are separately recorded.',
         'Unique document count is SHA-256 deduplication across all three directions.',
         'Administrative material, indexes, other profiles and supplementary reading are excluded from accepted contest documents.',
         'Unclassified mathematical materials remain explicit; they are not claimed to contain solutions.',
         'Year/round/class metadata are organizer-link heuristics unless otherwise recorded; undated files remain undated.'],
        before=before,after=after,new_unique_material_documents=len(hashes-old_hash),
        net_growth_unique_material_documents=len(hashes)-len(old_hash),
        previous_hashes_not_in_current_inventory=sorted(old_hash-hashes),
        new_unique_solution_documents=len(solhash-old_sol),directions=stats,contests=contests,
        continuation_queue=str(qpath.relative_to(ROOT)),
        excluded_records=[r for r in now if r['status']=='downloaded' and r['category'] not in ['material','index']],
        completeness='partial',raw_initial_counts=base['counts'])
    summary['integrity']=dict(accepted_records_checked=accepted_count,distinct_file_paths_hashed=len(checked),
        sha256_matches=accepted_count-len(integrity_failures),sha256_mismatches=integrity_failures,
        accepted_missing_files=sum(r['status']=='downloaded' and r['category']=='material' and not r['file_exists'] for r in now),
        bytes_hashed=sum((ROOT/p).stat().st_size for p in checked),status='passed' if not integrity_failures else 'failed')
    if previous and previous.get('after',{}).get('unique_material_documents_by_sha256')==5225:
        summary['superseded_first_report_reconciliation']=dict(before=3113,after=5225,
            gross_new_hashes=2121,net_growth=2112,difference=9,
            russian_gross_new_hashes=1853,russian_net_growth=1844,
            reason='Nine older SHA-256 values (ten URL records) belonged to annual Turgor HTML archive indexes whose content changed at the same URLs. No downloaded paper was removed. These landing pages are now classified as indexes in both baseline and current inventory, so they no longer inflate mathematical-material counts.')
    elif previous and previous.get('superseded_first_report_reconciliation'):
        summary['superseded_first_report_reconciliation']=previous['superseded_first_report_reconciliation']
    (ROOT/f'research/archive-resume-summary-{stamp}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    (ROOT/f'research/archive-material-inventory-{stamp}.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in now))
    lines=[f'# Итог возобновления архива, {stamp}','',
        f"Уникальных математических материалов по SHA-256: **{before['unique_material_documents_by_sha256']} → {after['unique_material_documents_by_sha256']}**, новых **{summary['new_unique_material_documents']}**, чистый прирост **{summary['net_growth_unique_material_documents']}**.",
        f"Документов с классифицированными решениями: **{before['unique_solution_documents_by_sha256']} → {after['unique_solution_documents_by_sha256']}**, новых **{summary['new_unique_solution_documents']}**.",'',
        f"Из них классифицированные документы задач/решений: **{before['unique_classified_task_or_solution_documents']} → {after['unique_classified_task_or_solution_documents']}**. Остальные математические материалы имеют явно неизвестный тип и не объявлены проверенными задачниками или решениями.",
        'Это числа документов, а не отдельных задач. Неизвестный тип файла не выдаётся за наличие решений. Уникальность по байтам не устраняет дубли одного текста в разных форматах/языках.','',
        '| Направление | Уникальные документы до | После | Новые |','|---|---:|---:|---:|']
    for region,s in stats.items():lines.append(f"| {region} | {s['before']['unique_material_documents_by_sha256']} | {s['after']['unique_material_documents_by_sha256']} | {s['new_unique_material_documents']} |")
    lines+=['','Внутри направлений одинаковый файл учитывается по одному разу; общая цифра дополнительно устраняет дубли между направлениями.','',
        f"Успешно сохранённые записи по категориям: `{json.dumps(after['downloaded_categories'],ensure_ascii=False)}`.",
        f"Статусы всех записей: `{json.dumps(after['statuses'],ensure_ascii=False)}`.",'',
        f"Проверка целостности: **{accepted_count}** записей, **{len(checked)}** физических файлов; отсутствующих accepted-файлов **{summary['integrity']['accepted_missing_files']}**, несовпадений SHA-256 **{len(integrity_failures)}**.",
        'В первой предварительной сводке 3113 → 5225 означало чистый прирост 2112, тогда как 2121 было числом новых SHA. Разница 9 — изменившиеся HTML-индексы Турнира городов (10 URL), а не исчезнувшие задачи. Для РФ аналогично: 1853 новых SHA против чистого прироста 1844. Эти индексы теперь исключены из материалов в обоих срезах; численные итоги выше пересчитаны.','',
        '## Годы и источники','', '| Архив | Уникальных документов | Годы с материалами | Годы с классифицированными решениями |','|---|---:|---|---|']
    for c in contests:
        lines.append(f"| {c['region']}/{c['contest']} | {c['counts']['unique_material_documents_by_sha256']} | {', '.join(map(str,c['years_with_materials'])) or 'нет'} | {', '.join(map(str,c['years_with_classified_solutions'])) or 'нет'} |")
    lines+=['','## Проверенные официальные опорные страницы','',
        '- [IMO: официальный архив](https://www.imo-official.org/problems/?language=en).',
        '- [APMO: задачи и решения 1989–2026](https://www.apmo-official.org/problems).',
        '- [IMC: задачи, решения и критерии 2026; ссылки на все годы с 1994](https://www.imc-math.org.uk/?item=problems&year=2026).',
        '- [MAA: Putnam 2018–2025](https://maa.org/maa-putnam-archive/); исторические авторские/университетские источники помечены отдельно в манифесте.',
        '- [ММО: официальный архив](https://mmo.mccme.ru/).',
        '- [ОММО: официальный адрес с HTML-перенаправлением](https://olympiads.mccme.ru/ommo/).','',
        'Полное покрытие не установлено. Недоступные документы/страницы, открытые очереди и годы без классифицированных решений перечислены в JSON. У олимпиад 2026/27 ещё идут этапы; Putnam 2026 пока не состоялся.','',
        '## Файлы для продолжения','',
        '- `research/archive-resume-summary-2026-10-22.json` — агрегаты, годы, источники, исключения.',
        '- `research/archive-material-inventory-2026-10-22.jsonl` — единая нормализованная инвентаризация со ссылками и SHA-256.',
        '- `research/archive-continuation-queue-2026-10-22.json` — ошибки и очереди.',
        '- `olympiads/russia/*/manifest.json`, `olympiads/international/manifest.jsonl`, `olympiads/university/manifest.jsonl` — исходные манифесты.',
        '- `scripts/download_{russia,international,university}.py`, `scripts/summarize_archive_resume.py` — воспроизведение.',
        '', 'Оригиналы не удалялись. Книга, README и AGENTS не изменялись. Коммит не создавался.']
    lines=[line.replace('2026-10-22',stamp) for line in lines if not (stamp!='2026-10-22' and line.startswith('В первой предварительной сводке'))]
    lines[-1]='Оригиналы сохранены. Изменения книги не входят в этот проход.'
    (ROOT/f'research/archive-resume-report-{stamp}.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:summary[k] for k in ['before','after','new_unique_material_documents','new_unique_solution_documents']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
