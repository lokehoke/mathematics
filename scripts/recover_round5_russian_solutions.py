#!/usr/bin/env python3
"""Target only published solution/answer links for remaining Russian years."""
import hashlib,json
from recover_round4_russian_mirrors import recover
from download_russia import ROOT,BASE

SOURCES={
 'hse':('https://postypashki.ru/олимпиады/высшая-проба/',{2012,2013,2015,2017}),
 'phystech':('https://postypashki.ru/олимпиады/физтех/',{2022}),
 'lomonosov':('https://postypashki.ru/олимпиады/ломоносов/',{2009,2010,2013,2016,2018,2022,2023,2026}),
}

if __name__=='__main__':
    for cid,(page,years) in SOURCES.items():
        cache='research/international_cache/round5/'+hashlib.sha256(page.encode()).hexdigest()
        recover(cid,page,years,solutions_only=True,source_cache=cache)
        p=BASE/cid/'manifest.json';m=json.loads(p.read_text());m['round5_solution_source']=page;p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
