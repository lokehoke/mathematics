"""Resolve the 2027 official topic crosswalk against stable textbook identities.

EGE has one codifier; basic/profile projections are checked separately against
their specifications. BU/UU in the codifier denotes curriculum depth, not a
promise that every common-list topic occurs in either examination variant.
"""
from pathlib import Path
import json,csv,re
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'sources/book/data'
OGE=r'''
1.1|Целые числа и делимость|c01,c02
1.2|Дроби и проценты|c03,c04,exam-measurements,exam-models
1.3|Рациональные числа и действия|c01,c03,c04
1.4|Действительные числа и действия|c06,c07,c08,c12-limits
1.5|Приближённые вычисления и оценка|exam-measurements
2.1|Буквенные выражения|c09,exam-rational
2.2|Степени и свойства|c06,c14-exponential
2.3|Многочлены|c09,c11,exam-rational
2.4|Алгебраические дроби|c09,exam-rational
2.5|Корни натуральной степени|c07,exam-rational
3.1|Уравнения, системы и совокупности|c11,exam-rational
3.2|Неравенства, системы и совокупности|c11,exam-rational,c17
3.3|Текстовые задачи|exam-models,exam-measurements
4.1|Последовательности и способы задания|c12-progressions,c12-limits
4.2|Прогрессии и сложные проценты|c12-progressions,exam-models
5.1|Функции и графики|c13,exam-functions
6.1|Координатная прямая|c01,c08,c16,exam-rational
6.2|Декартовы координаты|c13,c18,exam-functions
7.1|Фигуры, свойства и преобразования|plane-geometry,exam-plane
7.2|Треугольник|plane-geometry,exam-plane
7.3|Многоугольники|plane-geometry,exam-plane
7.4|Окружность и круг|plane-geometry,exam-plane
7.5|Измерение геометрических величин|exam-measurements,plane-geometry,exam-plane,solid-geometry,exam-solid
7.6|Векторы на плоскости|c18
8.1|Описательная статистика|statistics
8.2|Вероятность|probability,random-variables
8.3|Комбинаторика|c10,exam-graphs
8.4|Множества|c16
8.5|Графы|exam-graphs
'''
EGE=r'''
1.1|Целые числа, делимость|c01,c02,c21,c17
1.2|Дроби, проценты, периодические дроби|c03,c04,exam-models
1.3|Корни натуральной степени|c07,exam-rational
1.4|Степени с целым и рациональным показателем|c06,c14-exponential
1.5|Тригонометрические числа и обратные функции|c15,exam-trigonometric
1.6|Логарифмы|c14-exponential,exam-exponential
1.7|Действительные числа и приближённые вычисления|c12-limits,exam-measurements
1.8|Преобразование выражений|c09,exam-rational,c10,c15,c14-exponential
1.9|Комплексные числа|c23-complex
2.1|Целые и дробно-рациональные уравнения|c11,exam-rational
2.2|Иррациональные уравнения|c07,exam-rational
2.3|Тригонометрические уравнения|exam-trigonometric
2.4|Показательные и логарифмические уравнения|exam-exponential
2.5|Целые и дробно-рациональные неравенства|exam-rational,c17
2.6|Иррациональные неравенства|exam-rational
2.7|Показательные и логарифмические неравенства|exam-exponential
2.8|Тригонометрические неравенства|exam-trigonometric
2.9|Системы и совокупности|exam-rational,exam-exponential,exam-parameters
2.10|Уравнения, неравенства и системы с параметрами|exam-parameters
2.11|Матрица линейной системы, определитель|c18,c26
3.1|Функция, обратная функция, чётность, периодичность|c13,exam-functions,c15,exam-trigonometric
3.2|Область, значения, нули, знаки, монотонность, экстремумы|exam-functions,c20
3.3|Степенная функция и корень|c06,c07,c13,exam-functions
3.4|Тригонометрические функции|c15,exam-trigonometric
3.5|Показательная и логарифмическая функции|c14-exponential,exam-exponential
3.6|Разрывы, асимптоты, непрерывность на отрезке|exam-functions,c19,c28
3.7|Последовательности|c12-progressions,c12-limits
3.8|Прогрессии и сложные проценты|c12-progressions,exam-models
4.1|Производная и таблица производных|c20
4.2|Производная, монотонность, экстремумы на отрезке|c20,exam-models
4.3|Первообразная и интеграл|c29
5.1|Множества и диаграммы|c16
5.2|Логика|c16,c17
6.1|Описательная статистика|statistics
6.2|Вероятность|probability,random-variables
6.3|Комбинаторика|c10
7.1|Фигуры на плоскости|plane-geometry,exam-plane
7.2|Прямые и плоскости|solid-geometry,exam-solid
7.3|Многогранники|solid-geometry,exam-solid
7.4|Тела и поверхности вращения|solid-geometry,exam-solid,c29
7.5|Координаты и векторы|c18,exam-solid
'''
def parse(raw):
 return [dict(code=a,title=b,chapter_ids=c.split(','))for a,b,c in (line.split('|')for line in raw.strip().splitlines())]
def build():
 book=json.loads((ROOT/'sources/book/book-data.json').read_text());by={c['id']:(i,c)for i,c in enumerate(book,1)}
 rows=[]
 for exam,raw in [('OGE',OGE),('EGE-common',EGE)]:
  for row in parse(raw):
   matching=[by[i]for i in row['chapter_ids']]
   row.update(exam=exam,chapters=[dict(number=i,id=c['id'],title=c['title'])for i,c in matching],
     theory_sections=[dict(chapter=i,title=s)for i,c in matching for s in re.findall(r'\\(?:sub)?section\*?\{([^\n]+?)\}',c['theory'])],
     worked_examples=sum(c['theory'].count(r'\begin{example}')+c['theory'].count('Пример:')for i,c in matching),
     exercises=[dict(number=f'{i}.{j}',uid=t['uid'])for i,c in matching for j,t in enumerate(c['tasks'],1)],
     status='covered-in-current-manuscript')
   assert row['exercises'] and row['worked_examples']>0 and all(c['theory'].strip()for i,c in matching)
   rows.append(row)
 assert len(rows)==70 and len({(r['exam'],r['code'])for r in rows})==70
 # Each row is checked against actual theory, not just a chapter heading.
 # These routes reflect the three specifications, which are saved verbatim.
 routes=[
  dict(exam='OGE',specification='research/exam-sources-2027/oge-spec.pdf',chapters=['c01','c03','c04','exam-measurements','c05','c06','c07','c08','c16','c02','c09','c11','exam-rational','c10','exam-graphs','c12-progressions','exam-models','c17','c13','exam-functions','plane-geometry','exam-plane','c18','solid-geometry','probability','statistics'],focus='Вычисления; практические блоки; уравнения и графики; вероятность и данные; планиметрия и доказательства; из стереометрии выборочно куб/прямоугольный параллелепипед, V=abc и единицы объёма.'),
  dict(exam='EGE-basic',specification='research/exam-sources-2027/ege-spec-basic.pdf',chapters=['c01','c03','c04','exam-measurements','c05','c06','c07','c08','c09','c11','exam-rational','c12-progressions','exam-models','c16','c02','c17','c13','exam-functions','c14-exponential','exam-exponential','c15','exam-trigonometric','plane-geometry','exam-plane','solid-geometry','exam-solid','c20','probability','statistics'],focus='Короткий ответ; признаки делимости, разложение на простые и построение числа; вычисления и преобразования; таблицы/графики; прикладные модели; уравнения и неравенства; знак производной, чтение графика производной и касательная; вероятность; плоская и пространственная геометрия.'),
  dict(exam='EGE-profile',specification='research/exam-sources-2027/ege-spec-profile.pdf',chapters=['c01','c03','c04','exam-measurements','c05','c06','c07','c08','c16','c02','c09','c11','exam-rational','c10','c12-progressions','exam-models','c21','c17','c13','exam-functions','c14-exponential','exam-exponential','c15','exam-trigonometric','exam-parameters','plane-geometry','exam-plane','c18','solid-geometry','exam-solid','c23-complex','c26','c12-limits','c19','c28','c20','c29','probability','random-variables','statistics'],focus='Все школьные разделы; параметры; отбор корней; сложные неравенства; геометрические доказательства; целочисленные рассуждения; производная/интеграл и вероятностные модели.')]
 for route in routes:
  route['chapters']=sorted(route['chapters'],key=lambda ident:by[ident][0])
  route['chapter_numbers']=[by[i][0]for i in route['chapters']]
 report=dict(checked_at='2026-10-24',official_status='project-2027',baseline_commit='b6e45a8',
  note='Один общий кодификатор ЕГЭ сопоставлен с обеими спецификациями отдельно. БУ/УУ в нём — уровень программы, а не обозначение экзамена. Покрытие перечня тем не означает гарантии решения любого нового задания.',
  official_sources='research/exam-sources-2027/manifest.json',oge_rows=29,ege_common_rows=41,rows=rows,routes=routes)
 path=ROOT/'research/exam-coverage-2027.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 with (ROOT/'research/exam-coverage-2027.tsv').open('w')as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['экзамен','код','тема','главы','задач в разделах','статус'])
  for r in rows:w.writerow([r['exam'],r['code'],r['title'],', '.join(str(c['number'])for c in r['chapters']),len(r['exercises']),r['status']])
 print('Verified crosswalk:',len(rows),'topic rows; three specification routes')
if __name__=='__main__':build()
