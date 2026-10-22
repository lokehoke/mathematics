#!/usr/bin/env python3
"""Download public university mathematics contest archives, keeping provenance.
No authentication, paywall workaround, or document conversion is performed.
Run from anywhere: python3 scripts/download_university.py [--only imc,putnam,...].
The manifest is incremental: successful resources are reused after SHA-256 checks.
"""
from __future__ import annotations
import argparse, concurrent.futures, datetime, hashlib, html, json, re, threading, time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlsplit,urlunsplit,unquote,quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'olympiads'/'university'
MANIFEST=BASE/'manifest.jsonl'
UA='MathematicsArchive/1.0 (public mathematics tasks; no authentication)'
LOCK=threading.Lock()
ROWS={}
ASSET=re.compile(r'\.(pdf|tex|zip|docx?|rar|ps|djvu)(?:$|[?#])',re.I)
EXCLUDE=re.compile(r'(result|winner|award|statistic|protocol|протокол|победител|результат|положени|регламент|diplom|diploma|заявк)',re.I)
RELEVANT=re.compile(r'(problem|question|solution|task|prob[_-]|sol[_-]|задан|задач|решени|услови|variant|вариант|answer|marking|resh)',re.I)

def norm(u):
 u=html.unescape(u).replace('§ion=','&section=')
 p=urlsplit(u);return urlunsplit((p.scheme,p.netloc,quote(unquote(p.path),safe='/@:+'),quote(unquote(p.query),safe='=&?/:+,%'),''))

class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.cur=None
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='a' and d.get('href'):self.cur=[d['href'],[]]
 def handle_data(self,d):
  if self.cur:self.cur[1].append(d)
 def handle_endtag(self,t):
  if t=='a' and self.cur:self.links.append((self.cur[0],''.join(self.cur[1]).strip()));self.cur=None

def links(data,url):
 p=Links();p.feed(data.decode('utf-8','replace'))
 return [(norm(urljoin(url,h)),t) for h,t in p.links if not h.startswith(('mailto:','javascript:','#'))]

def year_of(s,fallback=None):
 ys=re.findall(r'(?<!\d)((?:19|20)\d{2})(?!\d)',unquote(s))
 return int(ys[-1]) if ys else fallback

def kind_of(u,label=''):
 s=unquote(u+' '+label).lower()
 sol=bool(re.search(r'(solution|answer|решени|resh|marking|\bsol\b|prob_sol)',s))
 prob=bool(re.search(r'(problem|question|задан|задач|услови|prob_sol)',s))
 if re.search(r'/\d{4}s\.(pdf|tex)$',s):sol=True
 return 'problems_and_solutions' if sol and prob else ('solutions' if sol else 'problems')

def record(row):
 with LOCK:
  ROWS[(row['contest'],row['url'])]=row
  MANIFEST.parent.mkdir(parents=True,exist_ok=True)
  with MANIFEST.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')

def fetch(contest,url,year=None,kind='index',label='',source='official',round_=None):
 url=norm(url);key=(contest,url)
 with LOCK: old=ROWS.get(key)
 if old and old.get('status')=='downloaded' and old.get('path'):
  p=ROOT/old['path']
  if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==old.get('sha256'):return p.read_bytes()
 row=dict(contest=contest,url=url,year=year,type=kind,path=None,status='pending',sha256=None,source_status=source,label=label,round=round_,age_group='university students',retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'))
 try:
  download_url=url
  if 'disk.yandex.' in urlsplit(url).netloc and kind!='index':
   endpoint='https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key='+quote(url,safe='')
   with urlopen(Request(endpoint,headers={'User-Agent':UA}),timeout=25) as rr:
    download_url=json.load(rr)['href']
   row['public_download_api']=endpoint
  req=Request(download_url,headers={'User-Agent':UA,'Accept':'*/*'})
  with urlopen(req,timeout=25) as resp:
   data=resp.read(60*1024*1024+1);row['http_status']=resp.status;row['final_url']=resp.url;row['content_type']=resp.headers.get('Content-Type','')
  if len(data)>60*1024*1024:raise ValueError('resource exceeds 60 MiB safety limit')
  ext=Path(unquote(urlsplit(url).path)).suffix.lower()
  if kind=='index':ext='.html'
  elif data.lstrip().startswith(b'%PDF-'):ext='.pdf'
  if ext=='.pdf' and not data.lstrip()[:1024].startswith(b'%PDF-'):raise ValueError('expected PDF header; received other content')
  if ext=='.zip' and not data.startswith(b'PK'):raise ValueError('expected ZIP header')
  if ext in ('.tex','.ps') and b'<html' in data[:1024].lower():raise ValueError('HTML returned instead of source')
  if ext not in ('.pdf','.zip','.tex','.ps','.doc','.docx','.rar','.djvu','.html'):ext='.html'
  if ext=='.html' and not re.search(br'(?i)<(?:!doctype|html|head|body|h[1-6]|p|table|div|a)\b',data[:10000]):raise ValueError('expected HTML page')
  slug=re.sub(r'[^a-zA-Z0-9._-]+','-',unquote(urlsplit(url).path).strip('/').split('/')[-1] or 'index')[:85]
  slug=re.sub(r'\.[a-zA-Z0-9]+$','',slug) or 'document'
  folder=BASE/contest/(str(year) if year is not None else 'undated')
  folder.mkdir(parents=True,exist_ok=True)
  target=folder/f'{kind}-{slug}-{hashlib.sha256(url.encode()).hexdigest()[:10]}{ext}'
  target.write_bytes(data)
  row.update(path=str(target.relative_to(ROOT)),status='downloaded',sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),validation='pdf_header' if ext=='.pdf' else ('zip_header' if ext=='.zip' else 'file_type'))
  record(row);return data
 except Exception as exc:
  row.update(status='failed',error=f'{type(exc).__name__}: {exc}')
  if isinstance(exc,HTTPError):row['http_status']=exc.code
  record(row);return None

def assets(jobs):
 # De-duplicate by contest and URL, preserving each source independently.
 d={(x[0],norm(x[1])):x for x in jobs}
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for _ in pool.map(lambda x:fetch(*x),d.values()):pass

def imc():
 def annual(y):
  u=f'https://www.imc-math.org.uk/?year={y}&item=problems';data=fetch('imc',u,y,'index',source='official organizer')
  if data is None:return []
  jobs=[]
  for v,label in links(data,u):
   if ASSET.search(v) and 'imc-math.org.uk' in v and not EXCLUDE.search(label+' '+v) and not re.search(r'poster|logo|flyer|sponsor',v+' '+label,re.I):jobs.append(('imc',v,y,kind_of(v,label),label,'official organizer'))
  return jobs
 jobs=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  for found in pool.map(annual,range(1994,2027)):jobs.extend(found)
 assets(jobs)
 print('IMC: discovered',len(jobs),'material links across 1994–2026',flush=True)

def putnam():
 # Exact links are discovered from the organizers' current archive, not guessed.
 u='https://maa.org/maa-putnam-archive/';data=fetch('putnam-maa',u,None,'index',source='official organizer')
 if data:
  assets([('putnam-maa',v,year_of(label+' '+v),kind_of(v,label),label,'official organizer') for v,label in links(data,u) if ASSET.search(v) and not EXCLUDE.search(label+' '+v)])
 # Public author-maintained archive: its copyright/republication notice is preserved in index.
 u='https://kskedlaya.org/putnam-archive/';data=fetch('putnam-author',u,None,'index',source='author-maintained; unofficial; see copyright notice in index')
 if data:
  jobs=[]
  for v,label in links(data,u):
   m=re.search(r'/(19\d\d|20\d\d)(s?)\.(pdf|tex)$',v)
   if m:jobs.append(('putnam-author',v,int(m[1]),'solutions' if m[2] else 'problems',label,'author-maintained; unofficial; see copyright notice in index'))
  assets(jobs)
  print('Putnam author archive: discovered',len(jobs),'PDF/TeX links',flush=True)

def crawl(contest,seeds,prefixes,depth=2,source='official organizer',all_assets=False):
 seen=set();queue=[(u,None,0) for u in seeds];jobs=[]
 while queue:
  batch=[x for x in queue if norm(x[0]) not in seen];queue=[]
  if not batch:break
  def page(x):
   u,y,d=x;return(x,fetch(contest,u,y,'index',source=source))
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
   for (u,y,d),data in pool.map(page,batch):
    seen.add(norm(u))
    if not data:continue
    ll=links(data,u)
    for v,label in ll:
     if ASSET.search(v):
      if contest=='mipt-organizer' and not (re.search(r'/(?:mipt[^/]*|training_by_subject)\.pdf$',v) or 'imc-math.org.uk/' in v):continue
      if not EXCLUDE.search(label+' '+unquote(v)) and (all_assets or RELEVANT.search(label+' '+unquote(v))):
       yy=year_of(label+' '+v,y);jobs.append((contest,v,yy,kind_of(v,label),label,source))
     elif d<depth and any(v.startswith(p) for p in prefixes):
      if not EXCLUDE.search(label+' '+unquote(v)) and (d==0 or re.search(r'(19\d\d|20\d\d|archiv|архив|olymp|олимп|problem|задач|решени)',v+' '+label,re.I)):
       queue.append((v,year_of(v+' '+label,y),d+1))
  if len(seen)>180:break
 assets(jobs)
 print(contest,':',len(seen),'pages,',len(jobs),'material links',flush=True)

SOURCES={
 'shilnikov':(['https://itmm.unn.ru/olympiad-shilnikov/olympiada-archiv/'],['https://itmm.unn.ru/olympiad-shilnikov/'],1),

 'msu-vmk':(['https://cs.msu.ru/students/math_olympiads'],['https://cs.msu.ru/students/math_olympiads'],0),
 'kolmogorov-msu':(['https://mech.math.msu.su/probab/olimpia/olimpia.htm','http://mech.math.msu.su/probab/olimpia/olimpia.htm'],['https://mech.math.msu.su/probab/olimpia/','http://mech.math.msu.su/probab/olimpia/'],2),
 'open-internet':(['https://olymp.i-exam.ru/node/937'],['https://olymp.i-exam.ru/'],0),
 'mipt-organizer':(['http://www.rkarasev.ru/note/all'],['http://www.rkarasev.ru/note/'],1),
 'msu-kazakhstan':(['https://www.msu.kz/kz/science/olimpiady/detail.php?ELEMENT_ID=4854'],['https://www.msu.kz/kz/science/olimpiady/'],0),

 'siberian-nsu':(['https://smc.nsu.ru/','http://smc.nsu.ru/'],['https://smc.nsu.ru/','http://smc.nsu.ru/'],2),

}

def itmo():
 u='https://im.itmo.ru/ru/events/olymp_spb';data=fetch('itmo-spb',u,None,'index',source='official organizer')
 if not data:return
 class Y(HTMLParser):
  def __init__(self):super().__init__();self.year=None;self.cur=None;self.out=[];self.region='spb'
  def handle_data(self,d):
   if 'Северо-Запада' in d:self.region='northwest'
   yy=re.findall(r'(?<!\d)(20\d{2})(?!\d)',d)
   if yy:self.year=int(yy[-1])
   if self.cur:self.cur[1]+=d
  def handle_starttag(self,t,a):
   h=dict(a).get('href','')
   if t=='a':self.cur=[h,'',self.year,self.region]
  def handle_endtag(self,t):
   if t=='a' and self.cur:
    if 'disk.yandex.' in self.cur[0] and self.cur[1].strip()=='PDF':self.out.append(self.cur)
    self.cur=None
 p=Y();p.feed(data.decode('utf-8','replace'))
 jobs=[('itmo-'+reg,v,y,'problems_and_solutions','Published official annual archive '+str(y),'official organizer hosted on public Yandex Disk') for v,label,y,reg in p.out]
 assets(jobs);print('ITMO:',len(jobs),'annual archives (SPb and Northwest)',flush=True)

def kalva():
 u='https://mks.mff.cuni.cz/kalva/putnam.html'
 data=fetch('putnam-historical',u,None,'index',source='John Scholes archive; university redirect to prase.cz')
 if not data:return
 annual=[(v,year_of(t),t) for v,t in links(data,u) if re.search(r'/putnam/putn\d\d[a-z]?\.html$',v)]
 def year_page(item):
  v,y,label=item;d=fetch('putnam-historical',v,y,'problems',label,'John Scholes archive; university redirect to prase.cz')
  if not d:return []
  # Links are relative to the final archival host; both hosts redirect publicly.
  return [('putnam-historical',x,y,'solutions',t or 'Published individual solution','John Scholes archive; university redirect to prase.cz') for x,t in links(d,v) if '/putnam/psoln/' in x and x.endswith('.html')]
 jobs=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for found in pool.map(year_page,annual):jobs.extend(found)
 assets(jobs)
 print('Historical Putnam:',len(annual),'annual papers,',len(jobs),'solution pages',flush=True)

def msu_algebra():
 c='msu-algebra';u='https://halgebra.math.msu.su/wiki/doku.php/shared:%D0%BE%D0%BB%D0%B8%D0%BC%D0%BF%D0%B8%D0%B0%D0%B4%D1%8B'
 d=fetch(c,u,None,'index',source='official department organizer')
 if not d:return
 ll=links(d,u)
 annual=[(v,year_of(v)) for v,t in ll if re.search(r'/Olympiad/(?:19|20)\d\d',v) or re.search(r'/shared:olympiad_20\d\d$',v)]
 jobs=[(c,v,year_of(v),kind_of(v,t),t,'official department organizer') for v,t in ll if ASSET.search(v) and not EXCLUDE.search(v+' '+t) and RELEVANT.search(unquote(v)+' '+t)]
 def one(item):
  v,y=item;d=fetch(c,v,y,'index',source='official department organizer')
  if not d:return []
  return [(c,x,year_of(x,y),kind_of(x,t),t,'official department organizer') for x,t in links(d,v) if ASSET.search(x) and not EXCLUDE.search(x+' '+t) and (('/Olympiad/' in x) or RELEVANT.search(unquote(x)+' '+t))]
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  for j in pool.map(one,annual):jobs.extend(j)
 assets(jobs)
 print('MSU algebra:',len(annual),'annual event pages,',len(jobs),'materials',flush=True)

def bauman():
 c='vso-bauman';u='https://baumo.narod.ru/zadachi.htm';d=fetch(c,u,None,'index',source='BMSTU olympiad team organizer O. Pugachev')
 if not d:return
 jobs=[]
 for v,t in links(d,u):
  if ASSET.search(v) and not EXCLUDE.search(v+' '+t):jobs.append((c,v,year_of(v),kind_of(v,t),t,'BMSTU olympiad team organizer O. Pugachev; year ranges verified in documents'))
 assets(jobs);print('BMSTU/VSО collections:',len(jobs),flush=True)

def kazakhstan():
 # All these filenames/years are listed by the official index (ELEMENT_ID=4854).
 # The index is intermittently unreachable, so retain the verified file inventory.
 jobs=[]
 for y in range(2008,2018):
  for kind,folder,prefix in [('problems','math-problems','problem'),('solutions','math-solutions','solution')]:
   u=f'https://www.msu.kz/upload/Files/ol/{folder}/{prefix}-{y}.pdf'
   jobs.append(('msu-kazakhstan',u,y,kind,f'Official index: {prefix}-{y}.pdf','official university organizer'))
 for kind,folder,prefix in [('problems','math-problems','problem'),('solutions','math-solutions','solution')]:
  for suffix,y in [('2014-bonus',2014),('2016-rep-math',2016),('2017-rep-math',2017)]:
   jobs.append(('msu-kazakhstan',f'https://www.msu.kz/upload/Files/ol/{folder}/{prefix}-{suffix}.pdf',y,kind,'Verified official annual file inventory','official university organizer'))
 jobs.append(('msu-kazakhstan','https://www.msu.kz/upload/Files/ol/math-solutions/solution-2019-rep-math.pdf',2019,'solutions','Republican university mathematics competition','official university organizer'))
 assets(jobs);print('MSU Kazakhstan:',len(jobs),'verified annual links attempted',flush=True)

def ucsd():
 c='putnam-ucsd';u='https://mathweb.ucsd.edu/~pfitz/pastputnam.html';d=fetch(c,u,None,'index',source='UC San Diego mathematics faculty archive')
 if not d:return
 jobs=[(c,v.replace('http://','https://'),year_of(v),'problems',t,'UC San Diego mathematics faculty archive') for v,t in links(d,u) if v.endswith('.pdf')]
 assets(jobs);print('UCSD Putnam:',len(jobs),'PDFs',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--resume',action='store_true',help='explicitly resume a user-paused download');p.add_argument('--only',default='imc,putnam,kalva,ucsd,itmo,msu-algebra,vso-bauman,kazakhstan,'+','.join(SOURCES));p.add_argument('--extra',help='JSON list of exact extra downloads; same fetch positional fields');args=p.parse_args()
 BASE.mkdir(parents=True,exist_ok=True)
 pause=BASE/'.paused'
 if pause.exists() and not args.resume:
  print('Archive is paused at user request; no network activity. Use --resume only after a new user request.');return
 if args.resume and pause.exists():pause.unlink()
 if MANIFEST.exists():
  for l in MANIFEST.read_text().splitlines():
   try:r=json.loads(l);ROWS[(r['contest'],r['url'])]=r
   except (ValueError,KeyError):pass
 for c in args.only.split(','):
  if c=='ucsd':ucsd()
  elif c=='kalva':kalva()
  elif c=='msu-algebra':msu_algebra()
  elif c=='vso-bauman':bauman()
  elif c=='kazakhstan':kazakhstan()
  elif c=='itmo':itmo()
  elif c=='imc':imc()
  elif c=='putnam':putnam()
  elif c in SOURCES:
   seeds,prefixes,depth=SOURCES[c];crawl(c,seeds,prefixes,depth)
 if args.extra:assets(json.loads(Path(args.extra).read_text()))
 # Keep one current manifest record per resource after any retry.
 with MANIFEST.open('w',encoding='utf-8') as f:
  for r in sorted(ROWS.values(),key=lambda x:(x['contest'],str(x['year']),x['url'])):f.write(json.dumps(r,ensure_ascii=False)+'\n')
 from collections import Counter
 print('manifest statuses:',dict(Counter(r['status'] for r in ROWS.values())),flush=True)

if __name__=='__main__':main()
