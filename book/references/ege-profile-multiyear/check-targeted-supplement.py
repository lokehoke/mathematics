#!/usr/bin/env python3
"""Independent exact enumeration and coordinate checks for residual methods.

Not a universal exam-coverage test. Coordinates independently verify author-created
examples and exercises; analytical proofs in the fragment cover continuous cases.
"""
import hashlib,itertools,json,math
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
checks=0
sections={}
def ok(v,msg):
 global checks
 checks+=1
 if not v: raise AssertionError(msg)
def norm2(v,delta=1): return v[0]*v[0]+delta*v[1]*v[1]
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def mul(k,a): return (k*a[0],k*a[1])
def dot(a,b,delta=1): return a[0]*b[0]+delta*a[1]*b[1]
def cross(a,b): return a[0]*b[1]-a[1]*b[0]
def dist2(a,b,d=1): return norm2(sub(a,b),d)
def rational(v): return [str(x) for x in v]

# Deliberately enumerate every permutation, not modular cases from the solution.
digit_results=[]
for ds,expected in [((0,1,2,3,5,7,9),10035),((0,1,3,4,5,6,8),9045)]:
 valid=[]
 for p in itertools.permutations(ds):
  checks+=1
  if p[0]==0 or p[4]==0: continue
  a=int(''.join(map(str,p[:4]))); b=int(''.join(map(str,p[4:])))
  if a%45==0 and b%45==0: valid.append((a+b,a,b))
 mx=max(v[0] for v in valid)
 ok(mx==expected,'digit maximum')
 maxima=[(a,b) for s,a,b in valid if s==mx]
 ok(any(s==2205 for s,a,b in valid),'required sum 2205 is attainable')
 ok(not any(s==3435 for s,a,b in valid) if ds[2]==2 else not any(s==4500 for s,a,b in valid),'forbidden sum is unattainable')
 for a,b in maxima:
  ok(sorted(map(int,str(a)+str(b)))==list(ds),'all original digits exactly once')
  ok(1000<=a<=9999 and 100<=b<=999,'number lengths')
 digit_results.append({'digits':ds,'permutations_checked':math.factorial(7),'admissible_pairs':len(valid),'maximum_sum':mx,'maximizers':maxima})
sections['digits']=digit_results

# Exhaust all ordered positive INTEGER configurations as a separate finite check.
# The proof in the book establishes stronger bounds over positive REAL values.
def partitions(n,k,lo=1):
 if k==0:
  if n==0: yield ()
  return
 for v in range(lo,n//k+1):
  for tail in partitions(n-v,k-1,v): yield (v,)+tail
seq_results=[]
for S,T,bounds in [(18,30,(38,42)),(24,36,(48,52))]:
 vals=[];witnesses={}
 for head in partitions(S,6):
  K=head[4]+head[5]
  for tail in partitions(T-K,4,head[-1]):
   seq=head+tail; u=sum(seq)
   ok(sum(seq[:6])==S and sum(seq[-6:])==T,'ordered partial sums')
   ok(all(0<seq[i]<=seq[i+1] for i in range(9)),'positive nondecreasing')
   ok(S<=5*seq[4]+seq[5]<=3*K,'lower K bound')
   ok(T>=seq[4]+5*seq[5]>=3*K,'upper K bound')
   vals.append(u);witnesses.setdefault(u,seq)
 ok((min(vals),max(vals))==bounds,'overlap extrema')
 seq_results.append({'six_smallest_sum':S,'six_largest_sum':T,'integer_configurations_exhausted':len(vals),'real_bounds_proved':bounds,'minimum_integer_witness':witnesses[min(vals)],'maximum_integer_witness':witnesses[max(vals)]})
sections['overlapping_sixes']=seq_results

def strictparts(n,k,lo=1):
 if k==0:
  if n==0: yield ()
  return
 for v in range(lo,(n-k*(k-1)//2)//k+1):
  for tail in strictparts(n-v,k-1,v+1): yield (v,)+tail
strict_results=[]
for S,T,umax,a1,mean in [(36,96,115,4,12),(42,102,125,5,13)]:
 count=0;foundmax=0;best=None;canmin=False;canmean=False;minK=10**9
 for head in strictparts(S,6):
  K=head[4]+head[5]
  for tail in strictparts(T-K,4,head[-1]+1):
   count+=1;seq=head+tail;u=sum(seq)
   ok(sum(seq[:6])==S and sum(seq[-6:])==T,'strict ordered partial sums')
   ok(all(0<seq[i]<seq[i+1] for i in range(9)),'positive strictly increasing integers')
   ok(u<=umax,'strict overlap upper bound')
   if u>foundmax:foundmax=u;best=seq
   minK=min(minK,K);canmin |= seq[0]==a1;canmean |= u==10*mean
 ok(foundmax==umax and not canmin and not canmean,'three parts of strict overlap example')
 strict_results.append({'six_smallest_sum':S,'six_largest_sum':T,'strict_integer_configurations_exhausted':count,'minimum_overlap_sum':minK,'maximum_total':foundmax,'maximum_mean':str(F(foundmax,10)),'maximizing_witness':best,'tested_smallest':a1,'tested_smallest_possible':canmin,'tested_mean':mean,'tested_mean_possible':canmean})
sections['distinct_natural_overlapping_sixes']=strict_results

# Exact rational geometry checks. In pentagons y means its coefficient of sqrt(D).
geometry=[]
for R,r,expect in [(9,4,F(432,13)),(16,9,F(3456,25))]:
 L=2*math.isqrt(R*r);ok(L*L==4*R*r,'integer tangent length chosen')
 A=(F(0),F(0));B=(F(L),F(0));O1=(F(0),F(R));O2=(F(L),F(r));K=(F(R*L,R+r),F(2*R*r,R+r));M=(F(L,2),F(0));D=(F(0),F(2*R));C=(F(L),F(2*r))
 ok(dist2(O1,O2)==(R+r)**2,'external circle tangency')
 ok(dist2(K,O1)==R*R and dist2(K,O2)==r*r,'K on both circles')
 ok(dist2(M,A)==dist2(M,B)==dist2(M,K),'equal tangent segments')
 ok(dot(sub(K,M),sub(O2,O1))==0,'line MK is common tangent')
 ok(dot(sub(A,K),sub(B,K))==0,'AKB right angle')
 ok(cross(sub(B,K),sub(D,K))==0,'D on BK')
 ok(cross(sub(A,K),sub(C,K))==0,'C on AK')
 ok(cross(sub(D,A),sub(C,B))==0,'diameters parallel')
 area=abs(cross(sub(B,A),sub(K,A)))/2
 ok(area==expect,'circle triangle area')
 geometry.append({'family':'two_externally_tangent_circles','R':R,'r':r,'K':rational(K),'area':str(area)})
for p,q,d,expected in [(2,3,1,F(7,2)),(3,4,1,F(13,3))]:
 delta=4*p*p-d*d
 A=(-F(d),F(0)); B=(-F(d,2),F(1,2)); C=(F(q)-F(d,2),F(1,2));D=(F(q),F(0));E=(F(q*d*d,2*p*p),-F(q*d,2*p*p));M=(F(0),F(0))
 center=(F(q-d,2),F(2*p*p-d*d-q*d,2*delta))
 rad2=dist2(A,center,delta)
 for V in [B,C,D,E]:ok(dist2(V,center,delta)==rad2,'five vertices on one circle')
 ok(dist2(A,B,delta)==dist2(C,D,delta)==p*p,'equal p chords')
 ok(dist2(B,C,delta)==dist2(D,E,delta)==q*q,'equal q chords')
 ok(dist2(A,D,delta)==(q+d)**2,'AD prescribed')
 ok(dist2(B,E,delta)==expected**2,'pentagon BE')
 ok(dist2(A,C,delta)==dist2(B,D,delta)==dist2(C,E,delta),'three equal diagonals')
 vs=[A,B,C,D,E]
 for i in range(5):ok(cross(sub(vs[(i+1)%5],vs[i]),sub(vs[(i+2)%5],vs[(i+1)%5]))<0,'strictly convex cyclic vertex order')
 ok(cross(sub(B,M),sub(E,M))==0 and dot(B,E,delta)<0,'M internal to BE')
 ok(A[0]<0<D[0],'M internal to AD')
 geometry.append({'family':'cyclic_pentagon','AB_CD':p,'BC_DE':q,'AD':q+d,'BE':str(expected),'y_unit':f'sqrt({delta})','vertices':{k:rational(v) for k,v in zip('ABCDE',vs)},'center':rational(center),'radius_squared':str(rad2)})
for p,h,s,areaexp,len2 in [(3,4,5,F(3,2),17),(5,12,13,F(35,2),193)]:
 A=(F(0),F(0));B=(F(p),F(h));P=(F(p),F(0));M=(F(h),F(0));D=(F(s*s,h),F(0));C=add(D,B);Q=(F(p+h),F(h-p))
 ok(dist2(A,B)==s*s and h*h+p*p==s*s,'right side triangle')
 ok(dot(sub(B,Q),sub(C,D))==0,'BQ perpendicular CD')
 ok(cross(sub(Q,D),sub(C,D))==0,'Q on CD line')
 t=F(h-p,h);ok(0<t<1 and Q==add(D,mul(t,sub(C,D))),'Q inside segment CD')
 ok(dist2(B,Q)==s*s,'BQ equals AB')
 ok(dist2(B,M)==dist2(P,Q)==len2,'BM equals PQ')
 ok(abs(cross(sub(P,A),sub(Q,A)))/2==areaexp,'APQ area')
 geometry.append({'family':'two_parallelogram_altitudes','AP':p,'BP':h,'AB':s,'D':rational(D),'Q':rational(Q),'BM_PQ_squared':len2,'APQ_area':str(areaexp)})
for a,b,exp2 in [(3,4,F(436,25)),(5,12,F(148))]:
 A=(F(0),F(a));B=(F(b),F(0));C=(F(0),F(0));M=(F(b,2),F(a,2));N=(F(b,2),F(0));K=(F(b,4),F(0));P=(F(3*b,8),F(a,4));T=(F(0),F(2*a,5))
 ok(dist2(A,N)==4*dist2(K,M),'AN equals twice KM')
 ok(P==add(A,mul(F(3,4),sub(N,A))),'P on AN')
 ok(P==add(K,mul(F(1,2),sub(M,K))),'P on KM')
 ok(cross(sub(P,B),sub(T,B))==0,'BPT collinear')
 ok(T[0]==0 and 0<T[1]<a,'T internal to AC')
 ok(0<P[0]/b+P[1]/a<1 and P[0]>0 and P[1]>0,'P strictly inside ABC')
 ok(dist2(B,T)==exp2,'full trace BT length')
 geometry.append({'family':'median_configuration_and_trace','AC':a,'BC':b,'P':rational(P),'T':rational(T),'trace_length_squared':str(exp2)})
for q,h,side2 in [(4,7,65),(5,12,169)]:
 A=(-F(q),F(0));B=(F(0),F(h));C=(F(q),F(0));O=(F(0),F(q));M=(F(0),F(0));AB=sub(B,A);H=add(A,mul(F(2*q*q,side2),AB))
 ok(side2==q*q+h*h,'isosceles side squared')
 ok(0<q<h,'all original angles acute')
 ok(dot(sub(C,H),AB)==0,'CH is altitude')
 radius2=F(q*q*(h-q)*(h-q),side2)
 # Distances to AB, BC, CH by line coefficients; common squared denominator s^2.
 for num in [h*O[0]-q*O[1]+h*q,h*O[0]+q*O[1]-h*q,q*O[0]+h*O[1]-q*q]:ok(num*num/F(side2)==radius2,'circle distances to three side lines')
 # Orthogonal feet to every segment are inside that segment, so this is the incircle.
 for X,Y in [(B,H),(B,C),(H,C)]:
  v=sub(Y,X);t=dot(sub(O,X),v)/norm2(v)
  ok(0<t<1,'tangency on side segment')
 ok(sub(O,A)[0]==sub(O,A)[1],'OAC is 45 degrees')
 ok(dot(sub(A,O),sub(C,O))==0,'AOC is right')
 ok(dist2(B,O)==(h-q)**2 and dist2(O,M)==q*q,'BO and OM')
 geometry.append({'family':'incircle_by_isosceles_altitude','AC':2*q,'BO':h-q,'BC_squared':side2,'center':rational(O),'altitude_foot_H':rational(H),'radius_squared':str(radius2)})
sections['geometry']=geometry

# Exact polynomial coefficient identity plus root branch counts on a rational grid.
def conv(a,b):
 out=[F(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):out[i+j]+=x*y
 return out
def ev(poly,x):
 out=F(0)
 for c in reversed(poly):out=out*x+c
 return out
def countroots(a,k,c):
 rs=[float(k)]
 if a:rs.append(float(F(c)/a))
 v=1-a*a
 if v>=0:
  r=math.sqrt(float(v));rs.extend([r,-r])
 distinct=[]
 for r in rs:
  if all(abs(r-t)>1e-8 for t in distinct):distinct.append(r)
 return len(distinct)
poly=[]
grid=sorted({F(i,97) for i in range(-6*97,6*97+1)}|{F(-4),F(-2),F(-1),F(0),F(1),F(3,2)})
for name,k,c,expected in [('2027-demo19.2',-1,2,lambda a:(abs(a)>1 and a!=-2) or a==0),('existing-worked-example',2,3,lambda a:abs(a)>1 and a!=F(3,2)),('targeted-independent-exercise',-1,4,lambda a:(abs(a)>1 and a!=-4) or a==0)]:
 for a in grid:
  Q=[-c*(a*a-1),a*(a*a-1),-c,a]
  expanded=conv([-k,1],Q)
  factored=conv(conv([-k,1],[-c,a]),[a*a-1,0,1])
  ok(expanded==factored,'independent coefficient factorization')
  ok(ev(expanded,F(k))==0,'constant branch solves expanded equation')
  if a:ok(ev(expanded,F(c)/a)==0,'linear branch solves expanded equation')
  ok((countroots(a,k,c)==2)==expected(a),'all critical/interval root counts')
 poly.append({'name':name,'constant_root':k,'linear_numerator':c,'rational_parameter_values_checked':len(grid),'critical_counts':{str(a):countroots(a,k,c) for a in [F(-4),F(-2),F(-1),F(0),F(1),F(3,2)]}})
sections['polynomials']=poly
path=ROOT/'book/source/data/review-ege-targeted.json';data=json.loads(path.read_text())
uids=[t['uid'] for v in data.values() for t in v['tasks']]
ok(len(uids)==len(set(uids)),'unique task UIDs')
for chap,v in data.items():
 ok(v['theory'].count('\\begin{example}')==v['theory'].count('\\end{example}'),'balanced example environments')
 for t in v['tasks']:ok(bool(t['q']) and bool(t['a']) and isinstance(t['hard'],bool),'complete task format')
result={'checked_at':'2026-10-25','status':'passed','checks':checks,'supplement_path':str(path.relative_to(ROOT)),'supplement_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'examples':sum(v['theory'].count('\\begin{example}') for v in data.values()),'tasks':len(uids),'task_uids':uids,'scope':'Exact author-example validation and finite exhaustive checks; no claim that every possible EGE task is covered.','results':sections}
out=ROOT/'book/references/ege-profile-multiyear/targeted-checks.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASSED',checks,'checks;',len(uids),'tasks;',result['examples'],'examples')
print(out)
