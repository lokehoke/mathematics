#!/usr/bin/env python3
"""Recover exactly linked archival scans and publisher-hosted public collections."""
import concurrent.futures, hashlib, json, re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from download_russia import ROOT, BASE, fetch, output_path, save_json, decode

def mmo_scans():
    mf=BASE/'mmo/manifest.json';m=json.loads(mf.read_text());records={r['url']:r for r in m['documents']};jobs={}
    for index in m['indexes']:
        if not any(x in index['url'] for x in ['archive/vars80.htm','problems93-10.htm']):continue
        soup=BeautifulSoup((ROOT/index['local_path']).read_bytes(),'html.parser')
        for a in soup.select('a[href]'):
            u=urljoin(index['url'],a['href']);ext=urlsplit(u).path.rsplit('.',1)[-1].lower()
            if ext not in ['jpg','jpeg','png','txt']:continue
            row=a.find_parent('tr');context=row.get_text(' ',strip=True) if row else ''
            ys=re.findall(r'(?<!\d)(19\d{2}|20\d{2})(?!\d)',context)
            if not ys:continue
            jobs[u]=dict(url=u,contest=m['contest'],subject='mathematics',year=ys[0],stage=None,classes=None,document_type='tasks',label=a.get_text(' ',strip=True),source_page=index['url'],source_status='official organizer',metadata_evidence='Year taken from annual table row: '+context[:180])
    def one(item):
        u,r=item;old=records.get(u)
        if old and old.get('status')=='downloaded':return old
        res=fetch(u,30)
        if not res['ok']:return dict(r,status='failed',error=res.get('error'))
        b=res['data'];ext=urlsplit(u).path.rsplit('.',1)[-1].lower()
        valid=(b.startswith(b'\xff\xd8\xff') if ext in ['jpg','jpeg'] else b.startswith(b'\x89PNG') if ext=='png' else bool(b.strip()) and b'<html' not in b[:1000].lower())
        if not valid:return dict(r,status='failed',error='File signature/content mismatch')
        p=output_path(BASE/'mmo/documents',u);p.write_bytes(b)
        return dict(r,status='downloaded',local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),final_url=res['final_url'],content_type=res['content_type'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        for r in ex.map(one,jobs.items()):records[r['url']]=r
    m['documents']=list(records.values());m['scan_recovery']=dict(links=len(jobs),downloaded=sum(records[u]['status']=='downloaded' for u in jobs))
    # Distinguish the problem-only and solved subsets of Prasolov's archive.
    for r in m['documents']:
        if '/prasolov/mo-ready/c-print.ps' in r['url']:
            r.update(document_type='tasks_and_solutions',covers_years=list(range(1935,1942))+list(range(1945,1955))+[1956],coverage_evidence='https://mmo.mccme.ru/prasolov/index.htm; almost all problems with solutions for these years',coverage_completeness='partial within listed years')
        elif '/prasolov/mo/c-print.ps' in r['url']:
            r.update(document_type='tasks',covers_years=list(range(1935,1942))+list(range(1945,1990)),coverage_evidence='https://mmo.mccme.ru/prasolov/index.htm; editions 1935–1941 and 1945–1989')
    for r in m['documents']:
        if r['url'].endswith('/books/mmo-35-57.pdf'):
            r.update(year='1935-1957',document_type='tasks_and_solutions',covers_years=list(range(1935,1942))+list(range(1945,1958)),coverage_evidence='PDF title and publisher abstract on page 2: problems with answers, hints and detailed solutions 1935–1957; war-year exclusions from official archive.')
        elif r['url'].endswith('/books/mmo-93-05.pdf'):
            r.update(year='1993-2005',document_type='tasks_and_solutions',covers_years=list(range(1993,2006)),coverage_evidence='PDF title and publisher abstract on page 2: problems with answers, hints and detailed solutions 1993–2005; publication year 2006 is not contest year.')
    save_json(mf,m);print('MMO scans',m['scan_recovery'],flush=True)

def historical_imo():
    # The educational publisher's public library explicitly offers this DJVU.
    import download_international as di
    for line in di.MANIFEST.read_text().splitlines():
        r=json.loads(line);di.RECORDS[(r['contest'],str(r['year']),r['type'],r['source'])]=r
    page='https://old.mccme.ru/free-books/djvu/olimp/mezhdunarodnye.htm'
    res=fetch(page)
    if not res['ok']:print('IMO collection index unavailable',res.get('error'));return
    soup=BeautifulSoup(decode(res['data'],res['content_type']),'html.parser')
    for a in soup.select('a[href]'):
        u=urljoin(page,a['href']).split('?')[0]
        if not u.endswith('mezhdunarodnye.djvu'):continue
        kind='problems_and_solutions';key=('IMO','1959-1975',kind,u)
        if di.RECORDS.get(key,{}).get('status')=='downloaded':continue
        rr=fetch(u,40)
        if not rr['ok'] or not (rr['data'].startswith(b'AT&TFORM') and b'DJV' in rr['data'][:20]):print('IMO collection unavailable',rr.get('error'));continue
        p=di.OUT/'IMO/1959-1975/mezhdunarodnye.djvu';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(rr['data'])
        di.RECORDS[key]=dict(contest='IMO',year='1959-1975',type=kind,source=u,source_page=page,language='ru',status='downloaded',path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(rr['data']).hexdigest(),bytes=len(rr['data']),covers_years=list(range(1959,1976)),source_authority='MCCME public educational library',coverage_evidence='Library description: problems and detailed solutions of seventeen IMO editions, including XVII',note='Published 1976; also contains jury and national-contest material; only main IMO span attributed here.')
        print('IMO historical collection saved',len(rr['data']),flush=True)
    di.save_manifest()

def mmo_problem_pages():
    """Preserve individual historical tasks, without claiming complete variants."""
    mf=BASE/'mmo/manifest.json';m=json.loads(mf.read_text());records={r['url']:r for r in m['documents']}
    root='https://problems.ru/view_by_source_new.php?parent=164898';res=fetch(root)
    if not res['ok']:print('Problems.ru index unavailable');return
    soup=BeautifulSoup(decode(res['data'],res['content_type']),'html.parser');jobs={}
    for a in soup.select('a[href]'):
        match=re.fullmatch(r'(199[012]) год',a.get_text(' ',strip=True))
        if not match:continue
        year=int(match[1]);u=urljoin(root,a['href']);rr=fetch(u)
        if not rr['ok']:continue
        sp=BeautifulSoup(decode(rr['data'],rr['content_type']),'html.parser')
        page_urls={u}
        page_urls.update(urljoin(u,link['href']) for link in sp.select('a[href]') if '&start=' in link['href'] and '/view_by_source_new.php?' in link['href'])
        for page_url in sorted(page_urls):
            if page_url!=u:
                page_res=fetch(page_url)
                if not page_res['ok']:continue
                listing=BeautifulSoup(decode(page_res['data'],page_res['content_type']),'html.parser')
            else:listing=sp
            for link in listing.select('a[href]'):
                v=urljoin(page_url,link['href'])
                if re.fullmatch(r'/view_problem_details_new.php\?id=\d+',urlsplit(v).path+'?'+urlsplit(v).query):jobs[v]=(year,page_url)
    def one(item):
        u,(year,src)=item
        if records.get(u,{}).get('status')=='downloaded':return records[u]
        r=dict(url=u,contest=m['contest'],subject='mathematics',year=year,stage=None,classes=None,document_type='tasks_or_solutions_html',source_page=src,source_status='MCCME public problem database',coverage_completeness='individual problem; not a complete variant')
        rr=fetch(u)
        if not rr['ok']:return dict(r,status='failed',error=rr.get('error'))
        sp=BeautifulSoup(decode(rr['data'],rr['content_type']),'html.parser');text=sp.get_text(' ',strip=True)
        if 'Московская математическая олимпиада' not in text or str(year) not in text:return dict(r,status='failed',error='Contest/year content check failed')
        # A labelled solution is present in the published detail page itself.
        if re.search(r'Решение\s+.{100}',text):r['document_type']='tasks_and_solutions'
        p=output_path(BASE/'mmo/documents',u,'.html');p.write_bytes(rr['data'])
        assets=[]
        for img in sp.select('img[src]'):
            v=urljoin(u,img['src'])
            if urlsplit(v).netloc!='problems.ru' or not any(w in urlsplit(v).path for w in ['/images/','/img/','/pictures/']):continue
            ir=fetch(v)
            if not ir['ok'] or not ir.get('content_type','').startswith('image/'):continue
            target=BASE/'mmo/supporting-assets';target.mkdir(exist_ok=True);ip=output_path(target,v);ip.write_bytes(ir['data'])
            assets.append(dict(url=v,path=str(ip.relative_to(ROOT)),sha256=hashlib.sha256(ir['data']).hexdigest()))
        return dict(r,status='downloaded',local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(rr['data']).hexdigest(),bytes=len(rr['data']),supporting_assets=assets,content_validation='Contest and year in page text; solution heading checked')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(one,jobs.items()):records[r['url']]=r
    m['documents']=list(records.values());m['individual_problem_recovery']=dict(years=[1990,1991,1992],discovered=len(jobs),downloaded=sum(records[u]['status']=='downloaded' for u in jobs),coverage='Individual tasks; full original variants not asserted')
    save_json(mf,m);print('MMO individual tasks',m['individual_problem_recovery'])

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--only',choices=['scans','imo','mmo-problems']);args=ap.parse_args()
    if not args.only or args.only=='scans':mmo_scans()
    if not args.only or args.only=='imo':historical_imo()
    if not args.only or args.only=='mmo-problems':mmo_problem_pages()
