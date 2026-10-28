"""Publish a validated raw book PDF atomically, preserving the last reading copy."""
from pathlib import Path
from collections import Counter
import argparse,shutil,subprocess,sys,json,hashlib,tempfile
import pdfplumber
ROOT=Path(__file__).resolve().parents[2];BOOK=ROOT/'book/source'

def publish(skip_optimize=False,prepared=None):
 with tempfile.TemporaryDirectory(prefix='.algebra-build-',dir=ROOT/'rendered')as temp_dir:
  report=ROOT/'book/references/book-flow-layout-check.json'
  source_sha=hashlib.sha256((BOOK/'main.pdf').read_bytes()).hexdigest()
  target=ROOT/'rendered/algebra-for-beloved-kitten.pdf'
  reading_candidate=Path(temp_dir)/target.name
  gs=shutil.which('gs')
  if prepared:
      shutil.copyfile(prepared,reading_candidate)
  elif gs and not skip_optimize:
      # Only the reading copy is downsampled. Original transparent artwork stays
      # untouched, and text, mathematics and plots retain vector representation.
      subprocess.run([gs,'-q','-dNOPAUSE','-dBATCH','-sDEVICE=pdfwrite',
          '-dCompatibilityLevel=1.5','-dDownsampleColorImages=true',
          '-dColorImageDownsampleType=/Bicubic','-dColorImageResolution=300',
          '-dDownsampleGrayImages=true','-dGrayImageDownsampleType=/Bicubic',
          '-dGrayImageResolution=300','-dAutoRotatePages=/None',
          '-dPreserveAnnots=true',f'-sOutputFile={reading_candidate}',str(BOOK/'main.pdf')],check=True)
  else:
      shutil.copyfile(BOOK/'main.pdf',reading_candidate)

  from restore_pdf_destinations import restore_destinations
  restored = restore_destinations(BOOK/'main.pdf', reading_candidate)
  print(f'Restored {restored} named navigation targets after PDF optimization')

  # PDF optimization must preserve every printed character on its original page.
  # Glyph ordering in extracted text can change after font subsetting, so compare
  # inventories rather than the extractor's reading order for display formulas.
  with pdfplumber.open(BOOK/'main.pdf') as original,pdfplumber.open(reading_candidate) as reading:
      assert len(original.pages)==len(reading.pages)
      for number,(a,b) in enumerate(zip(original.pages,reading.pages),1):
          inventory=lambda p:Counter(''.join(c['text'] for c in p.chars if c['text'].strip()))
          assert inventory(a)==inventory(b),f'Export changed characters on page {number}'
  assert hashlib.sha256((BOOK/'main.pdf').read_bytes()).hexdigest()==source_sha,'Raw PDF changed during export'
  data=json.loads(report.read_text())
  assert data.get('source_pdf_sha256')==source_sha,'Run the layout check against the current raw PDF first'
  assert not any(data[k]for k in ['text_art_overlaps','colored_box_art_overlaps','outside_content','exercise_label_anomalies','gaps_over_three_pages','orphaned_olympiad_blocks'])
  reading_candidate.replace(target)
  data.update(reading_pdf_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
      reading_pdf_bytes=target.stat().st_size,reading_pdf_character_inventories_preserved=True)
  report.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
  print(f'Published {target} ({target.stat().st_size:,} bytes)')

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--skip-optimize',action='store_true')
 parser.add_argument('--prepared',type=Path,help='Ghostscript reading candidate from the same raw PDF; every printed character is still verified')
 args=parser.parse_args()
 publish(args.skip_optimize,args.prepared)
