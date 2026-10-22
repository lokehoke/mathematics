"""Assemble, compile, check and publish the textbook PDF from the repository."""
from pathlib import Path
from collections import Counter
import argparse,shutil,subprocess,sys,json,hashlib
import pdfplumber

ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT/'sources/book'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tectonic',default='tectonic')
parser.add_argument('--skip-optimize',action='store_true')
args=parser.parse_args()

subprocess.run([sys.executable,str(ROOT/'scripts/make_symbols.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/assemble_book.py')],check=True)
subprocess.run([args.tectonic,'--keep-logs','--keep-intermediates','main.tex'],cwd=BOOK,check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/verify_book_layout.py')],check=True)
target=ROOT/'rendered/algebra-for-beloved-kitten.pdf'
gs=shutil.which('gs')
if gs and not args.skip_optimize:
    # Only the reading copy is downsampled. Original transparent artwork stays
    # untouched, and text, mathematics and plots retain vector representation.
    subprocess.run([gs,'-q','-dNOPAUSE','-dBATCH','-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.5','-dDownsampleColorImages=true',
        '-dColorImageDownsampleType=/Bicubic','-dColorImageResolution=300',
        '-dDownsampleGrayImages=true','-dGrayImageDownsampleType=/Bicubic',
        '-dGrayImageResolution=300','-dAutoRotatePages=/None',
        '-dPreserveAnnots=true',f'-sOutputFile={target}',str(BOOK/'main.pdf')],check=True)
else:
    shutil.copyfile(BOOK/'main.pdf',target)

# PDF optimization must preserve every printed character on its original page.
# Glyph ordering in extracted text can change after font subsetting, so compare
# inventories rather than the extractor's reading order for display formulas.
with pdfplumber.open(BOOK/'main.pdf') as original,pdfplumber.open(target) as reading:
    assert len(original.pages)==len(reading.pages)
    for number,(a,b) in enumerate(zip(original.pages,reading.pages),1):
        inventory=lambda p:Counter(''.join(c['text'] for c in p.chars if c['text'].strip()))
        assert inventory(a)==inventory(b),f'Export changed characters on page {number}'
report=ROOT/'research/book-flow-layout-check.json'
data=json.loads(report.read_text())
data.update(reading_pdf_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
    reading_pdf_bytes=target.stat().st_size,reading_pdf_character_inventories_preserved=True)
report.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(f'Published {target} ({target.stat().st_size:,} bytes)')
