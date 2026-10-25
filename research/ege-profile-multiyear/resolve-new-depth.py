from pathlib import Path
import json,re,hashlib,collections
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'research/ege-profile-multiyear'
old=json.loads((P/'coverage.json').read_text());depthpath=ROOT/'sources/book/data/review-ege-depth.json';depth=json.loads(depthpath.read_text())
def ex(cid,*nums):return [f'ex:review-ege-{cid}-{n}' for n in nums]
def tasks(g,*nums):return [f'review-ege.{g}.{n}' for n in nums]
refs={
 'data-read':(ex('exam-functions',1,2),tasks('G4',1,2,3,4)),
 'derivative-sign':([],tasks('G4',5)),
 'tangent-slope':([],tasks('G4',6)),
 'derivative-extremum':([],tasks('G4',5)),
 'prism-side-scale':([],tasks('G5',6)),
 'mixture':(ex('exam-models',1),tasks('G3',1)),
 'ext-trig':(ex('c20',1),tasks('G6',2)),
 'log-ineq':(ex('exam-exponential',1,2),tasks('G7',1,2,3,5)),
 'finance-schedule':(ex('exam-models',2),tasks('G3',2,3,4)),
 'optimization-profit':(ex('exam-models',3),tasks('G3',5)),
 'optimization-weighted':(ex('exam-models',4),tasks('G3',6)),
 'optimization-physics':(ex('c20',2,3),tasks('G6',1,3)),
 'recover-graph':(ex('exam-functions',1),tasks('G4',1,2,3)),
 'intersection-graph':(ex('exam-functions',2),tasks('G4',4)),
 'solid-prism-side':(ex('exam-solid',1,2),tasks('G5',4,5)),
 'plane-advanced':(ex('exam-plane',1,2,3),tasks('G5',1,2,3)),
 'param-circles':(ex('exam-parameters',2),tasks('G1',1)),
 'param-branches':(ex('exam-parameters',1),tasks('G1',2,3,6)),
 'param-interval':(ex('exam-parameters',3),tasks('G1',4,5)),
 'param-nonlinear':(ex('exam-parameters',1),tasks('G1',6)),
 'discrete-average':(ex('c21',3)+ex('c17',2),tasks('G2',6)),
 'discrete-pair':(ex('c21',2),tasks('G2',3,4)),
 'discrete-subsets':(ex('c21',1),tasks('G2',1,2)),
 'discrete-cards':(ex('c17',3),tasks('G2',6)),
 'discrete-coins':(ex('c17',1),tasks('G2',5)),
 'discrete-digits':(ex('c21',4),tasks('G2',1,2)),
 'discrete-letters':(ex('c17',2),tasks('G2',6)),
 'param-polynomial':(ex('exam-parameters',4),tasks('G1',2,3)),
 'exp-polynomial-ineq':(ex('exam-exponential',3),tasks('G7',6)),
}
alltasks={t['uid'] for c in depth.values() for t in c['tasks']};labels={l for c in depth.values() for l in re.findall(r'\\label\{([^}]+)\}',c['theory'])}
rows=[]
for r in old['rows']:
 if r['status']!='partial':continue
 e,t=refs[r['method_id']];assert set(e)<=labels;assert set(t)<=alltasks
 status='targeted_supplement_added_independent_review_required';remain='Повторно сопоставить полное условие и новый разбор; рост числа задач сам по себе не меняет статус покрытия.'
 if r['method_id']=='param-nonlinear':
  status='prerequisites_strengthened_not_fully_resolved';remain='Новый пример обучает ветвям и симметрии, но полного разбора показательно-модульной системы открытого2026 №18 во фрагменте нет. Эту строку нельзя объявлять закрытой без отдельной проверки/разбора.'
 elif r['method_id']=='data-read':
  status='adjacent_graph_practice_added_direct_data_reading_recheck_required';remain='Новые рисунки тренируют координатную сетку и формулу функции. Для табличных/погодных диаграмм нужна отдельная повторная оценка имеющихся глав; прямое дополнительное упражнение на столбчатую диаграмму этот фрагмент не добавляет.'
 rows.append({'year':r['year'],'variant_kind':r['variant_kind'],'task_number':r['task_number'],'alternative':r['alternative'],'method_id':r['method_id'],'group':r['gap'].split(':')[0],'old_status':'partial','source_url':r['source_url'],'new_example_labels':list(e),'new_task_uids':list(t),'resolution_status':status,'remaining_check':remain})
# Second isolated supplement closes the eight explicitly carried gaps, without promoting audit status.
lastpath=ROOT/'sources/book/data/review-ege-last-gap.json'
lastmeta=None
if lastpath.exists():
 last=json.loads(lastpath.read_text());lastuids={t['uid'] for c in last.values() for t in c['tasks']}
 lastlabels={l for c in last.values() for l in re.findall(r'\\label\{([^}]+)\}',c['theory'])}
 lastmeta={'path':str(lastpath.relative_to(ROOT)),'sha256':hashlib.sha256(lastpath.read_bytes()).hexdigest(),'tasks':len(lastuids),'figure':'sources/book/images/review-ege-data-reading.pdf'}
 for r in rows:
  if r['method_id']=='data-read':
   r['new_example_labels'].append('ex:review-ege-last-data')
   resistance=(r['year'] in (2020,2021) and r['alternative']==2)
   r['new_task_uids'].append('review-ege-last.G4.2' if resistance else 'review-ege-last.G4.1')
   r['resolution_status']='specific_data_graph_example_and_practice_added_independent_review_required'
   r['remaining_check']='Проверить изображение, читаемость шкал и ответы. Новая панельA тренирует порог, знак и первое точное совпадение; панельB — разность сопротивлений при заданных значениях тока. Прямой содержательный пробел дополнен; автоматического перевода вcovered-method нет.'
   r['new_figure']='sources/book/images/review-ege-data-reading.pdf'
  elif r['method_id']=='param-nonlinear':
   r['new_example_labels']+=['ex:review-ege-last-monotone','ex:review-ege-last-full-system']
   r['new_task_uids']+=['review-ege-last.G1.1','review-ege-last.G1.2']
   r['resolution_status']='full_source_solution_and_two_analogues_added_independent_review_required'
   r['remaining_check']='Официальный пиксельный оригинал показывает7|x|+1, а не7|x+1|. Полный элементарный разбор вexam-parameters: чётность поx ограничивает единственное решение значениемx=0; кандидатыa=1,17; второй отвергнут тремя решениями; первый доказан суммой неотрицательных слагаемых. Ответa=1, единственная пара(0,1). Два самостоятельных аналога имеют точные ответы−7и3. Проверить транскрипцию по2026-open/task18-evidence.json и повторно проверить доказательство; производные не требуются.'
   r['additional_prerequisites']=['c07','c14-exponential','exam-parameters']
  assert set(r['new_example_labels'])<=labels|lastlabels
  assert set(r['new_task_uids'])<=alltasks|lastuids
assert len(rows)==131
summary={'checked_at':'2026-10-25','old_audit_snapshot_sha256':old['book_data_sha256'],'supplement_path':str(depthpath.relative_to(ROOT)),'supplement_sha256':hashlib.sha256(depthpath.read_bytes()).hexdigest(),'supplement_tasks':39,'supplement_examples':28,'last_gap_supplement':lastmeta,'principle':'Authored additions mapped to the old partial findings; no automatic promotion to covered-method. Parent integration, figures and independent mathematical/layout review remain separate.','finding_rows':len(rows),'rows':rows,'status_counts':dict(collections.Counter(r['resolution_status'] for r in rows))}
(P/'findings-resolution.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(P/'new-example-labels.json').write_text(json.dumps({cid:re.findall(r'\\label\{([^}]+)\}',c['theory']) for cid,c in depth.items()},ensure_ascii=False,indent=2)+'\n')
print(summary['status_counts'])
