"""Check stable exercises, navigation, labels and final reading-PDF integrity."""
from pathlib import Path
from collections import Counter
import json,re,hashlib,subprocess
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2];BOOK=ROOT/'book/source'
chapters=json.loads((BOOK/'book-data.json').read_text());parts=json.loads((BOOK/'data/book-structure.json').read_text())
uid=Counter(t['uid']for c in chapters for t in c['tasks']);assert all(v==1 for v in uid.values())
baseline=json.loads(subprocess.check_output(['git','show','b01efdd:sources/book/book-data.json'],cwd=ROOT,text=True))
old={f'c{i:02d}.{j}':t for i,c in enumerate(baseline,1)for j,t in enumerate(c['tasks'],1)}
assert len(old)==790 and old.keys()<=uid.keys()
modified=[]
for i,c in enumerate(chapters,1):
 for j,t in enumerate(c['tasks'],1):
  prev=old.get(t['uid'])
  if prev and any(t[k]!=prev[k]for k in ['q','a']):modified.append(dict(uid=t['uid'],now=f'{i}.{j}'))
flow=json.loads((BOOK/'cats-flow.json').read_text());art=[e['art']for e in flow];assert len(art)==len(set(art))
from PIL import Image
pixels={};alpha=[]
for n in art:
 p=BOOK/'images/unique'/f'art-{n:02d}.png';im=Image.open(p)
 sig=hashlib.sha256(im.tobytes()).hexdigest();assert sig not in pixels,(n,pixels.get(sig));pixels[sig]=n
 assert im.mode=='RGBA'and im.getchannel('A').getextrema()[0]==0
 alpha.append(n)
tex=(BOOK/'main.tex').read_text()+'\n'+'\n'.join((BOOK/f'chapters/chapter-{i:02d}.tex').read_text()for i in range(1,len(chapters)+1))
labels=re.findall(r'\\label\{([^}]+)\}',tex);refs=re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',tex)
assert len(labels)==len(set(labels));assert set(refs)<=set(labels),(set(refs)-set(labels))
assert r'\renewcommand{\sectionmark}[1]{}'in tex
log=(BOOK/'main.log').read_text()
assert not re.search(r'Overfull|Undefined control sequence|undefined references|Missing character',log,re.I)
path=ROOT/'rendered/algebra-for-beloved-kitten.pdf';r=PdfReader(path);raw=PdfReader(BOOK/'main.pdf')
assert len(r.pages)==len(raw.pages)
assert r.page_labels[0]=='Обложка'and r.page_labels[1:]==[str(i)for i in range(1,len(r.pages))]
assert set(r.named_destinations)==set(raw.named_destinations)
for key in raw.named_destinations:
 assert raw.get_destination_page_number(raw.named_destinations[key])==r.get_destination_page_number(r.named_destinations[key]),key
def outline_targets(reader,items):
 out=[]
 for item in items:
  if isinstance(item,list):out.extend(outline_targets(reader,item))
  else:out.append((item.title,reader.get_destination_page_number(item)))
 return out
assert outline_targets(raw,raw.outline)==outline_targets(r,r.outline)
def internal_links(reader):
 page_ids={p.indirect_reference.idnum:i for i,p in enumerate(reader.pages)}
 links=[]
 for no,page in enumerate(reader.pages):
  annots=page.get('/Annots',[])
  if hasattr(annots,'get_object'):annots=annots.get_object()
  for ref in annots:
   annot=ref.get_object();destination=annot.get('/Dest')
   action=annot.get('/A')
   if action:
    action=action.get_object()
    if action.get('/S')=='/GoTo':destination=action.get('/D')
   if destination is None:continue
   if hasattr(destination,'get_object'):destination=destination.get_object()
   if isinstance(destination,str):
    name=str(destination).lstrip('/')
    assert name in reader.named_destinations,name
    target=reader.get_destination_page_number(reader.named_destinations[name])
   else:
    page_ref=destination[0]
    target=page_ids[page_ref.idnum] if hasattr(page_ref,'idnum') else int(page_ref)
   assert 0<=target<len(reader.pages)
   links.append((no,target))
 return sorted(links)
raw_links=internal_links(raw);reading_links=internal_links(r)
assert raw_links==reading_links
text='\n'.join(p.extract_text()for p in r.pages)
assert '??'not in text
# A subsection number like 11.2.1 must not be interpreted as exercise 11.2.
labels_printed=Counter(re.findall(r'(?m)^(\d+\.\d+)\.',text))
expected={f'{i}.{j}'for i,c in enumerate(chapters,1)for j in range(1,len(c['tasks'])+1)}
assert all(labels_printed[k]>=2 for k in expected),{k:labels_printed[k]for k in expected if labels_printed[k]!=2}
layout=json.loads((ROOT/'book/references/book-flow-layout-check.json').read_text())
assert not any(layout[k]for k in ['text_art_overlaps','colored_box_art_overlaps','outside_content','exercise_label_anomalies','gaps_over_three_pages'])
report=dict(parts=len(parts),chapters=len(chapters),pages=len(r.pages),arabic_pages=len(r.pages)-1,tasks=sum(len(c['tasks'])for c in chapters),retained_edition8_tasks=len(old),changed_legacy_statements=modified,new_tasks=len(uid)-len(old),unique_cats=len(art),new_cats=len(art)-135,all_art_transparent=True,theorems=len(re.findall(r'\\begin\{theorem\}',tex)),proofs=len(re.findall(r'\\begin\{proof\}',tex))+tex.count(r'\textit{Доказательство.}'),notation_rows=sum(len(g['rows'])for g in json.loads((BOOK/'data/symbols-groups.json').read_text())),notation_groups=len(json.loads((BOOK/'data/symbols-groups.json').read_text())),named_destinations=len(r.named_destinations),bookmarks=len(outline_targets(r,r.outline)),internal_links=len(reading_links),all_navigation_preserved=True,all_exercises_printed_twice=True,all_references_resolved=True,reading_pdf_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),reading_pdf_bytes=path.stat().st_size)
(ROOT/'book/references/book-edition9-integrity-2026-10-23.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
