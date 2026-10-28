"""Independent numerical and exact-arithmetic checks of review-ege-depth.json."""
from pathlib import Path
import json,re,math,itertools,random,hashlib,collections
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[3]; src=ROOT/'book/source/data/review-ege-depth.json'; data=json.loads(src.read_text())
checks=collections.Counter()
def ck(group,condition):
 checks[group]+=1
 assert condition,(group,checks[group])
def near(a,b,tol=1e-9):return abs(a-b)<=tol*(1+abs(a)+abs(b))
# Structural checks: all IDs unique and all TeX delimiters/environments paired.
ids=[t['uid'] for c in data.values() for t in c['tasks']];ck('structure',len(ids)==39==len(set(ids)))
labels=[]
for c in data.values():
 for s in [c['theory']]+[t[k] for t in c['tasks'] for k in ['q','a']]:
  ck('structure',s.count(r'\(')==s.count(r'\)'));ck('structure',s.count(r'\[')==s.count(r'\]'))
  ck('structure',s.count('{')==s.count('}'))
  stack=[]
  for typ,env in re.findall(r'\\(begin|end)\{([^}]+)\}',s):
   if typ=='begin':stack.append(env)
   else:ck('structure',bool(stack) and stack.pop()==env)
  ck('structure',not stack)
  labels+=re.findall(r'\\label\{([^}]+)\}',s)
ck('structure',len(labels)==len(set(labels))==28)
# G1: direct enumeration of different intersections, independent from case descriptions.
def uniq(vals):
 out=[]
 for v in vals:
  if not any(near(v,x,1e-7) for x in out):out.append(v)
 return out
for a in [i/100 for i in range(-400,701)]+[0,1,4]:
 vals=[(a+2)/3]+([0] if a==0 else [math.sqrt(a),-math.sqrt(a)] if a>0 else [])
 ck('G1', (len(uniq(vals))==2)==(a in (0,1,4)))
 vals=[a]+([0] if a==0 else [math.sqrt(a),-math.sqrt(a)] if a>0 else [])
 ck('G1',(len(uniq(vals))==2)==(a==1))
for a in [i/100 for i in range(-250,251)]+[-1,1,math.sqrt(2)]:
 disc=2-a*a; roots=[]
 if disc>=-1e-12:
  for u in uniq([(a+math.sqrt(max(0,disc)))/2,(a-math.sqrt(max(0,disc)))/2]):
   if u>=-1e-10:
    u=max(u,0);roots += [(u,a-u)] if u<1e-8 else [(u,a-u),(-u,a-u)]
 n=0 if a<-1 or a>math.sqrt(2)+1e-12 else 1 if a==-1 else 3 if a==1 else 4 if 1<a<math.sqrt(2)-1e-12 else 2
 ck('G1',len(roots)==n)
 for x,y in roots:ck('G1',near(x*x+y*y,1) and near(y,a-abs(x)))
for a in [i/100 for i in range(-200,801)]:
 if 0<=a<=6:
  x=((math.sqrt(1+4*a)-1)/2)**2
  ck('G1',-1e-10<=x<=4+1e-10 and near(math.sqrt(x),a-x))
for a in [i/100 for i in range(-300,301)]+[1.5]:
 roots=[2]
 if a!=0:roots.append(3/a)
 if a*a<=1:roots += [math.sqrt(1-a*a),-math.sqrt(1-a*a)]
 expected=(abs(a)>1 and a!=1.5)
 ck('G1',(len(uniq(roots))==2)==expected)
# G2: combinatorial constructions, reverse transformations and digit optimum.
for start,end,steps in [((28,1),(116,108),5),((16,1),(68,60),5),((9,2),(72,16),6),((9,2),(88,56),7)]:
 a,b=start
 for _ in range(steps):a,b=a+b,a-b
 ck('G2',(a,b)==end)
nums=[1+12*i for i in range(9)]
for k in [4,6]:
 for subset in itertools.combinations(nums,k):ck('G2',sum(subset)%k==0)
nums=[2+15*i for i in range(8)]
for k in [3,5]:
 for subset in itertools.combinations(nums,k):ck('G2',sum(subset)%k==0)
sums={2*a+7*b+c for a in range(6) for b in range(5) for c in range(3)}
ck('G2',set(range(41))<=sums);ck('G2',2*5+7*4+1<40)
ck('G2',sum(list(range(12))+[15])==11*7+2*2==81)
ck('G2',14*13//2>7*14-10)
ck('G2',F(12-8,2)==2 and F(22+8,3)==10)
blues=list(range(-9,16,3)); reds=list(range(-10,19,2));ck('G2',len(blues)==9 and len(reds)==15 and max(blues)==len(reds) and max(reds)==2*len(blues))
bydigit=collections.defaultdict(list)
for n in range(1,200):bydigit[sum(map(int,str(n)))].append(n)
ck('G2',min(sum(v[:3]) for v in bydigit.values() if len(v)>=3)==33)
# G3: exact finance and mass balance.
x,y=F(27),F(21)
ck('G3',(F(1,5)*x+F(3,5)*y)/(x+y+12)==F(3,10))
ck('G3',(F(1,5)*x+F(3,5)*y+6)/(x+y+12)==F(2,5))
D=[300000,240000,120000,0];pay=[F(23,20)*a-b for a,b in zip(D,D[1:])]
ck('G3',pay==[105000,156000,138000] and sum(pay)==399000)
ck('G3',sum([F(51,50)*60000-30000,F(51,50)*30000])==61800)
D=F(210000)
for payment in [21000,21000,121000,121000]:D=F(11,10)*D-payment
ck('G3',D==0 and sum([21000,21000,121000,121000])==284000)
ck('G3',8*6-(F(1,2)*6**2+2*6+2)==16)
ck('G3',100*20**2+400*5**2==50000 and 20+5==25)
for i in range(1,2000):
 x=math.sqrt(50000/100)*i/2000;y=math.sqrt(max(0,(50000-100*x*x)/400));ck('G3',x+y<=25+1e-9)
# G4: exact point/function reconstruction and derivative signs.
ck('G4',2*(2+1)**2-3==15);ck('G4',F(-8,4)==-2);ck('G4',F(3)**(-1)==F(1,3));ck('G4',5**2-4*5==5)
ck('G4',F(0-3,4-(-2))==F(-1,2))
g=lambda x:F(1,10)*(x+2)*(x-1)**2*(x-3)
for x,sgn in [(-F(5,2),1),(-1,-1),(0,-1),(F(3,2),-1),(F(5,2),-1),(F(7,2),1)]:ck('G4',g(x)*sgn>0)
# G5: vector areas and lengths, independent from closed formulas.
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return math.sqrt(dot(a,a))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
h=2*math.sqrt(3);A1=(0,0,h);B=(6,0,0);M=(3,3*math.sqrt(3),h/2)
ck('G5',near(norm(sub(M,A1)),norm(sub(M,B))));ck('G5',near(norm(cross(sub(B,A1),sub(M,A1)))/2,18))
a=3;h=4*math.sqrt(2);M=(0,0,h/2);K=(a,a,h/2);B1=(a,0,h);D=(0,a,0)
ck('G5',near(norm(sub(M,B1)),norm(sub(M,D))))
ck('G5',near(norm(cross(sub(K,M),sub(D,B1)))/2,15))
ck('G5',near(120/17,2*(8*15/2)/17));ck('G5',near(13**2/12,169/12));ck('G5',near(math.sqrt(9**2-(9*math.sqrt(2)/2)**2),9*math.sqrt(2)/2))
ck('G5',F(2,3)*120==80 and F(4,9)*270==120)
# G6: sample whole positive domains logarithmically, compare to attained maxima.
P=lambda R:144*R/(R+3)**2; A=lambda t:3*t*t/math.sqrt((16-t*t)**2+4*t*t)
opt=math.sqrt(128/7);amax=24/math.sqrt(15)
ck('G6',near(P(3),12));ck('G6',near(A(opt),amax))
for i in range(20001):
 t=10**(-4+8*i/20000);ck('G6',P(t)<=12+1e-10);ck('G6',A(t)<=amax+1e-10)
fn=lambda x:(x-2)*math.cos(x)-math.sin(x)
for i in range(5001):
 x=math.pi*i/5000;ck('G6',-2-1e-10<=fn(x)<=-math.sin(2)+1e-10)
# G7: evaluate original inequalities on a dense grid, independently of sign-table answers.
for i in range(-20000,20001):
 x=i/1000
 if x<-2 or x>-1:
  val=math.log2(x*x+3)-math.log2(x*x+x+1)-math.log2((x+2)/(x+1))
  ans=x<-2 or -math.sqrt(2)/2<=x<=math.sqrt(2)/2
  if abs(val)>1e-9:ck('G7',(val>=0)==ans)
 if x>0 and not near(x,4):
  t=math.log2(x);v=(t*t-3*t+2)/(t/2-1);ans=x>=2 and not near(x,4)
  if abs(v)>1e-9:ck('G7',(v>=0)==ans)
 if x>1 and not near(x,2):
  v=math.log(x*x-4*x+5,x-1)-1
  if abs(v)>1e-9:ck('G7',(v>=0)==(x>=3))
 if abs(x)<8 and not near(x,1):
  t=3**x;v=(t*t-10*t+9)/(t-3)
  if abs(v)>1e-8:ck('G7',(v<=0)==(x<=0 or 1<x<=2))
 if x>2 and not near(x,3):
  v=math.log2(math.log(x-1,3))/(math.log2(x-1)-1)
  if abs(v)>1e-9:ck('G7',(v>=0)==(2<x<3 or x>=4))
 if abs(x)<8 and not near(x,F(2,3)):
  t=3**x;v=(t*t*t-12*t*t+48*t-64)/(3*x-2)**2
  if abs(v)>1e-8:ck('G7',(v<=0)==(x<=math.log(4,3)))
result={'checked_at':'2026-10-25','file':str(src.relative_to(ROOT)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'tasks':len(ids),'worked_examples':len(labels),'assertions':dict(checks),'total_assertions':sum(checks.values()),'result':'passed','limits':'Numerical sampling supplements the written proofs; it is not a substitute for proof or independent content review.'}
(ROOT/'book/references/ege-profile-multiyear/new-depth-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
