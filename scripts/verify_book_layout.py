"""Check cats against the original TeX PDF (before optional downsampling).

Raster page previews are still reviewed by a person/agent. This complements that
review with checks for missing/repeated art, objects outside the content area,
text/art intersections and missing exercise labels.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,re,sys
import pdfplumber
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT/'sources/book'
source=Path(sys.argv[1]) if len(sys.argv)>1 else BOOK/'main.pdf'
output=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'research/book-flow-layout-check.json'
lookup={hashlib.sha256(Image.open(p).convert('RGB').tobytes()).hexdigest():int(p.stem.removeprefix('art-')) for p in (BOOK/'images/unique').glob('art-*.png')}
expected_art={entry['art'] for entry in json.loads((BOOK/'cats-flow.json').read_text())}
placements=[];overlaps=[];box_overlaps=[];outside=[];sparse=[];labels=Counter()
with pdfplumber.open(source) as pdf:
 page_count=len(pdf.pages)
 for no,page in enumerate(pdf.pages,1):
  text=page.extract_text() or ''
  # Font-aware matching separates 12 pt exercise labels from numbered
  # section headings, and tolerates a following digit joined by extraction.
  words=page.extract_words(extra_attrs=['fontname','size'])
  for wi,word in enumerate(words):
   if abs(word['size']-12)>.1 or 'Bold' not in word['fontname']:continue
   match=re.match(r'^(\d+\.\d+)\.$',word['text'])
   if match:
    previous=words[wi-1] if wi else {}
    if previous.get('text','') in ('Теорема','Определение','Аксиома','Лемма') and abs(previous['top']-word['top'])<2:continue
    labels[match[1]]+=1
  if no>6 and len(page.chars)<650 and not page.images:
   sparse.append({'page':no,'characters':len(page.chars),'tail':text[-150:]})
  for im in page.images:
   # Other illustrations have a wider box; skip decoding them.
   if im['width']>270 or im['height']>280:continue
   digest=hashlib.sha256(im['stream'].get_data()).hexdigest()
   if digest not in lookup:continue
   art=lookup[digest]
   box={k:round(im[k],3) for k in ['x0','x1','top','bottom']}
   placements.append({'art':art,'physical_page':no,**box})
   if im['x0']<67 or im['x1']>529 or im['top']<65 or im['bottom']>775:
    outside.append({'art':art,'page':no,**box})
   chars=[c for c in page.chars if c['text'].strip() and c['x0']<im['x1']-1 and c['x1']>im['x0']+1 and c['top']<im['bottom']-1 and c['bottom']>im['top']+1]
   if chars:overlaps.append({'art':art,'page':no,'text':''.join(c['text'] for c in chars)})
   # A colored definition/theorem frame could cover a cat even if the words
   # inside the frame happen to miss it, so inspect the filled shapes too.
   for shape in page.rects+page.curves:
    color=shape.get('non_stroking_color')
    palette=[(0.98431,0.9412,0.85883),(0.9451,0.94902,0.90588)]
    if not shape.get('fill') or not isinstance(color,(tuple,list)) or len(color)!=3:continue
    if not any(max(abs(a-b) for a,b in zip(color,c))<.002 for c in palette):continue
    if shape['x0']<im['x1']-1 and shape['x1']>im['x0']+1 and shape['top']<im['bottom']-1 and shape['bottom']>im['top']+1:
     box_overlaps.append({'art':art,'page':no,'box_top':shape['top'],'box_bottom':shape['bottom']})
chapters=json.loads((BOOK/'book-data.json').read_text())
expected={f'{i}.{j}' for i,c in enumerate(chapters,1) for j in range(1,len(c['tasks'])+1)}
wrong_labels={k:labels[k] for k in sorted(expected) if labels[k]!=2}
placements.sort(key=lambda v:(v['physical_page'],v['top']))
result={'pages':page_count,'unique_art':len({p['art'] for p in placements}),'art_occurrences':len(placements),'placements':placements,'text_art_overlaps':overlaps,'colored_box_art_overlaps':box_overlaps,'outside_content':outside,'exercise_label_anomalies':wrong_labels,'sparse_pages_for_visual_review':sparse,'gaps_over_three_pages':[(a['physical_page'],b['physical_page']) for a,b in zip(placements,placements[1:]) if b['physical_page']-a['physical_page']>3]}
output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['placements','sparse_pages_for_visual_review']},ensure_ascii=False))
print('Sparse pages:',[(v['page'],v['characters']) for v in sparse])
if len(placements)!=len(expected_art) or {p['art'] for p in placements}!=expected_art or overlaps or box_overlaps or outside or wrong_labels:sys.exit(1)
