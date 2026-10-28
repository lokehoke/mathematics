"""Checks of the corrected visual transcription: 7|x|+1 (the +1 is outside)."""
from pathlib import Path
import json,math,re,hashlib
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'book/references/ege-profile-multiyear';src=ROOT/'book/source/data/review-ege-last-gap.json';data=json.loads(src.read_text());checks=0
def ck(c):
 global checks;checks+=1;assert c,checks
uids=[t['uid'] for c in data.values() for t in c['tasks']];ck(len(uids)==4==len(set(uids)));ck('c20' not in data)
for c in data.values():
 for s in [c['theory']]+[t[k] for t in c['tasks'] for k in ['q','a']]:
  ck(s.count('{')==s.count('}'));ck(s.count(r'\(')==s.count(r'\)'));ck(s.count(r'\[')==s.count(r'\]'));stack=[]
  for typ,env in re.findall(r'\\(begin|end)\{([^}]+)\}',s):
   if typ=='begin':stack.append(env)
   else:ck(stack.pop()==env)
  ck(not stack)
ck('7|x|+1=8y' in data['exam-parameters']['theory'])
ck('7|x+1|' not in data['exam-parameters']['theory'].split(r'\end{cases}')[0])
# Same proof is checked for the original and two independently authored analogues.
results=[]
for base,A,C,D in [(2,8,7,1),(3,9,5,2),(2,4,2,3)]:
 B=A*(base-1);amin=A+D-B;other=A+D+B
 F=lambda x,y:A*base**abs(x)+C*abs(x)+D-C*x*x-B*y
 ck(F(0,1)==amin);ck(F(0,-1)==other);ck(F(1,0)==other);ck(F(-1,0)==other)
 # Every circle point has F-amin=A(base^u-1)+Cu(1-u)+B(1-y), all nonnegative.
 minseen=float('inf');N=100000
 for i in range(N):
  th=2*math.pi*i/N;x,y=math.cos(th),math.sin(th);u=abs(x)
  residual=F(x,y)-amin;decomp=A*(base**u-1)+C*u*(1-u)+B*(1-y)
  ck(abs(residual-decomp)<1e-11);ck(residual>=-1e-11)
  ck(abs(F(x,y)-F(-x,y))<1e-12)
  minseen=min(minseen,F(x,y))
 # Positive-u terms are strict, so the sum can vanish only at u=0,y=1.
 for k in range(1,10001):
  u=k/10000;ck(A*(base**u-1)>0);ck(C*u*(1-u)>=-1e-12)
 results.append({'base':base,'A':A,'coefficient_abs':C,'constant':D,'coefficient_y':B,'unique_parameter':amin,'unique_pair':[0,1],'rejected_candidate':other,'three_rejection_witnesses':[[0,-1],[1,0],[-1,0]],'circle_samples':N,'sampled_min':minseen})
temps=[-6,-4,1,8,15,19,22,20,14,7,0,-3]
ck(sum(t>=19 for t in temps)==3);ck(sum(t>0 for t in temps)==8);ck(temps.index(0)+1==11)
ck(sum(t<0 for t in temps)==3);ck(sum(t>18 for t in temps)==3);ck(temps.index(15)+1==5)
ck(12/(1+1)==6 and 12/(3+1)==3 and 3-1==2 and 3/1==3)
figure=ROOT/'book/source/images/review-ege-data-reading.pdf';ck(figure.exists())
evidence=P/'2026-open/task18-evidence.json';ev=json.loads(evidence.read_text());ck(ev['physical_pdf_page']==4);ck('7|x|+1=' in ev['transcription'])
res={'checked_at':'2026-10-25','source':str(src.relative_to(ROOT)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'tasks':len(uids),'assertions':checks,'systems':results,'source_evidence':str(evidence.relative_to(ROOT)),'figure_sha256':hashlib.sha256(figure.read_bytes()).hexdigest(),'result':'passed','correction':'The earlier non-elementary numerical solution referred to a misread different expression7|x+1|. It is withdrawn as a solution of the official task. The official pixels show7|x|+1; the exact answer is a=1, obtained by symmetry and a sum of nonnegative terms, without derivatives.'}
(P/'last-gap-checks.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False,indent=2))
