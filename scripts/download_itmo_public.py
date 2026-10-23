#!/usr/bin/env python3
"""Collect only anonymous public mathematics archive branches on olymp.itmo.ru.

Uses the same GET endpoints as the public website. It does not register, submit
answers, access participant results or try to open protected problem sets.
"""
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime,timezone
import hashlib,json,re,time
import requests

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'olympiads/russia/itmo'
BASE='https://olymp.itmo.ru'
UA='MathematicsArchive/1.0 (public educational contest archive)'

def main():
 FOLDER.mkdir(parents=True,exist_ok=True)
 for name in ['indexes','documents']:(FOLDER/name).mkdir(exist_ok=True)
 mf=FOLDER/'manifest.json'
 old=json.loads(mf.read_text()) if mf.exists() else {}
 docs={r['url']:r for r in old.get('documents',[])}
 indexes={r['url']:r for r in old.get('indexes',[])}
 failures=[];visited=set()
 def checkpoint():
  out={**old,'id':'itmo','contest':'Открытая олимпиада ИТМО — математика',
   'updated_at':datetime.now(timezone.utc).isoformat(),
   'coverage_status':'public mathematics project archive branches processed; other historical sources may remain',
   'documents':list(docs.values()),'indexes':list(indexes.values()),
   'public_api_failures':failures,'public_api_sections_visited':len(visited),
   'pending_documents':[r for r in docs.values() if r.get('status')!='downloaded']}
  temp=mf.with_suffix('.json.tmp');temp.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');temp.replace(mf)
 def get_json(url):
  previous=indexes.get(url,{})
  if previous.get('local_path'):
   p=ROOT/previous['local_path']
   if p.is_file() and p.suffix=='.json' and hashlib.sha256(p.read_bytes()).hexdigest()==previous.get('sha256'):
    return json.loads(p.read_bytes())
  try:
   r=requests.get(url,headers={'User-Agent':UA},timeout=(6,15));r.raise_for_status()
   value=r.json()
   raw=r.content;p=FOLDER/'indexes'/(hashlib.sha256(url.encode()).hexdigest()[:16]+'.json');p.write_bytes(raw)
   indexes[url]=dict(url=url,local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),status='downloaded',role='public_archive_api_index',bytes=len(raw))
   return value
  except Exception as e:
   failures.append(dict(url=url,error=str(e),status=getattr(getattr(e,'response',None),'status_code',None)))
   return None
 def save_file(project,section,api,year):
  f=section.get('file') or {}
  if not f.get('src'):return
  url=urljoin(BASE,f['src']);previous=docs.get(url,{})
  if previous.get('status')=='downloaded':
   p=ROOT/previous.get('local_path','NO_FILE')
   if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==previous.get('sha256'):return
  name=f.get('name','');label=section.get('name','')
  solution=bool(re.search(r'решени|ответ|разбор|solution|answer',name+' '+label,re.I))
  kind='tasks_and_solutions' if solution else 'tasks'
  rec=dict(url=url,contest='Открытая олимпиада ИТМО — математика',subject='mathematics',
   source_page=f"{BASE}/p/{project}/{section['id']}",source_api=api,
   year=year,stage=None,classes=None,label=label,material_title=name,
   document_type=kind,status='pending',retrieved_at=datetime.now(timezone.utc).isoformat())
  try:
   r=requests.get(url,headers={'User-Agent':UA},timeout=(6,30));r.raise_for_status()
   b=r.content
   if len(b)>60*1024*1024:raise ValueError('file exceeds 60 MiB')
   if b.lstrip().startswith(b'%PDF-'):ext='.pdf'
   elif b.startswith(b'PK'):ext='.zip'
   else:raise ValueError('published archive attachment is not a PDF/ZIP; retained as an unresolved record')
   p=FOLDER/'documents'/(hashlib.sha256(url.encode()).hexdigest()[:16]+ext);p.write_bytes(b)
   rec.update(status='downloaded',local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),content_type=r.headers.get('Content-Type'),classification_evidence='Public mathematical archive branch; solution title keyword' if solution else 'Public mathematical archive branch')
   print('SAVED',year,label,name,len(b),flush=True)
  except Exception as e:rec.update(status='failed',error=str(e))
  docs[url]=rec;checkpoint()
 def walk(project,node,in_archive=False,year=None):
  sid=node.get('id')
  if sid is None or (project,sid) in visited:return
  if len(visited)>=500:raise RuntimeError('Explicit public section limit reached')
  name=node.get('name','')
  if not in_archive and not node.get('isRoot') and not re.search(r'архив.*зада|archive',name,re.I):return
  visited.add((project,sid))
  api=f'{BASE}/api/section/{project}/{sid}';s=get_json(api)
  if not isinstance(s,dict):return
  if s.get('isAllowed') is False or s.get('securityCode'):
   failures.append(dict(url=api,error='Protected section: no access attempted'))
   return
  in_archive=in_archive or bool(re.search(r'архив.*зада|archive',name,re.I))
  ym=re.search(r'(20\d\d)\s*[-/–]\s*(20\d\d)',s.get('name',''))
  if ym:year=ym[1]+'/'+ym[2]
  if in_archive:
   save_file(project,s,api,year)
  for child in s.get('sections',[]):walk(project,child,in_archive,year)
  checkpoint()
 projects=get_json(BASE+'/api/public-projects?languageCode=ru')
 if not isinstance(projects,list):checkpoint();return
 for p in projects:
  if not ('математ' in p.get('name','').lower() or (p.get('urlSlug') or '').startswith('math')):continue
  slug=p.get('urlSlug') or str(p['id'])
  d=get_json(BASE+'/api/project/'+slug)
  if not isinstance(d,dict):continue
  print('PROJECT',slug,d['name'],flush=True)
  for root in d.get('projectSections',[]):walk(slug,root)
 checkpoint()
 print('COMPLETE',len(docs),'file records;',len(failures),'public API failures',flush=True)

if __name__=='__main__':main()
