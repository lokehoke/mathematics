"""Copy an unmodified native ImageGen output and record its prompt/provenance."""
from pathlib import Path
import sys,json,shutil
from PIL import Image
p=Path(__file__).resolve().parents[1]/'sources/book/images/unique'
art=int(sys.argv[1]);source=Path(sys.argv[2])
item=next(v for v in json.loads((p/'prompts-exam-2027.json').read_text())if v['art']==art)
im=Image.open(source)
assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
target=p/f'art-{art:02}.png'
assert not target.exists(),target
shutil.copyfile(source,target)
item.update(path=str(target.relative_to(p.parents[3])),source=str(source),tool='builtin image_gen',transparent_background=True)
(p/f'generation-{art}.json').write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n')
print(art)
