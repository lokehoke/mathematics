"""Render the grouped notation reference, one expression per bordered row."""
from pathlib import Path
import json
BOOK=Path(__file__).resolve().parents[1]/'sources/book'
groups=json.loads((BOOK/'data/symbols-groups.json').read_text())
out=[r'\chapter*{Справочник обозначений}\markright{Обозначения}',
 r'\addcontentsline{toc}{chapter}{Справочник обозначений}',
 r'\begingroup\small\renewcommand{\arraystretch}{1.35}\setlength{\tabcolsep}{4pt}\arrayrulecolor{Teal}\setlength{\arrayrulewidth}{.35pt}']
for group in groups:
 out += [r'\Needspace{12\baselineskip}\section*{'+group['title']+'}',
  r'\begin{longtable}{|>{\raggedright\arraybackslash}p{.21\textwidth}|>{\raggedright\arraybackslash}p{.27\textwidth}|>{\raggedright\arraybackslash}p{.46\textwidth}|}',
  r'\hline\textbf{Обозначение}&\textbf{Как читать}&\textbf{Значение}\\\hline\endfirsthead',
  r'\hline\textbf{Обозначение}&\textbf{Как читать}&\textbf{Значение}\\\hline\endhead',
  r'\hline\endfoot',r'\hline\endlastfoot']
 for symbol,reading,meaning in group['rows']:
  out.append(r'\tablemath{'+symbol+r'}&'+reading+'&'+meaning+r'\\\hline')
 out.append(r'\end{longtable}')
out.append(r'\endgroup')
(BOOK/'symbols.tex').write_text('\n'.join(out)+'\n')
print('Notation reference:',len(groups),'groups;',sum(len(g['rows']) for g in groups),'rows')
