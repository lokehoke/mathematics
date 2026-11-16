"""Integrate isolated, independently reviewed additions without renumbering IDs."""
import json,re

def integrate(by,data):
 for name in ['review-ege-targeted.json','review-ege-parameters-final.json']:
  for ident,extra in json.loads((data/name).read_text()).items():
   by[ident]['theory']+='\n'+extra['theory']
   for t in extra['tasks']:
    t['advanced']=t.pop('hard',t.get('advanced',False))
    by[ident]['tasks'].append(t)
 ml=by['ml-foundations']
 heading=r'\section{Градиентный спуск: точный разбор квадратичной модели}'
 assert ml['theory'].count(heading)==1
 ml['theory']=ml['theory'].replace(heading,heading+'\n'+(data/'review-convexity.tex').read_text())
 matrix=json.loads((data/'review-ml-matrix.json').read_text())
 anchor=matrix['metadata']['integration']['insert_theory_before']
 assert ml['theory'].count(anchor)==1
 ml['theory']=ml['theory'].replace(anchor,matrix['theory']+'\n'+anchor)
 ml['tasks']+=matrix['tasks']
 # Typography only: all fractions in a mathematical exercise use stacked TeX.
 for t in ml['tasks']:
  for k in ['q','a']:t[k]=t[k].replace('(10-3)/1',r'\frac{10-3}{1}')
 for ident,fix in matrix['clarifications'].items():
  source=by[ident]['theory']
  marker=r'\begin{theorem}['+fix['insert_before_theorem']+']'
  assert source.count(marker)==1,(ident,marker)
  at=source.index(marker);a=source.index(r'\begin{proof}',at)
  b=source.index(r'\end{proof}',a)+len(r'\end{proof}')
  source=source[:a]+fix['replacement_proof']+source[b:]
  text=fix['theory']
  if ident=='random-variables':
   a=text.index('Пусть');b=text.index('Конечные первые')
   text=(text[:a]+r'\begin{theorem}[Расширение Тонелли--Фубини для плотностей]'
     +r'\label{thm:probability-fubini-extension}'+'\n'+text[a:b]
     +r'\end{theorem}'+'\n'+text[b:])
  else:
   # Definitions and general results follow the same numbered style as the book.
   a=text.index(r'\underline{Свёрткой плотностей}')
   b=text.index('Для независимых')
   definition=text[a:b].replace(r'\underline{Свёрткой плотностей} (convolution of densities)',
      r'\term{Свёртка плотностей} (\emph{convolution of densities})')
   definition=definition.replace('называют функцию','--- функция').replace('задаваемую','задаваемая')
   text=text[:a]+r'\begin{definition}'+definition+r'\end{definition}'+'\n'+text[b:]
   a=text.index('Пусть независимые');b=text.index('Обозначим',a)
   stop=text.index('Если дисперсия одной')
   theorem=(r'\begin{theorem}[Сумма независимых нормальных величин]'
    +r'\label{thm:normal-convolution}'+'\n'+text[a:b]
    +r'Тогда \(X+Y\sim\operatorname N(\mu_1+\mu_2,a+b)\).'
    +r'\end{theorem}\begin{proof}'+'\n'+text[b:stop].rstrip()+r'\qedhere\end{proof}'+'\n')
   text=text[:a]+theorem+text[stop:]
   source=source.replace(marker,marker+'\n'+r'Предполагаются \(n\ge1\), \(0<\alpha<1\), \(\sigma>0\).',1)
  by[ident]['theory']=source[:at]+text+'\n'+source[at:]
