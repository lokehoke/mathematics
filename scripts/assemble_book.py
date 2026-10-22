from pathlib import Path
import re,json,math,struct
ROOT=Path(__file__).resolve().parents[1];BOOK=ROOT/'sources/book';TMP=BOOK/'data'
base=(TMP/'edition2-base.tex').read_text()
english=json.loads((TMP/'english.json').read_text())
def eng(s):
 return re.sub(r'\\term\{([^{}]+)\}',lambda m:r'\term{'+m[1]+'}'+(r' (\emph{'+english[m[1]]+'})' if m[1] in english else ''),s)
# Split existing chapters and preserve all original exercises/answers.
before,answer_text=base.split(r'\clearpage\section*{Ответы и краткие решения}',1)
parts=re.split(r'\\section\{([^}]*)\}',before)
chapters=[]
answer_groups=re.split(r'\\subsection\*\{\d+\. [^\n]+\}',answer_text)[1:]
for idx in range(1,15):
 title=parts[2*idx-1];body=parts[2*idx]
 theory,ex=body.split(r'\subsection*{Задачи}',1)
 theory=theory.replace(r'\subsection*{Краткая справка}','')
 theory=re.sub(r'\\Needspace\{[^}]+\}','',theory)
 theory=theory.split(r'\subsubsection*{Связь со следующими темами}')[0]
 qs=[]
 for line in ex.splitlines():
  if '\\item' not in line:continue
  m=re.search(r'\\item(?:\[.*?\])? (.*)',line)
  if m:qs.append({'q':m[1],'advanced':'\\starmark' in line})
 ans=[]
 for line in answer_groups[idx-1].splitlines():
  m=re.match(r'\\item(?:\[.*?\])? (.*)',line)
  if m:ans.append(m[1])
 assert len(qs)==len(ans),(idx,len(qs),len(ans))
 for q,a in zip(qs,ans):q['a']=a
 chapters.append({'old':idx,'title':title,'theory':eng(theory.strip()),'tasks':qs})
assert sum(len(c['tasks']) for c in chapters)==269
# Integrate new content written and cross-reviewed by agents.
f=json.loads((TMP/'add-foundation.json').read_text());alg=json.loads((TMP/'additions-algebra.json').read_text());fun=json.loads((TMP/'extension-functions.json').read_text())
for c in chapters:
 key=str(c['old']);c['tasks']+=f.get(key,[])
 if key in alg:
  v=alg[key];c['tasks']+=v['tasks'];c['theory']+='\n'+v.get('theory','')
 if key in fun:
  v=fun[key];c['tasks']+=v['tasks'];c['theory']+='\n'+v['theory']
# Replace introductory number definitions with Peano axioms, retaining integers and rational arithmetic.
c=chapters[0];cut=c['theory'].rfind(r'\begin{definition}',0,c['theory'].index(r'\term{Целые числа}'))
c['theory']=(TMP/'peano.tex').read_text()+'\n'+c['theory'][cut:]
chapters[6]['theory']+='\n'+(TMP/'roots-n.tex').read_text()
chapters[9]['theory']+='\n'+(TMP/'polynomial-equations.tex').read_text()
comb=json.loads((TMP/'combinatorics.json').read_text());comb['old']=None
prog=json.loads((TMP/'sequences-progressions.json').read_text());prog['old']=None
prog['tasks'][17]['a']=r'Положим \(b_n=a_n+1\). Тогда '+prog['tasks'][17]['a']
# The two elementary counting rules also get complete proofs.
t=comb['theory'];ends=list(re.finditer(r'\\end\{theorem\}',t))
if len(ends)>=2:
 for loc,proof in reversed([(ends[0].end(),r'\begin{proof}Перечислим сначала \(m\) результатов первой группы, затем \(n\) результатов второй. Группы не пересекаются, поэтому все перечисленные результаты различны и их ровно \(m+n\).\end{proof}'),(ends[1].end(),r'\begin{proof}Для каждого результата первого шага имеется \(n_2\) продолжений. Получаются \(n_1\) непересекающихся групп по \(n_2\) исходов, всего \(n_1n_2\). Для большего числа шагов повторяем рассуждение, то есть применяем индукцию по числу шагов.\end{proof}')]):t=t[:loc]+'\n'+proof+t[loc:]
comb['theory']=t
comb['tasks'][19]['q']+=r' Рассматривай целое \(r\in\mathbb N_0\).'

# Add elementary proofs to the two inherited number-theory theorems.
th=chapters[1]['theory']
proofs=[r'\begin{proof}Существование докажем индукцией по числу: простое число уже разложено; составное имеет вид \(ab\), где \(1<a,b<n\), и к обоим множителям применяется предположение индукции. Для единственности используем следующий факт: если простое \(p\) делит \(ab\), то оно делит \(a\) или \(b\). Если \(p\nmid a\), то \(\gcd(p,a)=1\); обратная подстановка в алгоритме Евклида даёт целые \(u,v\) с \(up+va=1\). Умножение на \(b\) показывает, что \(p\mid b\). Теперь первый простой множитель одного разложения обязан совпасть с одним из множителей другого; сократим его и повторим. Все множители совпадут с точностью до порядка.\end{proof}',r'\begin{proof}Для каждого простого множителя обозначим его показатели в \(a,b\) через \(\alpha,\beta\), допуская показатель \(0\). В НОД его показатель \(\min(\alpha,\beta)\), в НОК — \(\max(\alpha,\beta)\). Их сумма равна \(\alpha+\beta\), то есть показателю того же простого в \(ab\). По единственности разложения произведения равны.\end{proof}']
locs=list(re.finditer(r'\\end\{theorem\}',th))
for loc,proof in reversed(list(zip(locs,proofs))):th=th[:loc.end()]+'\n'+proof+th[loc.end():]
chapters[1]['theory']=th

ordered=chapters[:9]+[comb,chapters[9],prog]+chapters[10:]
# Useful diagrams stay attached to the corresponding existing exercises.
old_diagrams={(7,14):'diagram-ladder.pdf',(9,15):'diagram-square.pdf',(13,18):'diagram-wheel.pdf',(14,16):'diagram-venn.pdf',(4,18):'cats-mixtures.png'}
for c in ordered:
 for j,task in enumerate(c['tasks'],1):
  if (c['old'],j) in old_diagrams:task['figure']=old_diagrams[c['old'],j]
# Rename and normalize existing references after the two inserted chapters.
old_to_new={c['old']:i for i,c in enumerate(ordered,1) if c['old']}
for c in ordered:
 c['theory']=re.sub(r'(глав[аеуы]\s+)(\d+)\b',lambda m:m[1]+str(old_to_new.get(int(m[2]),int(m[2]))),c['theory'])
 # Replace the old unnumbered Pythagoras section by a theorem and proof.
 c['theory']=re.sub(r'\\subsubsection\*\{Теорема Пифагора\}.*?(?=\\sub(?:sub)?section|\Z)',lambda _:r'''\subsubsection*{Теорема Пифагора}
\begin{theorem}[Пифагор; Pythagorean theorem]
В прямоугольном треугольнике с катетами \(a,b\) и гипотенузой \(c\) выполнено \(a^2+b^2=c^2\).
\end{theorem}
\begin{proof}Расположим четыре таких треугольника внутри квадрата со стороной \(a+b\) так, чтобы их гипотенузы ограничивали внутренний квадрат со стороной \(c\). Сравнение площадей даёт \((a+b)^2=4\frac{ab}{2}+c^2\). После раскрытия скобок получаем требуемое равенство.\end{proof}
''',c['theory'],flags=re.S)
 c['theory']=c['theory'].replace(r'\subsubsection*',r'\section*')
 c['theory']=re.sub(r'\\\((.*?)\\\)',lambda m:('\n'+r'\['+m[1]+r'\]'+'\n') if len(m[1])>100 and (r'\sum' in m[1] or r'\prod' in m[1]) else m[0],c['theory'],flags=re.S)
# All exercise instructions are embedded in their statements, with no repeated hints.
assert len(ordered)==16
count=sum(len(c['tasks']) for c in ordered)
assert count==385,count
for c in ordered:
 for task in c['tasks']:assert task.get('q') and task.get('a')
(BOOK/'book-data.json').write_text(json.dumps(ordered,ensure_ascii=False,indent=2)+'\n')
# Artwork wraps real paragraphs inside a short unbreakable block. This avoids
# wrapfig's documented incompatibility with list environments and keeps a cat
# together with the text it accompanies. Exercise numbering is explicit.
flow=json.loads((BOOK/'cats-flow.json').read_text()) if (BOOK/'cats-flow.json').exists() else []
used_art=[]
def catblock(body,entry):
 used_art.append(entry['art'])
 side=entry.get('side','r');width=entry.get('width',54)
 image_path=BOOK/'images/unique'/f"art-{entry['art']:02d}.png"
 iw,ih=struct.unpack('>II',image_path.read_bytes()[16:24])
 height=min(width*ih/iw,58)
 wrap_lines=math.ceil(height*72/25.4/(14.5*1.12))+2
 return (r'\par\addvspace{5pt}\begin{lrbox}{\CatFlowBox}\begin{minipage}[t]{\linewidth}'+'\n'
  +r'\setlength{\parskip}{'+str(entry.get('parskip',5))+r'pt}\setlength{\columnsep}{4.5mm}\setlength{\intextsep}{0pt}'+'\n'
  +r'\begin{wrapfigure}['+str(wrap_lines)+']{'+side+'}{'+str(width)+r'mm}'+'\n'
  +r'\includegraphics[width='+str(width)+r'mm,height=58mm,keepaspectratio]{images/unique/art-'+f"{entry['art']:02d}"+r'.png}'+'\n'
  +r'\end{wrapfigure}'+'\n'+body+'\n'+r'\par\WFclear\end{minipage}\end{lrbox}%'+'\n'
  +r'\ifdim\dimexpr\ht\CatFlowBox+\dp\CatFlowBox\relax<64mm\dp\CatFlowBox=\dimexpr64mm-\ht\CatFlowBox\relax\fi%'+'\n'
  +r'\noindent\usebox{\CatFlowBox}\par\addvspace{5pt}'+'\n')
def theory_cats(theory,chapter):
 # Process original proof indices simultaneously, so inserted wrappers cannot
 # change which proof another entry refers to.
 entries=[v for v in flow if v['kind']=='proof' and v['chapter']==chapter]
 ordinal=0
 def proof(m):
  nonlocal ordinal
  ordinal+=1
  entry=next((v for v in entries if v['index']==ordinal),None)
  if not entry:return m[0]
  body=r'\textit{Доказательство.} '+m[1].strip()+r'\hfill\(\square\)'
  if entry.get('include_after'):return catblock(body+'\n\n'+m[2].strip(),entry)
  return catblock(body,entry)+m[2]
 theory=re.sub(r'\\begin\{proof\}(.*?)\\end\{proof\}((?:(?!\\begin\{|\\(?:sub)?section).)*)',proof,theory,flags=re.S)
 for entry in [v for v in flow if v['kind']=='prose' and v['chapter']==chapter]:
  a=theory.index(entry['start']);b=theory.index(entry['end'],a)
  theory=theory[:a]+catblock(theory[a:b].strip(),entry)+theory[b:]
 return theory
def task_paragraph(chapter,j,t,answers=False):
 mark=r'\starmark{}' if t.get('advanced') else ''
 text=t['a'].replace('как в задаче 9','как в задаче 16.9') if answers else t['q'].replace(r'\frac',r'\dfrac')
 body=r'\textbf{'+f'{chapter}.{j}.'+'}'+mark+' '+text
 if not answers and t.get('figure'):
  body+=r'\begin{center}\includegraphics[width=.7\linewidth,height=45mm,keepaspectratio]{images/'+t['figure']+r'}\end{center}'
 return body+r'\par'
def task_section(chapter,tasks,answers=False):
 kind='answers' if answers else 'tasks'
 entries={v['start']:v for v in flow if v['kind']==kind and v['chapter']==chapter}
 spacing=1 if chapter==5 else 3
 result=[r'\begingroup\setlength{\parskip}{'+str(spacing)+r'pt}' if not answers else r'\begingroup\setlength{\parskip}{4pt}'];j=1
 while j<=len(tasks):
  if j in entries:
   entry=entries[j];end=entry['end']
   assert end<=len(tasks)
   if not answers:assert not any(t.get('figure') for t in tasks[j-1:end])
   result.append(catblock('\n\n'.join(task_paragraph(chapter,k,tasks[k-1],answers) for k in range(j,end+1)),entry))
   j=end+1
  else:
   body=task_paragraph(chapter,j,tasks[j-1],answers)
   result.append(body if answers else r'\noindent\begin{minipage}[t]{\linewidth}'+body+r'\end{minipage}\par')
   j+=1
 return result+[r'\endgroup']

header=r'''\documentclass[12pt,a4paper,oneside,openany]{book}
\usepackage{fontspec}
\setmainfont{NotoSerif}[Path=fonts/,Extension=.ttf,UprightFont=*-Regular,BoldFont=*-Bold,ItalicFont=*-Italic,BoldItalicFont=*-BoldItalic]
\usepackage[russian]{babel}
\usepackage{amsmath,amssymb,amsthm,unicode-math}
\setmathfont[Scale=1.05]{latinmodern-math.otf}
\usepackage[left=24mm,right=24mm,top=24mm,bottom=24mm,headheight=16pt]{geometry}
\usepackage{enumitem,needspace,microtype,graphicx,longtable,wrapfig}
\usepackage[table]{xcolor}
\usepackage[normalem]{ulem}
\usepackage{titlesec,fancyhdr,tikz}
\usepackage[breakable,skins]{tcolorbox}
\usepackage[unicode,hidelinks]{hyperref}
\definecolor{Navy}{HTML}{233F4A}
\definecolor{Teal}{HTML}{5A7B77}
\definecolor{Coral}{HTML}{AE7046}
\definecolor{Tint}{HTML}{F1F2E7}
\definecolor{Warm}{HTML}{FBF0DB}
\definecolor{Paper}{HTML}{FFFCF6}
\definecolor{Ink}{HTML}{292B29}
\titleformat{\chapter}[display]{\color{Navy}\bfseries\raggedright\hyphenpenalty=10000\exhyphenpenalty=10000}{\large ГЛАВА \thechapter}{10pt}{\Huge}
\titlespacing*{\chapter}{0pt}{0pt}{24pt}
\titleformat{\section}{\Large\bfseries\color{Navy}\raggedright\hyphenpenalty=10000}{}{0pt}{}
\titleformat{\subsection}{\large\bfseries\color{Teal}\raggedright\hyphenpenalty=10000}{}{0pt}{}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}
\setlength{\emergencystretch}{3em}\linespread{1.12}\sloppy
\everymath{\textstyle}
\widowpenalty=10000\clubpenalty=10000\displaywidowpenalty=10000\raggedbottom
\newtheoremstyle{colordef}{8pt}{8pt}{\normalfont}{}{\color{Teal}\bfseries}{.}{.5em}{}
\theoremstyle{colordef}\newtheorem{definition}{Определение}[chapter]
\theoremstyle{plain}\newtheorem{theorem}{Теорема}[chapter]
\newtheorem{lemma}[theorem]{Лемма}
\theoremstyle{definition}\newtheorem{axiom}{Аксиома}[chapter]
\newtheorem*{example}{Пример}
\tcolorboxenvironment{definition}{enhanced,colback=Tint,colframe=Teal,boxrule=.3pt,arc=1mm,left=2mm,right=2mm,top=1mm,bottom=1mm}
\tcolorboxenvironment{theorem}{enhanced,breakable,colback=Warm,colframe=Coral,boxrule=.3pt,arc=1mm,left=2mm,right=2mm,top=1mm,bottom=1mm}
\AtBeginDocument{\renewcommand{\setminus}{\smallsetminus}}
\newcommand{\term}[1]{{\color{Navy}\uline{#1}}}
\newcommand{\starmark}{\ensuremath{\textcolor{Coral}{{}^{\ast}}}}
\newsavebox{\CatFlowBox}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small\color{Navy}Алгебра для Насти}\fancyhead[R]{\small\color{Teal}\rightmark}\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{.3pt}

\begin{document}
\pagecolor{Paper}\color{Ink}
\hypersetup{pageanchor=false}
\begin{titlepage}\thispagestyle{empty}
\begin{tikzpicture}[remember picture,overlay]
\node[inner sep=0] at (current page.center){\includegraphics[width=\paperwidth,height=\paperheight]{images/cover-cats.png}};
\node[anchor=north,text width=.86\paperwidth,align=center,text=Navy] at ([yshift=-23mm]current page.north){\fontsize{29}{36}\selectfont\bfseries Алгебра перед\\математическим\\анализом\\[7mm]{\fontsize{25}{30}\selectfont для Насти}};
\node[anchor=north,text width=.8\paperwidth,align=center,text=Navy] at ([yshift=-93mm]current page.north){\large От аксиом Пеано до функций и доказательств};
\end{tikzpicture}\null\end{titlepage}

\frontmatter
\hypersetup{pageanchor=true}
\markright{}\chapter*{Как читать эту книгу}
\addcontentsline{toc}{chapter}{Как читать эту книгу}
Эта книга начинается с устройства натуральных чисел и постепенно переходит к алгебре, комбинаторике, последовательностям и функциям. Здесь 16 глав и 385 задач с ответами. Определения сопровождаются английскими терминами, теоремы — доказательствами. Звёздочка \starmark{} отмечает повышенную сложность.

Сначала прочитай определения и примеры, затем попробуй решить задачи самостоятельно. Дроби сокращай до несократимого вида; в уравнениях находи все допустимые корни. В заданиях на доказательство нескольких численных проверок недостаточно. Ответы в конце помогут проверить вычисления и ход рассуждения.

Изображения в теории показывают точные графики; художественные иллюстрации не заменяют математические условия. В рисунках к задачам длины и масштабы задаются подписями.
\begingroup\small\linespread{1}\selectfont\setlength{\parskip}{0pt}\tableofcontents\endgroup
\markright{Обозначения}\input{symbols.tex}
\mainmatter
'''
intro_entry=next((v for v in flow if v['kind']=='intro'),None)
if intro_entry:
 a=header.index('Эта книга начинается');b=header.index(r'\begingroup\small',a)
 header=header[:a]+catblock(header[a:b].strip(),intro_entry)+header[b:]
(BOOK/'main.tex').write_text(header)
main=[]
for i,c in enumerate(ordered,1):
 atlas_intro=''
 theory=c['theory']
 if i==14 and r'График \(\sinh x\)' in theory:
  theory,atlas_intro=theory.split(r'График \(\sinh x\)',1)
  atlas_intro=r'График \(\sinh x\)'+atlas_intro
 theory=theory_cats(theory,i)
 out=[r'\chapter{'+c['title']+'}'+r'\markright{Глава '+str(i)+'}',theory]
 atlas={7:('atlas-roots.pdf','Корни нечётной и чётной степени'),13:('atlas-algebra.pdf','Базовые алгебраические функции'),14:('atlas-exponential.pdf','Показательные, логарифмические и гиперболические функции'),15:('atlas-trigonometry.pdf','Тригонометрические и обратные функции')}
 if i in atlas:
  path,cap=atlas[i]
  if i==7:out.append(r'\Needspace{.4\textheight}\section*{Графики}')
  else:out.append(r'\clearpage\section*{Графики}')
  if atlas_intro:out.append(atlas_intro)
  h='.65' if atlas_intro else '.79'
  out.append(r'\begin{center}\includegraphics[width=\textwidth,height='+h+r'\textheight,keepaspectratio]{images/'+path+'}'+r'\par\small '+cap+r'\end{center}')
 out += [r'\Needspace{7\baselineskip}\section*{Задачи}']
 out += task_section(i,c['tasks'])
 path=f'chapters/chapter-{i:02d}.tex';(BOOK/path).write_text('\n'.join(out)+'\n');main.append(r'\input{'+path+'}')
main += [r'\backmatter\markright{Ответы}\chapter*{Ответы и краткие решения}\addcontentsline{toc}{chapter}{Ответы и краткие решения}']
for i,c in enumerate(ordered,1):
 main += [r'\section*{Глава '+str(i)+'. '+c['title']+'}']
 main += task_section(i,c['tasks'],answers=True)
main += [r'\end{document}']
with (BOOK/'main.tex').open('a') as f:f.write('\n'.join(main)+'\n')
assert len(used_art)==len(set(used_art))==len(flow),(len(used_art),len(flow))
print('Assembled',len(ordered),'chapters;',count,'tasks')
