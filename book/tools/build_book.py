"""Assemble, compile, check and publish the textbook PDF from the repository."""
from pathlib import Path
from collections import Counter
import argparse,shutil,subprocess,sys,json,hashlib,re
import pdfplumber

ROOT=Path(__file__).resolve().parents[2]
BOOK=ROOT/'book/source'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tectonic',default='tectonic')
parser.add_argument('--skip-optimize',action='store_true')
args=parser.parse_args()

subprocess.run([sys.executable,str(ROOT/'book/tools/make_symbols.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'book/tools/assemble_book.py')],check=True)
subprocess.run([args.tectonic,'--keep-logs','--keep-intermediates','main.tex'],cwd=BOOK,check=True)
log=(BOOK/'main.log').read_text()
assert not re.search(r'Overfull|Undefined control sequence|undefined references|Missing character',log,re.I), 'Fix TeX layout, unresolved references or missing glyphs before publishing'
subprocess.run([sys.executable,str(ROOT/'book/tools/verify_book_layout.py')],check=True)
from publish_book import publish
publish(args.skip_optimize)
