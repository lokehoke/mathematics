#!/usr/bin/env python3
"""Discover and preserve public official international mathematics contest papers.

No URL template is treated as a successful download: every document is obtained
from an actual official archive link and checked before it enters the manifest.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
import time
from collections import Counter
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'olympiads/international'
CACHE = ROOT / 'research/international_cache'
MANIFEST = OUT / 'manifest.jsonl'
UA = 'MathematicsPublicArchive/1.0 (public educational archive; respectful fetch)'
RECORDS = {}


def register(contest, year, kind, url, source_page, language='en', **extra):
    record = dict(contest=contest, year=year, type=kind, source=url,
                  source_page=source_page, language=language, status='discovered',
                  path=None, sha256=None, **extra)
    key = (contest, str(year), kind, url)
    if key not in RECORDS or RECORDS[key].get('status') != 'downloaded':
        RECORDS[key] = record


def gap(contest, year, kind, source_page, reason):
    register(contest, year, kind, source_page, source_page, language=None,
             note=reason)
    RECORDS[(contest, str(year), kind, source_page)]['status'] = 'not_available_on_checked_official_archive'


def save_manifest():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = sorted(RECORDS.values(), key=lambda x:(x['contest'], str(x['year']), x['type'], x['source']))
    temp = MANIFEST.with_suffix('.tmp')
    temp.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))
    temp.replace(MANIFEST)


def year_of(s, fallback=None):
    matches = re.findall(r'(?:19|20)\d{2}', s)
    return int(matches[-1]) if matches else fallback


def pdf_links(soup, base):
    return [(u,t,a) for u,t,a in links(soup,base) if re.search(r'\.pdf(?:$|[?#])',u,re.I)]


def discover_apmo():
    src = 'https://www.apmo-official.org/problems'
    soup, base = page(src)
    for u,t,a in pdf_links(soup,base):
        register('APMO',year_of(u),'solutions' if '/solutions/' in u else 'problems',u,src)


def discover_imo():
    src = 'https://www.imo-official.org/problems/?language=en'
    soup, base = page(src)
    years = [urljoin(base,o['value']) for o in soup.select('#year-select option[value]')]
    def one(u):
        try:
            s,b=page(u); y=year_of(u)
            for o in s.select('#problems-language option[value]'):
                code=o.get('data-lang-code')
                if code in ('eng','rus'):
                    register('IMO',y,'problems',urljoin(b,o['value']),u,'ru' if code=='rus' else 'en')
            for v,t,a in pdf_links(s,b):
                if 'SL.pdf' in v or 'shortlist' in v.lower():
                    register('IMO',y,'shortlist_problems_and_solutions',v,u)
            if not any(r['contest']=='IMO' and r['year']==y and 'solutions' in r['type'] for r in list(RECORDS.values())):
                gap('IMO',y,'solutions',u,'No official final-paper solutions linked on the central problem archive; shortlist documents are recorded separately.')
        except Exception as e:
            gap('IMO',year_of(u),'index',u,str(e))
    with ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(one,years))
    gap('IMO',1980,'edition',src,'No 1980 edition is listed in the official archive (IMO was not held).')


def discover_egmo():
    src='https://www.egmo.org/'
    soup,b=page(src)
    entries=[(u,year_of(t)) for u,t,a in links(soup,b) if re.fullmatch(r'EGMO 20\d\d',t) and year_of(t)<=2026]
    def one(entry):
        u,y=entry
        try:
            s,b=page(u)
            for v,t,a in links(s,b):
                low=(v+' '+t).lower()
                if '.pdf' in v.lower() and ('solution' in low or 'marking' in low):
                    register('EGMO',y,'problems_and_solutions',v,u)
                elif '.pdf' in v.lower() and 'english' in low and '-bg-' not in v:
                    register('EGMO',y,'problems',v,u)
                elif 'solution' in t.lower() and urlparse(v).netloc != urlparse(u).netloc:
                    try:
                        ss,bb=page(v)
                        files=pdf_links(ss,bb)
                        for vv,tt,aa in files:
                            if any(w in (vv+' '+tt).lower() for w in ['solution','marking','problem']):
                                register('EGMO',y,'problems_and_solutions',vv,v)
                        if not files:
                            register('EGMO',y,'solutions_html',v,u)
                    except Exception as e: gap('EGMO',y,'solutions',v,str(e))
            if not any(r['contest']=='EGMO' and r['year']==y and 'solutions' in r['type'] and r['status'] in ('discovered','downloaded') for r in list(RECORDS.values())):
                gap('EGMO',y,'solutions',u,'No solutions link found on the official annual index.')
        except Exception as e: gap('EGMO',y,'index',u,str(e))
    with ThreadPoolExecutor(max_workers=5) as pool: list(pool.map(one,entries))


def discover_baltic():
    src='https://www.math.olympiaadid.ut.ee/eng/html/index.php?id=bw'
    soup,b=page(src)
    for u,t,a in pdf_links(soup,b):
        m=re.search(r'/bw(\d\d)(eng|sol)\.pdf',u)
        if m:
            n=int(m[1]);y=1900+n if n>=90 else 2000+n
            register('BalticWay',y,'problems_and_solutions' if m[2]=='sol' else 'problems',u,src)
    for y in range(1990,2026):
        if not any(r['contest']=='BalticWay' and r['year']==y and 'solutions' in r['type'] for r in list(RECORDS.values())):
            gap('BalticWay',y,'solutions',src,'Official University of Tartu archive links no solutions for this year.')


def preferred_pdf(url, label):
    low=unquote(url+' '+label).lower()
    if any(w in low for w in ['regulation','schedule','programme','program.pdf','result','statistic','travel','participant','invitation','annual_reg','conduct','tour','report','logo','poster','flyer','sponsor','bulletin','unknotting']):
        return False
    if any(w in low for w in ['english','_en.','-en.','eng.pdf','en.pdf','official','solution','booklet']):
        return True
    if re.search(r'(?:[_/\-])(hr|cs|cz|fr|de|hu|lt|pl|sk|sl|ro|sr|slo|ger|rom)(?:[_.\-/])',low):
        return False
    if any(w in low for w in ['croatian','czech','french','german','hungarian','lithuanian','polish','slovak','slovene','romanian','russian','turkish','albanian','bulgarian','greek','bosnian','italian','macedonian','montenegrin','serbian','spanish','armenian','georgian','arabic','azerbaijani','uzbek']):
        return False
    return True


def crawl_materials(contest, year, start, max_pages=14):
    queue=[(start,0)];seen=set();count=0;host=urlparse(start).netloc
    while queue and len(seen)<max_pages:
        u,depth=queue.pop(0)
        if u in seen:continue
        seen.add(u)
        try:s,b=page(u)
        except Exception as e:
            gap(contest,year,'index',u,str(e));continue
        for v,t,a in links(s,b):
            low=(v+' '+t).lower()
            if any(w in low for w in ['physics','chemystry','chemistry','computer_science','informatics','login','log-in']):continue
            if re.search(r'\.pdf(?:$|[?#])',v,re.I):
                if not preferred_pdf(v,t):continue
                if any(w in low for w in ['shortlist','shortlisted']):kind='shortlist_problems_and_solutions'
                elif any(w in low for w in ['solution','solut','booklet','loesung','rjesen','řešen','riesen']):kind='problems_and_solutions'
                else:kind='problems'
                register(contest,year,kind,v,u,'en' if any(w in low for w in ['english','_en.','eng.pdf','en.pdf','official','solutions']) else 'und')
                count+=1
            elif depth<2 and urlparse(v).netloc==host and any(w in low for w in ['problem','solution','download','booklet','competition','contest','aufgab','zadani','material']):
                if any(w in low for w in ['result','regulation','participant','photo','gallery','committee','report','training']):continue
                foundyear=year_of(urlparse(v).path)
                if foundyear and foundyear!=year:continue
                queue.append((v,depth+1))
    return count


def discover_rmm():
    src='https://rmms.lbi.ro/'
    soup,b=page(src)
    entries={}
    for u,t,a in links(soup,b):
        if re.fullmatch(r'\d+(st|nd|rd|th)',t):
            edition=int(re.match(r'\d+',t)[0]);year=2007+edition
            if edition>=7:year+=1
            if edition>=14:year+=1
            entries[year]=u
    entries[2026]=b
    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(lambda e:crawl_materials('RMM',e[0],e[1]),entries.items()))
    # UKMT is the official national delegation and publishes the actual contest papers.
    uk='https://bmos.ukmt.org.uk/home/rmm.shtml'
    s,b=page(uk)
    for u,t,a in pdf_links(s,b):
        if urlparse(u).netloc=='bmos.ukmt.org.uk' and 'rmm-' in u:
            register('RMM',year_of(u),'problems',u,uk)
    # Actual official URL found by the web index when the legacy index stopped rendering PHP.
    register('RMM',2009,'problems_and_solutions','https://rmms.lbi.ro/rmm2/_dwl/solutions2009.pdf',
             'https://rmms.lbi.ro/rmm2/',discovery='official PDF indexed by web search')
    for year in (2014,2022):gap('RMM',year,'edition',src,'No edition listed for this calendar year on the official edition index.')


def discover_memo():
    src='https://memo-official.org/MEMO/contests/previous/'
    s,b=page(src);entries=[]
    for tr in s.find_all('tr'):
        text=tr.get_text(' ',strip=True);matches=re.findall(r'\b20\d\d\b',text)
        if not matches:continue
        year=int(matches[0])
        if not 2007<=year<=2026:continue
        external=[u for u,t,a in links(tr,b) if urlparse(u).netloc != 'memo-official.org']
        if external:entries.append((year,external[0]))
        else:gap('MEMO',year,'index',src,'Official annual index provides no surviving host URL.')
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(lambda e:crawl_materials('MEMO',e[0],e[1]),entries))
    crawl_materials('MEMO',2024,'https://www.bolyai.hu/versenyek-memo2024-problems')


def discover_bmo():
    src='https://bmos.ukmt.org.uk/home/balkan.shtml';s,b=page(src)
    entries=[]
    for u,t,a in links(s,b):
        m=re.fullmatch(r'Balkan MO (20\d\d)',t)
        if m:entries.append((int(m[1]),u))
    entries += [(2026,'https://hms.gr/43bmo2026/problems.html'),(2024,'https://bmo2024.org/problems/'),
                (2023,'https://bmo2023.tubitak.gov.tr/problems')]
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(lambda e:crawl_materials('BMO',e[0],e[1],18),entries))


def discover_supplements():
    # Host archives fill the two omissions in the central EGMO solutions index.
    crawl_materials('EGMO',2012,'https://www.egmo2012.org.uk/competition/')
    crawl_materials('EGMO',2014,'https://egmo2014.tubitak.gov.tr/index.html_q%3DProblems.html')
    # Freely published complete book from the national Mathematical Society of Serbia.
    register('BMO','1984-1995','official_society_problems_and_solutions',
             'https://dms.rs/wp-content/uploads/2021/09/Sveska-32.pdf',
             'https://dms.rs/materijali-za-mlade-matematicare/','sr',
             covers_years=list(range(1984,1996)),covers_contests=['BMO','IMO'],
             note='Complete 137-page official society publication; Serbian fallback where English/Russian official historical solutions were not found.')


def discover_society():
    register('BMO','1996-2006','official_society_problems_and_solutions',
             'https://dms.rs/wp-content/uploads/2016/12/Sveska48.pdf',
             'https://dms.rs/materijali-za-mlade-matematicare/','sr',
             covers_years=list(range(1996,2007)),covers_contests=['BMO','IMO'],
             note='Complete 139-page official society publication with all IMO/BMO statements and solutions in Serbian.')


def discover_skmo():
    src='https://skmo.sk/dokumenty.php';s,b=page(src)
    urls={}
    for o in s.select('select[name=rocnik] option[value]'):
        value=o['value']
        if not value.isdigit() or int(value)==0:continue
        y=year_of(o.get_text(' ',strip=True))
        if y and 2007<=y<=2026:urls[y]=urljoin(b,'dokumenty.php?rocnik='+value)
    for u,t,a in links(s,b):
        if '?rocnik=' in u:
            ry=re.search(r'rocnik=(\d+)',u)
            if ry:
                y=1951+int(ry[1])
                if 2007<=y<=2026:urls[y]=u
    def one(entry):
        y,u=entry
        try:
            ss,bb=page(u)
            for tr in ss.find_all('tr'):
                text=tr.get_text(' ',strip=True);low=text.lower()
                if 'memo' not in low or any(w in low for w in ['kvalifik','sústred','sustred','výber','vyber','reprezent']):continue
                if re.search(r'\bimo\b',low):continue
                if not any(w in low for w in ['zadan','riešen','riesen','solution','booklet','problem']):continue
                for v,t,a in links(tr,bb):
                    if 'dokument.php?id=' in v or '.pdf' in v.lower():
                        register('MEMO',y,'problems_and_solutions' if any(w in low for w in ['riešen','riesen','solution']) else 'problems',
                                 v,u,'en' if any(w in low for w in ['anglick','english',' en)']) else 'sk',context=text[:600])
        except Exception as e:gap('MEMO',y,'index',u,str(e))
    with ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(one,urls.items()))


def download(record):
    r=dict(record)
    filename=unquote(Path(urlparse(r['source']).path).name) or 'document'
    filename=re.sub(r'[^\w.\-]+','_',filename)[:160]
    ext='.html' if r['type'].endswith('_html') else '.pdf'
    if not filename.lower().endswith(ext): filename+=ext
    name=f"{r['type']}_{r.get('language') or 'und'}_{hashlib.sha256(r['source'].encode()).hexdigest()[:8]}_{filename}"
    target=OUT/r['contest']/str(r['year'])/name
    try:
        if target.exists():
            data=target.read_bytes(); mime='application/pdf' if ext=='.pdf' else 'text/html';final=r['source']
        else:
            response=fetch(r['source']);data=response.content
            mime=response.headers.get('Content-Type','').split(';')[0].strip().lower();final=response.url
        if ext=='.pdf':
            if b'%PDF-' not in data[:1024]: raise ValueError(f'Invalid PDF signature; MIME={mime}, prefix={data[:45]!r}')
            if len(data)<100: raise ValueError('PDF is implausibly short')
        else:
            if b'<html' not in data[:10000].lower() and b'<!doctype html' not in data[:10000].lower():
                raise ValueError('Invalid HTML signature')
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists(): target.write_bytes(data)
        r.update(status='downloaded',path=str(target.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),
                 bytes=len(data),mime=mime,final_url=final,pdf_signature_valid=(ext=='.pdf'))
    except Exception as e: r.update(status='download_error',error=str(e))
    return r


def run_downloads():
    todo=[r for r in RECORDS.values() if r['status']=='discovered' or r['status']=='download_error']
    print('DOWNLOAD_QUEUE',len(todo),flush=True)
    count=0; started=time.monotonic()
    with ThreadPoolExecutor(max_workers=8) as pool:
        for future in as_completed([pool.submit(download,r) for r in todo]):
            r=future.result(); RECORDS[(r['contest'],str(r['year']),r['type'],r['source'])]=r
            count+=1
            if count%25==0 or count==len(todo):
                save_manifest()
                print('PROGRESS',count,'/',len(todo),dict(Counter(x['status'] for x in RECORDS.values())),round(time.monotonic()-started,1),'seconds',flush=True)
    save_manifest()


def fetch(url, retries=2):
    error = None
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers={'User-Agent': UA}, timeout=(12, 35))
            if r.status_code == 403 and url.startswith('http://') and ('HTTPS' in r.text[:300] or 'https' in r.text[:300]):
                r = requests.get('https://'+url[7:], headers={'User-Agent': UA}, timeout=(12,35))
            r.raise_for_status()
            if len(r.content) > 75_000_000:
                raise ValueError('Document exceeds 75 MB safety limit')
            return r
        except Exception as e:
            error = e
            if attempt < retries:
                time.sleep(attempt + 1)
    raise RuntimeError(f'{type(error).__name__}: {error}')


def page(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()
    target = CACHE / f'{key}.html'
    if target.exists():
        return BeautifulSoup(target.read_bytes(), 'html.parser'), url
    r = fetch(url)
    target.write_bytes(r.content)
    (CACHE / f'{key}.json').write_text(json.dumps({
        'source': url, 'final_url': r.url, 'content_type': r.headers.get('Content-Type'),
        'retrieved_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }, ensure_ascii=False, indent=2))
    return BeautifulSoup(r.content, 'html.parser'), r.url


def links(soup, base):
    for a in soup.find_all(['a', 'iframe', 'embed', 'object']):
        raw = a.get('href') or a.get('src') or a.get('data')
        if not raw or raw.startswith(('javascript:', 'mailto:', '#')):
            continue
        yield urljoin(base, raw), a.get_text(' ', strip=True), a


def probe(url):
    try:
        soup, final = page(url)
        print('PAGE', final, flush=True)
        for u, label, a in links(soup, final):
            print(u, '|', label[:140], flush=True)
        for form in soup.find_all(['select', 'form', 'script']):
            if form.name != 'script' or any(x in str(form).lower() for x in ['pdf', 'problems', 'language', 'download']):
                print('CONTROL', str(form)[:10000], flush=True)
    except Exception as e:
        print('ERROR', url, str(e), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe', nargs='+')
    parser.add_argument('--contests',nargs='+',default=['APMO','IMO','EGMO','BalticWay'])
    args = parser.parse_args()
    if args.probe:
        with ThreadPoolExecutor(max_workers=5) as pool:
            list(pool.map(probe, args.probe))
        return
    if MANIFEST.exists():
        for line in MANIFEST.read_text().splitlines():
            r=json.loads(line);RECORDS[(r['contest'],str(r['year']),r['type'],r['source'])]=r
    modules={'APMO':discover_apmo,'IMO':discover_imo,'EGMO':discover_egmo,'BalticWay':discover_baltic,
             'RMM':discover_rmm,'MEMO':discover_memo,'BMO':discover_bmo,'supplements':discover_supplements,'SKMO':discover_skmo,'society':discover_society}
    for contest in args.contests:
        print('DISCOVER',contest,flush=True)
        try: modules[contest]()
        except Exception as e: gap(contest,None,'index','official archive',str(e))
        save_manifest()
    run_downloads()


if __name__ == '__main__':
    main()
