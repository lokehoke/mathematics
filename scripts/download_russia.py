#!/usr/bin/env python3
"""Download public mathematics contest archives from organizers.

No logins, paywalls or access-control bypasses. HTML indexes and failed requests
are recorded separately from successfully downloaded contest documents.
Use --contest ID to resume one contest; --max-pages is an explicit crawl bound,
not a claim that the archive is complete. Existing verified files are reused.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, html, json, re, sys, threading, time
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'olympiads' / 'russia'
UA = 'Mozilla/5.0 (public mathematics educational archive; noncommercial research)'
MATH = re.compile(r'математ|\bmath\b|math[-_\d/]|matem|algebra|geometry', re.I)
POS = re.compile(r'зада[чн]|услов|решени|ответ|критери|problem|solution|task|answer|задани|archive|архив', re.I)
NEG = re.compile(r'result|rezult|protocol|protokol|(?:^|[/_-])prots|диплом|спис[ок]|результат|протокол|жюри|согласие|персональн|положени|правила|регламент|winners|победител|приз[её]р|participants|contact|контакт|jury|program|программ|poster|logo', re.I)
OTHER = re.compile(r'физик|physics|phys[-_/]|хими|chem|биолог|biolog|истор|histor|литератур|literat|информат|informat|эконом|econom|географ|geograph|обществ|societ|русск|russian|англий|english|правовед|юриспруд', re.I)
EXT = re.compile(r'\.(pdf|zip|rar|7z|djvu|ps|docx?|rtf|tex)(?:$|[?#])', re.I)

CONTESTS = {
 'mmo': dict(name='Московская математическая олимпиада', seeds=['https://mmo.mccme.ru/'], domains=['mmo.mccme.ru'], scope=r'.*', math_only=True, depth=5),
 'turgor': dict(name='Математический Турнир городов', seeds=['https://turgor.ru/problems/','https://olympiads.mccme.ru/turgor/turgor.htm'], domains=['www.turgor.ru','turgor.ru','olympiads.mccme.ru'], scope=r'(?:.*turgor.*|.*problems.*|.*\d.*)', math_only=True, depth=5),
 'vsosh': dict(name='Всероссийская олимпиада школьников по математике', seeds=['https://matholymp.ru/','http://matholymp.ru/','https://vos.olimpiada.ru/tasks?subject=math','https://olympiads.mccme.ru/vmo/'], domains=['matholymp.ru','www.matholymp.ru','vos.olimpiada.ru','olympiads.mccme.ru'], scope=r'(?:.*math.*|.*vmo.*|.*tasks.*)', math_only=False, depth=5),
 'hse': dict(name='Высшая проба — математика', seeds=['https://olymp.hse.ru/mmo/tasks-math'], domains=['olymp.hse.ru','www.hse.ru','hse.ru'], scope=r'.*tasks-math.*', math_only=True, depth=1),
 'lomonosov': dict(name='Ломоносов — математика', seeds=['https://olymp.msu.ru/rus/page/main/29/page/zadaniya-olimpiady-proshlyh-let'], domains=['olymp.msu.ru'], scope=r'(?:.*zadaniya.*|.*archive.*)', math_only=False, depth=2),
 'pvg': dict(name='Покори Воробьёвы горы — математика', seeds=['https://pvg.mk.ru/'], domains=['pvg.mk.ru','www.mk.ru'], scope=r'(?:.*pvg.*|.*archive.*|.*arhiv.*|.*zadani.*|.*math.*)', math_only=False, depth=4),
 'phystech': dict(name='Физтех — математика', seeds=['https://olymp.mipt.ru/olympiad/samples','https://olymp-online.mipt.ru/page/primery-zadanij'], domains=['olymp.mipt.ru','olymp-online.mipt.ru','mipt.ru'], scope=r'(?:.*fizteh.*|.*archive.*|.*arhiv.*|.*samples.*|.*primery.*|.*задани.*|.*математ.*|.*math.*)', math_only=False, depth=4),
 'spbu': dict(name='Олимпиада школьников СПбГУ — математика', seeds=['https://olympiada.spbu.ru/','https://sch-olymp.spbu.ru/'], domains=['olympiada.spbu.ru','sch-olymp.spbu.ru','spbu.ru'], scope=r'(?:.*matemat.*|.*math.*|.*arkhiv.*|.*arhiv.*|.*archive.*|.*material.*|.*zadani.*|.*past.*)', math_only=False, depth=4),
 'petersburg': dict(name='Санкт-Петербургская олимпиада по математике', seeds=['http://www.pdmi.ras.ru/~olymp/','https://www.pdmi.ras.ru/~olymp/'], domains=['www.pdmi.ras.ru','pdmi.ras.ru'], scope=r'.*/~olymp/.*', math_only=True, depth=5),
 'sammat': dict(name='САММАТ — математика', seeds=['https://sammat.samgtu.ru/'], domains=['sammat.samgtu.ru'], scope=r'.*', math_only=True, depth=4),
 'yumsh': dict(name='Олимпиада ЮМШ', seeds=['https://yumsh.ru/cms/yumsh-olymp/archive'], domains=['yumsh.ru','www.yumsh.ru','yumsh.spbu.ru'], scope=r'.*(?:olymp|олимп|archive|arhiv|задач).*', math_only=True, depth=4),
 'kurchatov': dict(name='Олимпиада Курчатов — математика', seeds=['https://olimpiadakurchatov.ru/','https://kurchatov.olimpiada.ru/'], domains=['olimpiadakurchatov.ru','kurchatov.olimpiada.ru'], scope=r'.*(?:math|математ|archive|arhiv|task|zadani|year|\d{4}).*', math_only=False, depth=4),
 'mekhmat': dict(name='Механико-математический факультет МГУ — школьные математические олимпиады', seeds=['https://math.msu.ru/olimpiady'], domains=['math.msu.ru'], scope=r'.*(?:olimp|олимп|archive|arhiv|zadani|задач).*', math_only=True, depth=3),
 'vsesib': dict(name='Всесибирская открытая олимпиада — математика',seeds=['https://sesc.nsu.ru/olymp-vsesib/sections/maths/'],domains=['sesc.nsu.ru'],scope=r'.*(?:olymp-vsesib/sections/maths|math|математ|archive|arhiv).*',math_only=True,depth=4),
 'innopolis': dict(name='Innopolis Open — математика',seeds=['https://dovuz.innopolis.university/innopolis-open'],domains=['dovuz.innopolis.university','innopolis.university'],scope=r'.*(?:innopolis-open|math|matem|archive|arhiv).*',math_only=False,depth=3),
 'izumrud': dict(name='Изумруд — математика',seeds=['https://dovuz.urfu.ru/olymps/izumrud'],domains=['dovuz.urfu.ru','izumrud.urfu.ru'],scope=r'.*(?:izumrud|math|matem|archive|arhiv).*',math_only=False,depth=4),
 'bibn': dict(name='Будущие исследователи — будущее науки — математика',seeds=['https://bibn.unn.ru/'],domains=['bibn.unn.ru','www.unn.ru'],scope=r'.*(?:math|математ|arhiv|archive|задани|zadani|prosh).*',math_only=False,depth=4),
 'verchenko': dict(name='Олимпиада имени И.Я. Верченко — математика и криптография',seeds=['https://v-olymp.ru/'],domains=['v-olymp.ru','www.v-olymp.ru'],scope=r'.*(?:math|matem|математ|verchen|верчен|archive|arhiv|задани|zadani).*',math_only=False,depth=4),
 'ommo': dict(name='Объединённая межвузовская олимпиада — математика',seeds=['https://olympiads.mccme.ru/ommo/','https://olympiads.mccme.ru/omo/'],domains=['olympiads.mccme.ru'],scope=r'.*/(?:ommo|omo)/.*',math_only=True,depth=5),
 'shag': dict(name='Шаг в будущее — математика',seeds=['https://olymp.bmstu.ru/ru/mathematics-olymp'],domains=['olymp.bmstu.ru'],scope=r'.*(?:mathemat|archive|arhiv|задач|задани|zadani).*',math_only=True,depth=3),
 'itmo': dict(name='Открытая олимпиада ИТМО — математика',seeds=['https://olymp.itmo.ru/'],domains=['olymp.itmo.ru'],scope=r'.*(?:math|математ|archive|arhiv|school|past|задач|задани).*',math_only=False,depth=4),
 'rosatom': dict(name='Росатом — математика',seeds=['https://olymp.mephi.ru/rosatom_it/'],domains=['olymp.mephi.ru'],scope=r'.*(?:rosatom|math|математ|archive|arhiv|задач|задани).*',math_only=False,depth=4),
 'turlom': dict(name='Турнир имени М.В. Ломоносова — математика',seeds=['https://turlom.olimpiada.ru/'],domains=['turlom.olimpiada.ru'],scope=r'.*(?:math|математ|archive|arhiv|задач|задани|\d{4}).*',math_only=False,depth=4),
 'belchonok': dict(name='Бельчонок — математика',seeds=['https://dovuz.sfu-kras.ru/abiturientu-sfu/olimpiady/belchonok/'],domains=['dovuz.sfu-kras.ru','sfu-kras.ru'],scope=r'.*(?:belchonok|math|математ|archive|arhiv|задач|задани).*',math_only=False,depth=4),
 'mos_probability': dict(name='Московская олимпиада по вероятности и статистике',seeds=['https://xn--l1ae4a.xn--l1afu.xn--p1ai/olymp/pt','https://ptlab.mccme.ru/node/1701'],domains=['xn--l1ae4a.xn--l1afu.xn--p1ai','ptlab.mccme.ru'],scope=r'.*(?:/olymp/pt|ptlab\.mccme\.ru/node/|вероят|статист).*',math_only=True,depth=4),
}

# Official pages moved or use meta-refresh navigation; keep the former addresses
# as provenance while following only subject-specific public archive branches.
CONTESTS['vsosh'].update(seeds=['https://olympiads.mccme.ru/vmo/','https://matholymp.ru/'],math_only=True,scope=r'.*(?:/vmo/|/mmo/okrug/|matholymp).*')
CONTESTS['bibn']['scope']=r'.*(?:calendar|archive|math|математ|задани|zadani).*'
CONTESTS['belchonok']['scope']=r'.*/abiturientu-sfu/olimpiady/belchonok/.*'
CONTESTS['turlom']['domains']+=['xn--k1acfgjg.xn--l1afu.xn--p1ai','olympiads.mccme.ru']
CONTESTS['turlom']['seeds']+=['https://xn--k1acfgjg.xn--l1afu.xn--p1ai/archives/архив/','https://olympiads.mccme.ru/turlom/']
CONTESTS['turlom']['scope']=r'.*(?:/archives/|/turlom/).*'
CONTESTS['mos_probability']['seeds']=['https://ptlab.mccme.ru/node/2904']
CONTESTS['sammat']['seeds']=['https://sammat.samgtu.ru/sammat','https://sammat.samgtu.ru/']

def canonical(url):
    p=urlsplit(html.unescape(url)); return urlunsplit((p.scheme,p.netloc.lower(),p.path,p.query,''))

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.items=[]; self.current=None; self.heading=''; self.hbuf=None; self.context=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ['h1','h2','h3','h4','h5']: self.hbuf=[]
        if tag=='a' and a.get('href'): self.current=[a['href'],[],self.heading,' '.join(self.context[-6:])]
    def handle_data(self,s):
        s=s.strip()
        if not s:return
        if self.current:self.current[1].append(s)
        if self.hbuf is not None:self.hbuf.append(s)
        self.context.append(s)
    def handle_endtag(self,tag):
        if tag=='a' and self.current:
            u,txt,h,c=self.current; self.items.append((u,' '.join(txt),h,c)); self.current=None
        if tag in ['h1','h2','h3','h4','h5'] and self.hbuf is not None:
            self.heading=' '.join(self.hbuf);self.hbuf=None

def decode(b,ctype=''):
    m=re.search(r'charset\s*=\s*["\']?([\w-]+)',ctype,re.I)
    declared=re.search(br'charset\s*=\s*["\']?([\w-]+)',b[:8192],re.I)
    candidates=([m.group(1)] if m else [])+([declared.group(1).decode('ascii')] if declared else [])+['utf-8','cp1251','koi8-r']
    for enc in candidates:
        try:return b.decode(enc)
        except (UnicodeDecodeError,LookupError):pass
    return b.decode('utf-8','replace')

def fetch(url,timeout=20):
    try:
        parsed=urlsplit(url)
        request_url=urlunsplit((parsed.scheme,parsed.netloc.encode('idna').decode(),quote(parsed.path,safe='/%:@!$&\'()*+,;=-._~'),quote(parsed.query,safe='=&%/:?+;,@-._~'),''))
        req=Request(request_url,headers={'User-Agent':UA})
        with urlopen(req,timeout=timeout) as r:
            return dict(ok=True,url=url,final_url=r.url,status=r.status,content_type=r.headers.get('Content-Type',''),data=r.read())
    except Exception as exc:return dict(ok=False,url=url,status=getattr(exc,'code',None),error=f'{type(exc).__name__}: {exc}')

def metadata(url,label,heading,context):
    # URL takes priority; nearby HTML context only supplies information absent there.
    text=unquote(url)+' '+label+' '+heading+' '+context
    years=re.findall(r'(?<!\d)((?:19|20)\d{2})(?:\s*[/_–—-]\s*((?:19|20)?\d{2}))?',text)
    year=None
    if years:
        first,second=years[0]
        # A filename like /2013/12-1-math.pdf is not the school year 2013/12.
        valid_second=second and (len(second)==4 or int(second)==(int(first)+1)%100)
        year=first+('/'+second if valid_second else '')
    compact=re.search(r'(?:zktg|zima|winter)(\d{2})(\d{2})(?:[-_/\.]|$)',unquote(url),re.I)
    if compact and (int(compact[2])-int(compact[1]))%100==1:
        first=(1900 if int(compact[1])>=70 else 2000)+int(compact[1])
        year=f'{first}/{first+1}'
    cm=re.search(r'(\d{1,2}(?:\s*[-–]\s*\d{1,2})?)\s*(?:класс|кл\b|grade)',text,re.I)
    if not cm:cm=re.search(r'(?:math|mat|klass|class|grade|tasks|sol)[-_]?(0?[4-9]|1[01])(?:[-_.]|$)',unquote(url),re.I)
    stage=None
    for pat,name in [(r'заключ|финал|final','final'),(r'регион|region','regional'),(r'муницип|municip','municipal'),(r'школьн|school','school'),(r'отбор|qualif|select','qualifying'),(r'осен|autumn','autumn'),(r'весен|spring','spring')]:
        if re.search(pat,text,re.I):stage=name;break
    has_tasks=bool(re.search(r'задач|задани|услов|task|problem',label+' '+url,re.I))
    has_sol=bool(re.search(r'решен|ответ|критери|solution|answer|(?:^|[/_-])sol(?:[/_.-]|$)',label+' '+url,re.I))
    typ='tasks_and_solutions' if has_tasks and has_sol else 'solutions' if has_sol else 'tasks' if has_tasks else 'mathematics_material'
    return dict(year=year,stage=stage,classes=cm.group(1) if cm else None,document_type=typ,label=label,heading=heading)

def output_path(folder,url,suffix=None):
    p=urlsplit(url); name=unquote(p.path.rsplit('/',1)[-1]) or 'index.html'
    name=re.sub(r'[^\w.() -]+','_',name)[:140]
    if suffix and not name.lower().endswith(suffix):name+=suffix
    return folder/(hashlib.sha256(url.encode()).hexdigest()[:12]+'-'+name)

def save_json(path,obj):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)

def crawl(cid,cfg,max_pages=4000,max_depth=None,workers=8):
    folder=BASE/cid;folder.mkdir(parents=True,exist_ok=True);(folder/'documents').mkdir(exist_ok=True);(folder/'indexes').mkdir(exist_ok=True)
    mf=folder/'manifest.json'
    old=json.loads(mf.read_text()) if mf.exists() else {}; records={r['url']:r for r in old.get('documents',[])}
    indexes={r['url']:r for r in old.get('indexes',[])}; failures=[];q=deque((u,0) for u in cfg['seeds']);seen=set();discovered={r['url']:r for r in old.get('pending_documents',[])}
    depthlimit=cfg['depth'] if max_depth is None else max_depth
    file_jobs={}; start=datetime.now(timezone.utc).isoformat()
    def remember_file(u,label,h,c,source):
        if u in discovered:return
        if cid=='lomonosov' and label.strip().lower()!='математика':return
        if cid=='spbu' and label.strip().lower()!='математика' and not re.search(r'[/_-]math(?:[/_.-]|\d)',unquote(u),re.I):return
        if NEG.search(label+' '+u) and not POS.search(label):return
        if OTHER.search(label+' '+unquote(u)) and not MATH.search(label+' '+unquote(u)):return
        if not(cfg.get('math_only') or MATH.search(label+' '+unquote(u)) or MATH.search(h) or (MATH.search(c) and not OTHER.search(c))):
            return
        rec=dict(url=u,contest=cfg['name'],subject='mathematics',source_page=source,**metadata(u,label,h,c))
        discovered[u]=rec
    def checkpoint():
        save_json(mf,dict(contest=cfg['name'],id=cid,subject='mathematics',started_at=start,updated_at=datetime.now(timezone.utc).isoformat(),scope=cfg,seeds=cfg['seeds'],crawl_limits=dict(max_pages=max_pages,max_depth=depthlimit),coverage_status='partial' if q or failures else 'all_links_within_declared_scope_processed',documents=list(records.values()),indexes=list(indexes.values()),failures=failures,discovered_documents=len(discovered),pending_pages=len(q),pending_documents=[r for u,r in discovered.items() if records.get(u,{}).get('status')!='downloaded']))
    def fetch_index(job):
        u,_=job; cached=indexes.get(u)
        if cached and (ROOT/cached.get('local_path','NONEXISTENT')).is_file():
            b=(ROOT/cached['local_path']).read_bytes()
            if hashlib.sha256(b).hexdigest()==cached.get('sha256'):
                return dict(ok=True,url=u,final_url=u,status=200,content_type='text/html',data=b,cache_reused=True)
        return fetch(u,12)
    while q and len(seen)<max_pages:
        batch=[]
        while q and len(batch)<workers:
            u,d=q.popleft()
            if u not in seen:seen.add(u);batch.append((u,d))
        if not batch:continue
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:out=list(ex.map(fetch_index,batch))
        for (u,d),res in zip(batch,out):
            if not res['ok']:
                failures.append({k:v for k,v in res.items() if k!='data'});continue
            b=res['data'];ctype=res['content_type']
            if b.startswith(b'%PDF') or b.startswith(b'PK\x03\x04'):
                remember_file(u,'','', '',u);rec=discovered.get(u)
                if rec:
                    path=output_path(folder/'documents',u,'.pdf' if b.startswith(b'%PDF') else '.zip');path.write_bytes(b);rec.update(status='downloaded',local_path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),content_type=ctype);records[u]=rec
                continue
            if 'html' not in ctype and b'<' not in b[:200]:continue
            path=output_path(folder/'indexes',u,'.html');path.write_bytes(b)
            indexes[u]=dict(url=u,local_path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),status='downloaded',role='archive_index')
            text=decode(b,ctype);parser=Links()
            try:parser.feed(text)
            except Exception:pass
            page_math=cfg.get('math_only') or bool(MATH.search(unquote(u)))
            try:
                from bs4 import BeautifulSoup
                soup=BeautifulSoup(text,'html.parser');items=[]
                for a in soup.find_all('a',href=True):
                    heading=a.find_previous(['h1','h2','h3','h4','h5']);row=a.find_parent('tr')
                    items.append((a['href'],a.get_text(' ',strip=True),heading.get_text(' ',strip=True) if heading else '',row.get_text(' ',strip=True) if row else ''))
                parser.items=items
                for meta in soup.find_all('meta'):
                    if str(meta.get('http-equiv','')).lower()=='refresh':
                        match=re.search(r'url\s*=\s*[\"\']?([^\"\']+)',str(meta.get('content','')),re.I)
                        if match:parser.items.append((match.group(1).strip(),'HTML refresh','',''))
            except ImportError:pass
            # HTML task/solution pages are primary published materials too.
            if page_math and POS.search(unquote(u)) and not re.search(r'archive|arhiv|архив|past|problems/?$|tasks/?$',u,re.I) and d>0:
                records[u]=dict(url=u,contest=cfg['name'],subject='mathematics',status='downloaded',local_path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),document_type='tasks_or_solutions_html',**{k:v for k,v in metadata(u,'',parser.heading,'').items() if k!='document_type'})
            for href,label,h,c in parser.items:
                v=canonical(urljoin(res['final_url'],href))
                if urlsplit(v).scheme not in ['http','https']:continue
                if EXT.search(v):
                    remember_file(v,label,h,c,u)
                elif d<depthlimit and urlsplit(v).netloc.lower() in cfg['domains'] and re.search(cfg['scope'],unquote(v),re.I):
                    if NEG.search(label+' '+unquote(v)) and not POS.search(label):continue
                    if OTHER.search(label+' '+unquote(v)) and not MATH.search(label+' '+unquote(v)):continue
                    if not re.search(r'login|register|logout|auth|calendar|search|facebook|vk\.com|mailto',v,re.I):q.append((v,d+1))
        checkpoint()
        print(f'{cid}: pages={len(seen)} queue={len(q)} documents_discovered={len(discovered)}',flush=True)
    pending=[]
    for u,rec in discovered.items():
        previous=records.get(u)
        if previous and previous.get('status')=='downloaded' and (ROOT/previous.get('local_path','NONEXISTENT')).is_file():continue
        pending.append((u,rec))
    def download(job):
        u,rec=job;res=fetch(u,30)
        if not res['ok']:return {**rec,**{k:v for k,v in res.items() if k!='data'},'status':'failed'}
        b=res['data'];ext=EXT.search(u);ext=('.'+ext.group(1).lower()) if ext else ''
        valid=(b.startswith(b'%PDF') if ext=='.pdf' else b.startswith(b'PK') if ext=='.zip' else True)
        if not valid:return {**rec,'status':'failed','error':'Content does not match advertised file type','content_type':res['content_type']}
        path=output_path(folder/'documents',u);path.write_bytes(b)
        result={**rec,'status':'downloaded','local_path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'content_type':res['content_type'],'final_url':res['final_url']}
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for i,rec in enumerate(ex.map(download,pending),1):
            records[rec['url']]=rec
            if i%20==0:checkpoint();print(f'{cid}: downloaded {i}/{len(pending)} new files',flush=True)
    checkpoint();success=sum(r.get('status')=='downloaded' for r in records.values())
    print(f'{cid}: COMPLETE successful_materials={success} files={len(records)} failed_pages={len(failures)}',flush=True)
    return dict(id=cid,downloaded=success,discovered=len(records),failed_pages=len(failures))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--contest',action='append',choices=sorted(CONTESTS));ap.add_argument('--max-pages',type=int,default=4000);ap.add_argument('--max-depth',type=int);ap.add_argument('--workers',type=int,default=8);args=ap.parse_args()
    selected=args.contest or list(CONTESTS)
    save_json(ROOT/'research'/'russia-archive-sources.json',CONTESTS)
    for cid in selected:
        try:crawl(cid,CONTESTS[cid],args.max_pages,args.max_depth,args.workers)
        except KeyboardInterrupt:raise
        except Exception as exc:print(f'{cid}: ERROR {exc}',file=sys.stderr,flush=True)
if __name__=='__main__':main()
