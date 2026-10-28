"""Edition nine: stable exercise identities, dependency order, seven parts and art.

Input is the canonical thirty-chapter edition. Splits retain exercise identities;
all cross-references and illustration anchors are resolved after reordering.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import json,re
ROOT=Path(__file__).resolve().parents[2];BOOK=ROOT/'book/source';D=BOOK/'data'
PROOF=re.compile(r'\\begin\{proof\}(?:\[[^\n]*?\])?(.*?)\\end\{proof\}',re.S)
def task(q,a,advanced=False):return dict(q=q,a=a,advanced=advanced)
def restructure(canonical):
 canonical=deepcopy(canonical)
 for i,c in enumerate(canonical,1):
  c['id']=f'c{i:02d}'
  for j,t in enumerate(c['tasks'],1):t['uid']=f'c{i:02d}.{j}'
 original=deepcopy(canonical)
 for c in canonical:
  n=0
  def label(m):
   nonlocal n;n+=1
   return m[0]+r'\label{thm:legacy-'+c['id']+f'-{n}'+'}'
  c['theory']=re.sub(r'\\begin\{theorem\}(?:\[[^\n]*?\])?',label,c['theory'])
 by={c['id']:c for c in canonical}
 def split(src,ident,title,theory,indices):
  return dict(id=ident,title=title,theory=theory,tasks=[deepcopy(by[src]['tasks'][j-1])for j in indices],old=None)
 c=by['c12']
 a,b=c['theory'].split(r'\subsection*{Предел, монотонность и ограниченность}',1)
 prog=[1,2,3,4,5,6,7,8,9,10,11,13,14,15,16,18,19]
 by['c12-progressions']=split('c12','c12-progressions','Последовательности и прогрессии',a,prog)
 by['c12-limits']=split('c12','c12-limits','Предел последовательности и полнота чисел',r'\section*{Предел, монотонность и ограниченность}'+b,[j for j in range(1,25)if j not in prog])
 extra=[
 task(r'Докажи по определению, что \(1/n\to0\). Для \(\varepsilon=0{,}01\) укажи подходящий номер \(N\).',r'Выбираем целое \(N>1/\varepsilon\). Тогда \(n\ge N\) влечёт \(1/n\le1/N<\varepsilon\). Для заданной точности подходит \(N=101\).'),
 task(r'Докажи, что \(a_n=2-1/n\) возрастает, ограничена и сходится к \(2\).',r'\(a_{n+1}-a_n=1/(n(n+1))>0\), \(1\le a_n<2\), а \(|a_n-2|=1/n\to0\).'),
 task(r'Сходится ли \(a_n=(-1)^n\)? Обоснуй ответ.',r'Нет: чётная подпоследовательность равна \(1\), нечётная \(-1\). Если бы общий предел был \(L\), оба числа должны были бы лежать сколь угодно близко к \(L\), что невозможно.'),
 task(r'Найди предел \(\frac{3n+1}{n+2}\) и оцени ошибку через \(n\).',r'Предел \(3\), ошибка равна \(\frac5{n+2}\).'),
 task(r'Докажи, что сходящаяся действительная последовательность ограничена.',r'Начиная с некоторого \(N\), \(|a_n-L|<1\), то есть \(|a_n|<|L|+1\). Конечное число первых членов также ограничено; берём максимум этих границ.',True),
 task(r'Докажи единственность предела последовательности.',r'Если \(A\ne B\), возьмём \(\varepsilon=|A-B|/3\). Для достаточно большого \(n\) обе ошибки меньше \(\varepsilon\), откуда \(|A-B|\le|A-a_n|+|a_n-B|<2|A-B|/3\), противоречие.',True),
 task(r'Пусть \(a_n\le b_n\le c_n\) и \(a_n,c_n\to L\). Докажи \(b_n\to L\).',r'Для любой точности начиная с общего номера выполнено \(L-\varepsilon<a_n\le b_n\le c_n<L+\varepsilon\). Это определение предела.',True)]
 for j,t in enumerate(extra,1):t['uid']=f'new-sequence.{j}'
 by['c12-limits']['tasks']+=extra
 c=by['c14'];a,b=c['theory'].split(r'\section*{Гиперболические функции}',1)
 hyper,rules=b.split(r'\section*{Правила степеней',1)
 # Formal construction now follows monotone convergence; the early chapter
 # introduces e and points to this construction explicitly.
 start=a.index(r'\begin{definition}\term{Предел последовательности}')
 end=a.index(r'\begin{definition}\term{Экспонента}')
 construction=a[start:end]
 # Factorial has already been introduced in combinatorics.
 construction=re.sub(r'\\begin\{definition\}\\term\{Факториал\}.*?\\end\{definition\}\s*','',construction,flags=re.S)
 construction=re.sub(r'\\begin\{definition\}\\term\{Предел последовательности\}.*?\\end\{definition\}\s*','',construction,flags=re.S)
 construction=r'\section*{Построение числа \(e\)}\label{sec:e-construction}'+'\n'+r'Положим \(a_n=(1+1/n)^n\).'+construction
 by['c12-limits']['theory']+='\n'+construction
 early=r'''\begin{definition}\term{Число \(e\)} (\emph{Euler's number}) — стандартная положительная константа \(e\approx2{,}718281828\). Её точное определение как предела \((1+1/n)^n\) и доказательство существования даны в подразделе \ref{sec:e-construction}.\end{definition}
'''
 a=a[:start]+early+a[end:]
 hi=[20]+list(range(25,42));ex=[j for j in range(1,42)if j not in hi]
 by['c14-exponential']=split('c14','c14-exponential','Степени, экспонента и логарифмы',a+r'\section*{Правила степеней'+rules,ex)
 by['c14-hyperbolic']=split('c14','c14-hyperbolic','Гиперболические функции',r'\section*{Гиперболические функции}'+hyper,hi)
 c=by['c23'];p=json.loads((D/'polynomial-formulas-full.json').read_text())
 base=json.loads((D/'new-chapter-23.json').read_text());n=len(base['tasks'])
 # The first heading of the appended manuscript is unchanged by labelling.
 heading=re.search(r'\\section\*\{[^\n]+',p['theory'])[0]
 cut=c['theory'].index(heading)
 by['c23-complex']=split('c23','c23-complex','Комплексные числа',c['theory'][:cut],range(1,n+1))
 by['c23-radicals']=split('c23','c23-radicals','Формулы Кардано и Феррари',c['theory'][cut:],range(n+1,len(c['tasks'])+1))
 by['c30']['theory']+='\n'+(D/'edition9-taylor.tex').read_text()
 by['c17']['theory']+='\n'+(D/'edition9-amgm.tex').read_text()
 add=json.loads((D/'edition9-improper.json').read_text());by['c29']['theory']+='\n'+add['theory']
 for j,t in enumerate(add['tasks'],1):t['uid']=f'new-improper.{j}'
 by['c29']['tasks']+=add['tasks']
 # This algebra chapter precedes differentiation: define the operator directly.
 t=by['c26']['tasks'][19]
 t['q']=r'Пусть \(D:\mathcal P_3\to\mathcal P_2\) задано формулой \(D(a_0+a_1t+a_2t^2+a_3t^3)=a_1+2a_2t+3a_3t^2\). Докажи линейность, найди ядро и образ. Позже этот оператор будет называться производной многочлена.'
 t['a']=r'Линейность проверяется по коэффициентам. Ядро — постоянные многочлены. Любой \(a+bt+ct^2\) есть образ \(at+\frac b2t^2+\frac c3t^3\), поэтому образ равен \(\mathcal P_2\). Размерности \(1\) и \(3\).'
 newids=['plane-geometry','solid-geometry','multivariable','multiple-integrals','line-surface-integrals','probability','random-variables','statistics']
 for ident in newids:
  c=json.loads((D/(ident+'.json')).read_text());by[ident]=c
  for j,t in enumerate(c['tasks'],1):t['uid']=f'{ident}.{j}'
 # Edition ten fills school-exam gaps while retaining every earlier exercise.
 examids=['exam-measurements','exam-graphs','exam-models','exam-functions',
          'exam-rational','exam-exponential','exam-trigonometric','exam-parameters',
          'exam-plane','exam-solid']
 for ident in examids:
  c=json.loads((D/(ident+'.json')).read_text());by[ident]=c
  c['theory']=re.sub(r'\\par(?=[А-Яа-яЁё])',lambda m:m[0]+' ',c['theory'])
  if ident in ('exam-measurements','exam-graphs','exam-models','exam-functions'):
   from exam_style import math_style
   c['theory']=math_style(c['theory'])
   for t in c['tasks']:
    for key in ('q','a'):t[key]=math_style(t[key])
  c['theory']+='\n\\relax\n'
  c['art_anchors']=[[a,r'\relax'if b=='END_THEORY'else b]for a,b in c['art_anchors']]
  for j,t in enumerate(c['tasks'],1):t['uid']=f'{ident}.{j}'
 # Rolle and Lagrange belong before the first systematic derivative sign test.
 source=by['c29']['theory'];start=source.index(r'\begin{theorem}[Ролль')
 stop=source.index(r'\end{proof}',source.index(r'\begin{theorem}[Лагранж',start))+len(r'\end{proof}')
 by['c20']['theory']+='\n\\section{Теоремы о среднем значении}\n'+source[start:stop]
 by['c29']['theory']=source[:start]+source[stop:]
 by['c20']['theory']=by['c20']['theory'].replace('В этой главе монотонность конкретной функции проверяем','Сначала монотонность конкретной функции проверяем')
 calc=json.loads((D/'exam-calculus.json').read_text())
 ca,cb=calc['theory'].split(r'\section{Площадь, первообразная и знак}',1)
 by['c20']['theory']+='\n'+ca+'\n\\relax\n'
 by['c29']['theory']+='\n'+r'\section{Площадь, первообразная и знак}'+cb
 for j,t in enumerate(calc['tasks'],1):
  t['uid']=f'exam-calculus.{j}'
  by['c20'if j<=14 else'c29']['tasks'].append(t)
 stats=json.loads((D/'exam-statistics.json').read_text())
 by['statistics']['theory']+='\n'+stats['theory']
 for j,t in enumerate(stats['tasks'],1):
  t['uid']=f'exam-statistics.{j}';by['statistics']['tasks'].append(t)
 for ident,text in json.loads((D/'exam-worked-basics.json').read_text()).items():
  by[ident]['theory']+='\n'+text
 final_coverage=json.loads((D/'exam-final-coverage.json').read_text())
 for ident,extra in final_coverage.items():
  by[ident]['theory']+='\n'+extra['theory']
  for j,t in enumerate(extra['tasks'],1):
   t['uid']=f'exam-final-{ident}.{j}';by[ident]['tasks'].append(t)
 # Independently reviewed prerequisites and deeper applications retain all UIDs.
 for ident,fix in json.loads((D/'review-school-clarifications.json').read_text()).items():
  assert by[ident]['theory'].count(fix['before'])==1,(ident,fix['before'])
  by[ident]['theory']=by[ident]['theory'].replace(fix['before'],fix['text']+'\n'+fix['before'])
 review_intros=json.loads((D/'review-art-intros.json').read_text())
 last_intros={
  'exam-parameters':r'Симметрия уравнения иногда определяет ответ раньше вычислений. Если замена знака одной координаты сохраняет всю систему, любое решение с ненулевой этой координатой имеет отличного от него партнёра. Поэтому единственную пару следует искать на оси симметрии. Полученные на оси значения параметра остаются лишь кандидатами: каждый нужно проверить на существование других точек вне оси. Для исключения лишних решений удобно собрать исходное равенство в сумму неотрицательных выражений. Тогда равенство нулю одновременно заставляет каждое слагаемое обращаться в нуль. Границы координат берут из второго уравнения системы, а знак каждого выражения проверяют на всём допустимом промежутке. Так устанавливают и необходимость, и достаточность ответа.',
  'exam-functions':r'Чтение диаграммы начинается с того, какая величина отложена по каждой оси и в каких единицах она измеряется. Нулевой уровень, отрицательная высота и отсутствие столбца имеют разные значения. При сравнении двух моментов надо различать изменение на несколько единиц и изменение в несколько раз. Вопрос о первом подходящем месяце требует проверить порядок месяцев, а не только наибольший столбец. Если график соединяет отмеченные точки, точный ответ по изображению надёжнее извлекать в отмеченных узлах; поведение между ними должно быть задано отдельно. Для физической зависимости название оси также указывает, какая величина изменяется, а какая определяется по графику.'}
 for name in ['review-ege-depth.json','review-ege-last-gap.json']:
  for ident,extra in json.loads((D/name).read_text()).items():
   if ident=='metadata':continue
   intro=(review_intros if name=='review-ege-depth.json'else last_intros)[ident]
   by[ident]['theory']+='\n'+intro+'\n\\relax\n'+extra['theory']
   for t in extra['tasks']:
    t['advanced']=t.pop('hard',t.get('advanced',False));by[ident]['tasks'].append(t)
 ml=json.loads((D/'review-ml-bridge.json').read_text())
 for ident,extra in ml['additions'].items():
  by[ident]['theory']+='\n'+extra['theory'];by[ident]['tasks']+=extra['tasks']
 by[ml['chapter']['id']]=ml['chapter']
 from integrate_deep_review import integrate
 integrate(by,D)
 extra_review_art=json.loads((D/'review-extra-art.json').read_text())
 for entry in extra_review_art:
  chapter=by[entry['chapter']]
  assert chapter['theory'].count(entry['before'])==1,entry
  chapter['theory']=chapter['theory'].replace(entry['before'],entry['before']+'\n'+entry['text']+'\n\\relax\n')
 gap_review_art=json.loads((D/'review-gap-art.json').read_text())
 for entry in gap_review_art:
  if 'text'not in entry:continue
  chapter=by[entry['chapter']];marker=entry['before'];assert chapter['theory'].count(marker)==1
  text=entry['text']+'\n\\relax\n'
  chapter['theory']=chapter['theory'].replace(marker,(text+marker)if entry['position']=='before'else(marker+'\n'+text))
 by['c10']['theory']=by['c10']['theory'].replace(r'\begin{theorem}[Правило произведения (product rule)]',r'\Needspace{8\baselineskip}\begin{theorem}[Правило произведения (product rule)]')
 by['c22']['theory']+='\n'+(D/'olympiad-prerequisites.tex').read_text()
 # The archive stage is explicitly authorised. Keep every earlier task and UID.
 olympiad_sources=json.loads((ROOT/'book/references/olympiad-book-sources.json').read_text())
 olympiad_tasks=json.loads((D/'olympiad-selected.json').read_text())
 for item in olympiad_tasks:
  olympiad_task=deepcopy(item);ident=olympiad_task.pop('chapter')
  olympiad_task['a']=r'\textbf{Ответ.} '+olympiad_task.pop('answer')+r'\par\nopagebreak[4]\textit{Решение.} '+olympiad_task.pop('solution')+r'\hfill\(\blacksquare\)'
  source=olympiad_sources[olympiad_task['olympiad']['source_id']]
  olympiad_task['olympiad']['url']=source['source_url']
  olympiad_task['olympiad']['translation']=source['contest'] in ('IMO','APMO','imc','putnam-maa')
  by[ident]['tasks'].append(olympiad_task)
 parts=json.loads((D/'book-structure.json').read_text());ids=[i for p in parts for i in p['chapters']];ordered=[by[i]for i in ids]
 assert len(ids)==len(set(ids))==52
 assert all(len(c['tasks'])>=10 for c in ordered)
 dest={t['uid']:(i,j)for i,c in enumerate(ordered,1)for j,t in enumerate(c['tasks'],1)}
 oldids={t['uid']for c in original for t in c['tasks']}
 assert len(oldids)==790 and oldids<=dest.keys()
 assert len(dest)==sum(len(c['tasks'])for c in ordered)
 flow=[]
 for entry in json.loads((D/'edition8-cats-flow.json').read_text()):
  e=deepcopy(entry);src=original[e['chapter']-1];candidates=[]
  if e['kind']=='proof':
   proofs=list(PROOF.finditer(src['theory']));body=proofs[e['index']-1][1]
   for i,c in enumerate(ordered,1):
    for j,m in enumerate(PROOF.finditer(c['theory']),1):
     if m[1]==body:candidates.append((i,j))
   assert len(candidates)==1,(e,candidates)
   e['chapter'],e['index']=candidates[0]
  elif e['kind']=='prose':
   candidates=[(i,c)for i,c in enumerate(ordered,1)if e['start']in c['theory']]
   assert len(candidates)==1,(e,[i for i,c in candidates])
   e['chapter']=candidates[0][0]
  else:
   targets=[dest[f"{src['id']}.{j}"]for j in range(e['start'],e['end']+1)]
   chosen=Counter(i for i,j in targets).most_common(1)[0][0]
   js=[j for i,j in targets if i==chosen]
   e.update(chapter=chosen,start=min(js),end=max(js))
  flow.append(e)
 for k,ident in enumerate(newids):
  i=ids.index(ident)+1;c=by[ident];art=136+k*6
  for j,(start,end)in enumerate(c['art_anchors']):flow.append(dict(kind='prose',chapter=i,start=start,end=end,art=art+j,side='r'if j%2==0 else'l'))
  # Prefer the shortest self-contained proof to keep the wrap block short.
  proofs=list(PROOF.finditer(c['theory']));pj=min(range(len(proofs)),key=lambda j:len(proofs[j][1]))+1
  flow.append(dict(kind='proof',chapter=i,index=pj,art=art+3,side='l'))
  flow.append(dict(kind='tasks',chapter=i,start=6,end=9,art=art+4,side='r'))
  flow.append(dict(kind='answers',chapter=i,start=8,end=11,art=art+5,side='l'))
 for j,p in enumerate(parts,1):flow.append(dict(kind='part',part=j,art=p['art']))
 # Three additional pictures bridge gaps introduced by chapter splits.
 flow.extend([
  dict(kind='tasks',chapter=ids.index('c01')+1,start=10,end=16,art=191,side='l'),
  dict(kind='proof',chapter=ids.index('c11')+1,index=1,art=192,side='r'),
  dict(kind='prose',chapter=ids.index('c14-exponential')+1,start='Рассмотрим учебную модель: на счёте',end=r'\begin{definition}',art=193,side='l'),
 ])
 for k,ident in enumerate(examids):
  i=ids.index(ident)+1;c=by[ident];art=194+6*k
  for j,(start,end)in enumerate(c['art_anchors']):
   flow.append(dict(kind='prose',chapter=i,start=start,end=end,art=art+j,side='r'if j%2==0 else'l'))
  proofs=list(PROOF.finditer(c['theory']));pj=min(range(len(proofs)),key=lambda j:len(proofs[j][1]))+1
  flow.append(dict(kind='proof',chapter=i,index=pj,art=art+3,side='l'))
  flow.append(dict(kind='tasks',chapter=i,start=6,end=9,art=art+4,side='r'))
  flow.append(dict(kind='answers',chapter=i,start=8,end=11,art=art+5,side='l'))
 # Balance a crowded modelling page with the longer progression exercises.
 flow=[entry for entry in flow if entry['art']!=208]
 flow.append(dict(kind='tasks',chapter=ids.index('c12-progressions')+1,start=12,end=17,art=208,side='r'))
 for j,(start,end)in enumerate(calc['art_anchors']):
  if end==r'\section{Площадь':end=r'\relax'
  flow.append(dict(kind='prose',chapter=ids.index('c20')+1,start=start,end=end,art=254+j,side='l'if j==0 else'r'))
 flow.append(dict(kind='prose',chapter=ids.index('statistics')+1,start='На столбчатой диаграмме',end=r'\begin{center}',art=256,side='l'))
 # Longer school-geometry proofs and the enlarged answer section need their
 # own unique illustrations, rather than repeating any existing kitten.
 flow.extend([
  dict(kind='proof',chapter=ids.index('exam-plane')+1,index=3,art=257,side='r'),
  dict(kind='proof',chapter=ids.index('exam-plane')+1,index=12,art=258,side='r'),
  dict(kind='proof',chapter=ids.index('exam-solid')+1,index=2,art=259,side='l'),
  dict(kind='answers',chapter=ids.index('c06')+1,start=8,end=13,art=260,side='r'),
  dict(kind='answers',chapter=ids.index('exam-plane')+1,start=27,end=30,art=261,side='r'),
 ])
 for art,ident in [(262,'c04'),(263,'random-variables')]:
  start,end=final_coverage[ident]['art_anchor']
  flow.append(dict(kind='prose',chapter=ids.index(ident)+1,start=start,end=end,art=art,side='r'if art==262 else'l'))
 for art,(ident,intro)in enumerate(review_intros.items(),264):
  flow.append(dict(kind='prose',chapter=ids.index(ident)+1,start=intro[:70],end=r'\relax',art=art,side='r'if art%2==0 else'l'))
 for art,ident in [(273,'c26'),(274,'c27')]:
  start,end=ml['additions'][ident]['art_anchors'][0]
  flow.append(dict(kind='prose',chapter=ids.index(ident)+1,start=start,end=end,art=art,side='l'if art==273 else'r'))
 for j,(start,end)in enumerate(ml['chapter']['art_anchors']):
  flow.append(dict(kind='prose',chapter=ids.index('ml-foundations')+1,start=start,end=end,art=275+j,side='r'if j%2==0 else'l'))
 for art,ident in [(280,'exam-parameters'),(281,'exam-functions')]:
  flow.append(dict(kind='prose',chapter=ids.index(ident)+1,start=last_intros[ident][:70],end=r'\relax',art=art,side='l'if art==280 else'r'))
 flow.extend([
  dict(kind='tasks',chapter=ids.index('ml-foundations')+1,start=6,end=9,art=278,side='r'),
  dict(kind='answers',chapter=ids.index('ml-foundations')+1,start=8,end=11,art=279,side='l'),
  dict(kind='answers',chapter=ids.index('exam-parameters')+1,start=35,end=38,art=282,side='l'),
  dict(kind='answers',chapter=ids.index('ml-foundations')+1,start=16,end=20,art=283,side='r'),
 ])
 for entry in extra_review_art:
  flow.append(dict(kind='prose',chapter=ids.index(entry['chapter'])+1,start=entry['text'][:70],end=r'\relax',art=entry['art'],side='r'if entry['art']%2==0 else'l'))
 for entry in gap_review_art:
  if 'text'in entry:
   flow.append(dict(kind='prose',chapter=ids.index(entry['chapter'])+1,start=entry['text'][:70],end=r'\relax',art=entry['art'],side='r'if entry['art']%2==0 else'l'))
  else:flow.append(dict(kind=entry['kind'],chapter=ids.index(entry['chapter'])+1,start=entry['start'],end=entry['end'],art=entry['art'],side=entry['side']))
 for entry in json.loads((D/'olympiad-art-flow.json').read_text()):
  first=dest[entry['start_uid']];last=dest[entry['end_uid']]
  assert first[0]==last[0] and first[1]<=last[1]
  flow.append(dict(kind=entry['kind'],chapter=first[0],start=first[1],end=last[1],art=entry['art'],side=entry.get('side','r')))
 for entry in flow:
  if entry['art']>=194 or entry['art']==49:entry.update(minheight=58,vspace=2,parskip=2)
  if entry['art'] in (130,152):entry.update(minheight=58,vspace=2,parskip=1)
  if entry['art']==92:entry.update(minheight=58,vspace=2,parskip=2)
 # Anchor strings are remapped by the same substitution as the manuscript.
 default={i:f'c{i:02d}'for i in range(1,31)};default.update({12:'c12-limits',14:'c14-exponential',23:'c23-complex'})
 def refs(s):
  s=re.sub(r'(глав[аеуы]\s+)(\d+)\b',lambda m:m[1]+r'\ref{chap:'+default[int(m[2])]+'}',s)
  s=re.sub(r'((?:теорем[а-я]*|Теорем[а-я]*)\s+)(\d+)\.(\d+)',lambda m:m[1]+r'\ref{thm:legacy-c'+f'{int(m[2]):02d}-{m[3]}'+'}',s)
  s=re.sub(r'((?:задач[а-я]*|Задач[а-я]*)\s+)(\d+)\.(\d+)',lambda m:m[1]+'.'.join(map(str,dest[f'c{int(m[2]):02d}.{m[3]}'])),s)
  return s.replace(r'\arctan',r'\operatorname{arctg}').replace(r'\mathbf',r'\symbf').replace(r'\boldsymbol',r'\symbf')
 for c in ordered:
  if c['id']=='c21':c['theory']=c['theory'].replace('В следующей главе мы сравним',r'В главе \ref{chap:c22} мы сравним')
  if c['id']=='c18':c['theory']=c['theory'].replace('из предыдущей главы теперь читается',r'из главы \ref{chap:c17} теперь читается')
  if c['id']=='c20':c['theory']=c['theory'].replace('доказанный в предыдущей главе предел',r'доказанный в главе \ref{chap:c19} предел')
  c['theory']=refs(c['theory'])
  # Number subject sections while keeping subordinate hierarchy intact.
  c['theory']=c['theory'].replace(r'\subsubsection*',r'\subsection').replace(r'\section*',r'\section').replace(r'\subsection*',r'\subsection')
  for t in c['tasks']:
   for key in ['q','a']:t[key]=refs(t[key])
   if 'как в задаче 9' in t['a']:t['a']=t['a'].replace('как в задаче 9','как в задаче '+'.'.join(map(str,dest['c16.9'])))
 for e in flow:
  if e['kind']=='prose':
   for key in ['start','end']:e[key]=refs(e[key]).replace(r'\section*',r'\section').replace(r'\subsection*',r'\subsection')
 (BOOK/'cats-flow.json').write_text(json.dumps(flow,ensure_ascii=False,indent=2)+'\n')
 # Record every retained old exercise and any prerequisite clarification.
 changes=[]
 for c in original:
  for t in c['tasks']:
   i,j=dest[t['uid']];new=ordered[i-1]['tasks'][j-1]
   if t['q']!=new['q']or t['a']!=new['a']:changes.append(dict(uid=t['uid'],published=f'{i}.{j}',reason='explicit algebraic definition'if t['uid']=='c26.20'else'reference/notation normalization'))
 report=dict(original_exercises=len(oldids),retained_once=len(oldids),total_exercises=len(dest),chapters=len(ordered),parts=len(parts),mapping={uid:'.'.join(map(str,dest[uid]))for uid in sorted(oldids)},clarifications=changes)
 (ROOT/'book/references/book-edition11-exercise-preservation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 return ordered,parts,flow
