#!/usr/bin/env python3
"""Read current official tables, including extensionless PDF downloads."""
import concurrent.futures, hashlib, json, re
from urllib.parse import urljoin,unquote
from bs4 import BeautifulSoup
from download_russia import ROOT,BASE,fetch,decode,output_path,save_json

def get_soup(url):
    r=fetch(url)
    if not r['ok']:raise RuntimeError(r.get('error'))
    return BeautifulSoup(decode(r['data'],r['content_type']),'html.parser'),r['final_url']

def phystech_jobs():
    src='https://olymp-online.mipt.ru/page/primery-zadanij';s,base=get_soup(src);jobs={}
    for table in s.select('table'):
        heading=table.find_previous(['h1','h2','h3','h4']);title=heading.get_text(' ',strip=True) if heading else ''
        match=re.search(r'(20\d{2})(?:/(\d{2}))?',title)
        if not match:continue
        year=f'{match[1]}/20{match[2]}' if match[2] else int(match[1])
        stage='qualifying' if 'Отборочный' in title else 'final'
        spans={};headers={}
        for tr in table.select('tr'):
            row={c:v[0] for c,v in spans.items()};spans={c:(v,n-1) for c,(v,n) in spans.items() if n>1}
            col=0
            for td in tr.find_all(['td','th'],recursive=False):
                while col in row:col+=1
                width=int(td.get('colspan',1));height=int(td.get('rowspan',1))
                for c in range(col,col+width):
                    row[c]=td
                    if height>1:spans[c]=(td,height-1)
                col+=width
            if not row:continue
            if row.get(0) and row[0].get_text(' ',strip=True)=='Предмет':
                if not headers:headers={c:td.get_text(' ',strip=True) for c,td in row.items()}
                continue
            if not row.get(0) or row[0].get_text(' ',strip=True)!='Математика':continue
            grade=row[1].get_text(' ',strip=True) if 1 in row else None
            for c,td in row.items():
                if c<2:continue
                label=headers.get(c,'')
                kind='solutions' if re.search(r'решен',label,re.I) else 'marking_scheme' if re.search(r'критер',label,re.I) else 'tasks'
                for a in td.select('a[href]'):
                    u=urljoin(base,a['href'])
                    if '/folders/file/' not in u and not u.lower().endswith('.pdf'):continue
                    jobs[u]=dict(year=year,stage=stage,classes=grade,document_type=kind,label=label+' '+a.get_text(' ',strip=True),source_page=src)
    return jobs

def innopolis_jobs():
    src='https://dovuz.innopolis.university/innopolis-open/math';s,base=get_soup(src);jobs={}
    for a in s.select('a[href]'):
        u=urljoin(base,a['href']);cursor=a
        while cursor.parent and cursor.previous_sibling is None:cursor=cursor.parent
        label=BeautifulSoup(str(cursor.previous_sibling or ''),'html.parser').get_text(' ',strip=True)[-180:]
        if not re.search(r'задач|решен',label,re.I) or 'победител' in label.lower():continue
        if not u.lower().endswith('.pdf'):continue
        name=unquote(u).rsplit('/',1)[-1]
        if re.search(r'result|итог|побед',name,re.I):continue
        pair=re.search(r'(?<!\d)(2[0-6])[-_](2[0-7])(?!\d)',name)
        full=re.search(r'(20\d{2})[-_](20\d{2})',name)
        if pair:year=f'20{pair[1]}/20{pair[2]}'
        elif full:year=f'{full[1]}/{full[2]}'
        else:
            year=None
            for node in a.find_all_previous(['h2','h3','h4','strong','b']):
                text=node.get_text(' ',strip=True);mm=re.search(r'Олимпиада\s+(20\d{2})/(\d{2})',text)
                if mm:year=f'{mm[1]}/20{mm[2]}';break
        jobs[u]=dict(year=year,stage='final' if re.search(r'final',name,re.I) else 'qualifying' if re.search(r'round|tour|тур',name,re.I) else None,classes=None,document_type='tasks_and_solutions',label=label,source_page=src)
    return jobs

def collect(cid,jobs):
    mf=BASE/cid/'manifest.json';m=json.loads(mf.read_text());records={r['url']:r for r in m['documents']}
    def one(item):
        u,md=item;old=records.get(u)
        if old and old.get('status')=='downloaded' and (ROOT/old['local_path']).is_file():
            old.update(md);return old
        row=dict(url=u,contest=m['contest'],subject='mathematics',source_status='official organizer',**md);r=fetch(u,35)
        if not r['ok']:return dict(row,status='failed',error=r.get('error'))
        if not r['data'].startswith(b'%PDF') and '/folders/file/' in u:
            wrapper=BeautifulSoup(decode(r['data'],r['content_type']),'html.parser')
            obj=wrapper.find('object',attrs={'type':'application/pdf'})
            target=urljoin(r['final_url'],obj.get('data','')) if obj else ''
            if target.startswith('https://idproctor.mipt.ru/public/folder_attachment/'):
                row['published_pdf_url']=target;r=fetch(target,35)
                if not r['ok']:return dict(row,status='failed',error=r.get('error'))
        if not r['data'].startswith(b'%PDF'):return dict(row,status='failed',error='Expected actual PDF, including extensionless download')
        p=output_path(BASE/cid/'documents',u,'.pdf');p.write_bytes(r['data'])
        return dict(row,status='downloaded',local_path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(r['data']).hexdigest(),bytes=len(r['data']),content_type=r['content_type'],final_url=r['final_url'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        for row in ex.map(one,jobs.items()):records[row['url']]=row
    m['documents']=list(records.values());m['current_official_page_pass']=dict(discovered=len(jobs),downloaded=sum(records[u]['status']=='downloaded' for u in jobs));save_json(mf,m)
    print(cid,m['current_official_page_pass'],flush=True)

if __name__=='__main__':
    collect('phystech',phystech_jobs());collect('innopolis',innopolis_jobs())
