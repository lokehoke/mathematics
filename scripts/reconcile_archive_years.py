#!/usr/bin/env python3
"""Year/round evidence matrix; gaps are not confused with unheld editions."""
import csv, datetime, json, re, subprocess
from collections import defaultdict
from pathlib import Path
from summarize_archive_resume import ROOT, records_now, normalized

TAG='2026-10-23'
SOURCES={
 'IMO':'https://www.imo-official.org/year_info.aspx?year=0',
 'APMO':'https://www.apmo-official.org/problems',
 'EGMO':'https://www.egmo.org/egmos/',
 'MEMO':'https://www.math.aau.at/MEMO/contests/previous/',
 'RMM':'https://www.bmoc.maths.org/home/rmm.shtml',
 'BMO':'https://bmos.ukmt.org.uk/home/balkan.shtml',
 'BalticWay':'https://www.math.olympiaadid.ut.ee/eng/html/?id=bw',
 'imc':'https://www.imc-math.org.uk/?item=problems',
 'putnam':'https://kskedlaya.org/putnam-archive/',
 'mmo':'https://mmo.mccme.ru/prasolov/index.htm',
}
SPANS={'IMO':(1959,2026),'APMO':(1989,2026),'EGMO':(2012,2026),'MEMO':(2007,2026),'RMM':(2008,2026),'BMO':(1984,2026),'BalticWay':(1990,2025),'imc':(1994,2026),'putnam':(1938,2025)}
EXCEPTIONS={'IMO':{1980:'не проводилась'},'RMM':{2014:'отменена (UKMT)',2022:'в официальном перечне выпусков отсутствует'},'putnam':{1943:'не проводилась',1944:'не проводилась',1945:'не проводилась'},'mmo':{1942:'не проводилась',1943:'не проводилась',1944:'не проводилась'}}

def years(r):
    if r.get('covers_years'):return r['covers_years']
    v=str(r.get('year',''))
    m=re.fullmatch(r'((?:19|20)\d{2})(?:[/–—-]((?:19|20)?\d{2}))?',v)
    if not m:return []
    a=int(m[1]);b=m[2]
    if not b:return [a]
    b=int(b) if len(b)==4 else a//100*100+int(b)
    if b==a+1:return [b] # school year: use end year, not two editions
    # Legacy metadata sometimes contains upload month or olympiad number
    # after the year. Keep the year as a candidate, never expand such pairs.
    return [a]

def compact(vals):
    vals=sorted(set(vals));chunks=[]
    for v in vals:
        if chunks and v==chunks[-1][-1]+1:chunks[-1].append(v)
        else:chunks.append([v])
    return ', '.join(str(x[0]) if len(x)==1 else f'{x[0]}–{x[-1]}' for x in chunks) or '—'

def main():
    groups=defaultdict(list)
    for raw in records_now():
        r=normalized(raw);r['source_record']=raw['record']
        cid='putnam' if r['contest'].startswith('putnam-') else r['contest']
        groups[(r['region'],cid)].append(r)
    result=[];flat=[]
    for (region,cid),rr in sorted(groups.items()):
        observed=sorted({y for r in rr if r['accepted_material'] for y in years(r)})
        span=SPANS.get(cid,(min(observed),2026) if observed else None)
        table=[]
        if span:
            for y in range(span[0],span[1]+1):
                entries=[r for r in rr if y in years(r)]
                kept=[r for r in entries if r['accepted_material']]
                sols=[r for r in kept if r['solution_bearing'] and 'shortlist' not in r['document_type']]
                short=[r for r in kept if 'shortlist' in r['document_type']]
                unclassified=[r for r in kept if r['document_type'].startswith('unclassified')]
                exception=EXCEPTIONS.get(cid,{}).get(y)
                state='edition_exception' if exception else 'no_downloaded_material' if not kept else 'solutions_present' if sols else 'materials_present_solutions_unconfirmed'
                row=dict(year=y,status=state,exception=exception,unique_documents=len({r['sha256'] for r in kept}),solution_documents=len({r['sha256'] for r in sols}),shortlist_documents=len({r['sha256'] for r in short}),unclassified_documents=len({r['sha256'] for r in unclassified}),season_labels=sorted({str(r['year']) for r in kept}),stages=sorted({str(r['stage']) for r in kept if r['stage']}),classes=sorted({str(r['classes']) for r in kept if r['classes']}),unknown_stage_documents=sum(not r['stage'] for r in kept),unknown_class_documents=sum(not r['classes'] for r in kept),files=[dict(path=r['path'],url=r['source_url'],type=r['document_type'],stage=r['stage'],classes=r['classes'],coverage_completeness=r['source_record'].get('coverage_completeness'),source_status=r.get('source_status'),final_url=r.get('final_url')) for r in kept],failed_urls=sorted({r['source_url'] for r in entries if r['status']!='downloaded'}))
                table.append(row);flat.append(dict(region=region,contest=cid,**{k:v for k,v in row.items() if k not in ['files','failed_urls']}))
        result.append(dict(region=region,contest=cid,reference=SOURCES.get(cid),scope='edition range from organizer index' if cid in SPANS else 'candidate interval from earliest dated downloaded material through 2026; earlier history and held editions not independently established',range=span,undated_material_documents=len({r['sha256'] for r in rr if r['accepted_material'] and not years(r)}),missing_material_years=[r['year'] for r in table if r['status']=='no_downloaded_material'],years_without_classified_final_solutions=[r['year'] for r in table if not r['exception'] and not r['solution_documents']],edition_exceptions=EXCEPTIONS.get(cid,{}),years=table,round_class_completeness='not established; one document never implies all classes/rounds covered'))
    # For newly recovered MEMO solution booklets, retain checkable problem IDs.
    memo=[]
    for line in (ROOT/'olympiads/international/manifest.jsonl').read_text().splitlines():
        r=json.loads(line)
        if r['contest']!='MEMO' or r['status']!='downloaded' or r['type']!='solutions' or 'skmo.sk/dokument.php' not in r['source']:continue
        t=subprocess.run(['pdftotext','-layout',str(ROOT/r['path']),'-'],capture_output=True,text=True,timeout=25).stdout
        ids=sorted({a+str(b) for a,b in re.findall(r'\b([IT])\s*[-–.]?\s*([1-8])\s*[.:]',t)})
        expected=['I'+str(n) for n in range(1,5)]+([] if r['year']==2020 else ['T'+str(n) for n in range(1,5 if r['year']<=2008 else 9)])
        memo.append(dict(year=r['year'],path=r['path'],source=r['source'],verified_headings=ids,missing_expected_headings=sorted(set(expected)-set(ids)),note='Heading extraction verifies identifiers, not mathematical correctness. No matches means manual check needed, not missing problems.'))
    output=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),method=['School years are assigned to end year, not expanded into two editions.','Explicit collection coverage overrides publication year.','Putnam mirrors are combined. Shortlist solutions are separate from final-contest solutions.','Unknown types, rounds and classes remain unknown. Missing material is a candidate gap unless edition existence independently established.','This compares the contests in the local register; it does not assert that every existing contest is included.'],contests=result,memo_booklet_heading_checks=memo)
    dest=ROOT/f'research/archive-year-reconciliation-{TAG}.json';dest.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    cp=ROOT/f'research/archive-year-reconciliation-{TAG}.csv'
    with cp.open('w',newline='') as f:
        keys=list(flat[0]);w=csv.DictWriter(f,fieldnames=keys,lineterminator="\n");w.writeheader()
        for row in flat:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v for k,v in row.items()})
    lines=['# Сверка олимпиад по годам','', 'Учебный год относится к году окончания. Наличие файла за год не подтверждает все классы, этапы и варианты. Shortlist IMO не засчитывается как проверенное решение финального тура. Для российских и малых вузовских архивов диапазон от первого датированного файла до 2026 — очередь проверки, а не утверждение о ежегодном проведении. Недатированные документы требуют отдельного разбора.','', '| Архив | Проверяемый диапазон | Нет скачанных материалов | Нет классифицированных решений финального конкурса | Недатированных документов |','|---|---|---|---|---:|']
    for c in result:
        span='—' if not c['range'] else f"{c['range'][0]}–{c['range'][1]}"
        lines.append(f"| {c['region']}/{c['contest']} | {span} | {compact(c['missing_material_years'])} | {compact(c['years_without_classified_final_solutions'])} | {c['undated_material_documents']} |")
    lines+=['','## Исключения и ещё не состоявшиеся выпуски','', 'IMO 1980 не проводилась. RMM 2014 отменена; 2022 отсутствует в официальном перечне выпусков. Putnam 1943–1945 и ММО 1942–1944 не проводились. Baltic Way 2026 назначен на 12–16 ноября; Putnam 2026 ещё впереди на дату этой сверки. Они не объявляются потерянными вариантами.','', '## Полнота по этапам и классам','', 'В JSON у каждого года есть файлы, источники, известные этапы, классы и число документов с неизвестными метаданными. Для всех российских годов полная сверка ожидаемых классов и этапов пока не установлена; наличие нескольких вариантов нельзя выдавать за полное покрытие. У MEMO дополнительно сохранены извлечённые номера задач I1–I4 и T1–T8 (в 2007–2008 командных задач четыре; в 2020 командного тура нет).','', '## Проверенные опорные страницы','']
    for cid,u in SOURCES.items():lines.append(f'- [{cid}]({u}).')
    lines+=['','Подробная матрица: `archive-year-reconciliation-2026-10-23.json`; компактная таблица для фильтрации: `archive-year-reconciliation-2026-10-23.csv`.']
    (ROOT/f'research/archive-year-reconciliation-{TAG}.md').write_text('\n'.join(lines)+'\n')
    print('Contest groups:',len(result),'year rows:',len(flat),'MEMO booklet checks:',len(memo))

if __name__=='__main__':main()
