"""Verify archive provenance, integration and preservation for the olympiad edition."""
from pathlib import Path
from collections import Counter
import json,re,hashlib,subprocess
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2];BOOK=ROOT/'book/source'
selected=json.loads((BOOK/'data/olympiad-selected.json').read_text())
sources=json.loads((ROOT/'book/references/olympiad-book-sources.json').read_text())
chapters=json.loads((BOOK/'book-data.json').read_text())
all_tasks={t['uid']:(i,j,t)for i,c in enumerate(chapters,1)for j,t in enumerate(c['tasks'],1)}
assert len(selected)==64 and len({t['uid']for t in selected})==64
counts=Counter(t['chapter']for t in selected)
assert len(counts)==30 and all(v in (2,3)for v in counts.values())
for key,s in sources.items():
 assert s['source_url'].startswith(('https://','http://'))
 assert hashlib.sha256((ROOT/s['path']).read_bytes()).hexdigest()==s['sha256'],key
for t in selected:
 i,j,out=all_tasks[t['uid']];meta=t['olympiad'];s=sources[meta['source_id']]
 assert t['q']==out['q'] and t['answer']in out['a'] and t['solution']in out['a'],t['uid']
 assert r'\textbf{Ответ.}'in out['a']and r'\textit{Решение.}'in out['a'] and out['a'].endswith(r'\(\blacksquare\)')
 assert meta['source_pages']and all(1<=p<=len(PdfReader(ROOT/s['path']).pages)for p in meta['source_pages'])
 assert re.search(r'\b(?:19|20)\d{2}\b',meta['label']) and ('№'in meta['label']or re.search(r'\b[A-B][1-6]\b',meta['label'])),t['uid']
 tex=(BOOK/f'chapters/chapter-{i:02d}.tex').read_text()
 assert meta['label']in tex and r'\href{'+out['olympiad']['url']+'}'in tex
 assert not any('/'in m for k in ['q','answer','solution']for m in re.findall(r'\\\(.*?\\\)|\\\[.*?\\\]',t[k],re.S))
provenance=json.loads((ROOT/'book/references/review-olympiad-provenance.json').read_text())
verified={t['uid']:t for t in provenance['items']}
assert len(verified)==64
for t in selected:
 assert t['olympiad']['source_pages']==verified[t['uid']]['verified_source_pages'],t['uid']
old=json.loads(subprocess.check_output(['git','show','df02549:sources/book/book-data.json'],cwd=ROOT))
old_tasks={t['uid']:t for c in old for t in c['tasks']}
assert len(old_tasks)==1432 and len(all_tasks)==1496
for uid,prev in old_tasks.items():
 assert uid in all_tasks and all(prev[k]==all_tasks[uid][2][k]for k in ['q','a']),uid
report=dict(selected_tasks=64,chapters=30,per_chapter=dict(counts),verified_primary_documents=len(sources),all_original_hashes_verified=True,all_tasks_have_source_label_and_link=True,all_tasks_have_answer_and_solution=True,legacy_tasks_preserved=1432,total_tasks=1496,payload_sha256=hashlib.sha256((BOOK/'data/olympiad-selected.json').read_bytes()).hexdigest(),index=[dict(uid=t['uid'],published=f'{all_tasks[t["uid"]][0]}.{all_tasks[t["uid"]][1]}',**t['olympiad'],source_url=sources[t['olympiad']['source_id']]['source_url'])for t in selected])
p=ROOT/'book/references/olympiad-book-integration.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Verified: 64 attributed tasks / 30 chapters / 20 source PDFs; all 1432 older exercises unchanged.')
