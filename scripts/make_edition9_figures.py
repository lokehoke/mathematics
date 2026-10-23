"""Vector diagrams for geometry, multivariable calculus and probability."""
from pathlib import Path
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle,Arc
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
OUT=Path(__file__).resolve().parents[1]/'sources/book/images'
N='#233f4a';T='#5a7b77';O='#ae7046';P='#fffcf6'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':P,'axes.facecolor':P,'savefig.bbox':'tight'})
def save(f,name):f.savefig(OUT/(name+'.pdf'));plt.close(f)
def axis(a,title):
 a.set_title(title,color=N,pad=12);a.grid(alpha=.16);a.axhline(0,lw=.6,color=N);a.axvline(0,lw=.6,color=N);a.set_xlabel('x');a.set_ylabel('y',rotation=0)
def arrow(a,p,q,color=T):a.annotate('',xy=q,xytext=p,arrowprops=dict(arrowstyle='->',lw=2,color=color))
x=np.linspace(-3,3,600)
f,aa=plt.subplots(2,2,figsize=(9,7),constrained_layout=True)
for a,title in zip(aa.flat,[r'$y=2^x$',r'$y=\log_2 x$',r'$y=e^x$',r'$y=\ln x$']):axis(a,title)
aa[0,0].plot(x,2**x,color=T);xx=np.linspace(.06,5,600);aa[0,1].plot(xx,np.log2(xx),color=O)
aa[1,0].plot(x,np.exp(x),color=T);aa[1,1].plot(xx,np.log(xx),color=O)
for a in aa.flat:a.set_ylim(-4,9)
save(f,'atlas-exponential-basic')
f,aa=plt.subplots(2,2,figsize=(9,7),constrained_layout=True)
for a,title in zip(aa.flat,[r'$y=\operatorname{sh}x$',r'$y=\operatorname{ch}x$',r'$y=\operatorname{th}x$',r'$y=\operatorname{cth}x$']):axis(a,title);a.set_xlim(-3,3)
aa[0,0].plot(x,np.sinh(x),color=T);aa[0,1].plot(x,np.cosh(x),color=O);aa[1,0].plot(x,np.tanh(x),color=T)
for l,r in [(-3,-.03),(.03,3)]:xx=np.linspace(l,r,400);aa[1,1].plot(xx,1/np.tanh(xx),color=O)
for a in aa[1]:
 for y in [-1,1]:a.axhline(y,color=N,ls='--',lw=.8)
 a.set_ylim(-3.5,3.5)
save(f,'atlas-hyperbolic-all')
f,aa=plt.subplots(2,2,figsize=(9,7),constrained_layout=True)
a=aa[0,0];a.set_title('Подобие: коэффициент 1/2',color=N)
for verts,col in [([(0,0),(4,0),(1,3)],T), ([(.5,1.5),(2.5,1.5),(1,3)],O)]:a.add_patch(Polygon(verts,fill=False,edgecolor=col,lw=2))
a.text(1.6,-.4,'4');a.text(1.5,1.65,'2');a.set_xlim(-.4,4.4);a.set_ylim(-.5,3.5)
a=aa[0,1];a.set_title('Вписанный угол и центральный',color=N);a.add_patch(Circle((0,0),1,fill=False,edgecolor=T,lw=2))
A=np.array([np.cos(.3),np.sin(.3)]);B=np.array([np.cos(1.7),np.sin(1.7)]);C=np.array([np.cos(3.8),np.sin(3.8)])
for v in [A,B]:a.plot([0,v[0]],[0,v[1]],color=O);a.plot([C[0],v[0]],[C[1],v[1]],color=N)
a.text(.05,.2,r'$2\alpha$',color=O);a.text(C[0]+.2,C[1]+.13,r'$\alpha$',color=N);a.set_xlim(-1.2,1.2);a.set_ylim(-1.2,1.2)
a=aa[1,0];a.set_title(r'$S=\frac{1}{2}ah$',color=N);a.add_patch(Polygon([(0,0),(4,0),(1,2.5)],fc=T,alpha=.25,ec=N));a.plot([1,1],[0,2.5],ls='--',color=O);a.text(1.08,1.1,'h');a.text(2,-.35,'a');a.set_xlim(-.5,4.5);a.set_ylim(-.5,3)
a=aa[1,1];a.set_title(r'$PA\cdot PB=PC\cdot PD$',color=N);a.add_patch(Circle((0,0),1,fill=False,ec=T,lw=2))
p=np.array([-2.,0.]);
for ang,labels in [(.15,('A','B')),(-.3,('C','D'))]:
 u=np.array([np.cos(ang),np.sin(ang)]);roots=np.sort(np.roots([1,2*p@u,p@p-1]));q=p+roots[1]*u;a.plot([*p[:1],q[0]],[p[1],q[1]],color=O);a.scatter(*(p+roots[0]*u),color=N,s=15);a.scatter(*q,color=N,s=15)
 for point,label in zip([p+roots[0]*u,q],labels):a.text(point[0]+.01,point[1]+(.12 if ang>0 else -.22),label,color=N,fontsize=10)
a.text(-2.15,.12,'P');a.set_xlim(-2.4,1.3);a.set_ylim(-1.2,1.2)
for a in aa.flat:a.set_aspect('equal');a.axis('off')
save(f,'atlas-plane-geometry')
f=plt.figure(figsize=(9,4.4),constrained_layout=True);a=f.add_subplot(121,projection='3d');b=f.add_subplot(122,projection='3d')
v=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[.5,.5,1.4]])
for k in range(4):
 j=(k+1)%4;a.plot(*v[[k,j]].T,color=N);a.plot(*v[[k,4]].T,color=N)
base=v[:4];cross=.5*base+.5*v[4];a.add_collection3d(Poly3DCollection([cross],facecolor=T,alpha=.6,edgecolor=O));a.set_title('Параллельное сечение: площадь × 1/4',fontsize=10,color=N)
z=np.linspace(-1,1,80);theta=np.linspace(0,2*np.pi,100);Z,TH=np.meshgrid(z,theta);rad=np.sqrt(1-Z*Z);b.plot_surface(rad*np.cos(TH),rad*np.sin(TH),Z,color=T,alpha=.2,linewidth=0)
r=np.sqrt(1-.4**2);b.plot(r*np.cos(theta),r*np.sin(theta),np.full_like(theta,.4),color=O,lw=2);b.set_title(r'Сечение шара: $\pi(R^2-z^2)$',color=N)
for a in [a,b]:a.set_box_aspect((1,1,1));a.set_xlabel('x');a.set_ylabel('y');a.set_zlabel('z')
from matplotlib.ticker import FormatStrFormatter
pyramid,sphere=f.axes
pyramid.set_xticks([0,.5,1]);pyramid.set_yticks([0,.5,1]);pyramid.set_zticks([0,.7,1.4])
sphere.set_xticks([-1,0,1]);sphere.set_yticks([-1,0,1]);sphere.set_zticks([-1,0,1])
for pane in [pyramid,sphere]:
 for dimension in [pane.xaxis,pane.yaxis,pane.zaxis]:dimension.set_major_formatter(FormatStrFormatter('%g'))
save(f,'atlas-solid-geometry')
f=plt.figure(figsize=(9,4.5),constrained_layout=True);a=f.add_subplot(121);b=f.add_subplot(122,projection='3d')
x=np.linspace(-2,2,100);X,Y=np.meshgrid(x,x);a.contour(X,Y,X*X+Y*Y,levels=[.5,1,2,3,4,5],colors=T);arrow(a,(.5,.5),(1.5,1.5),O);a.scatter([.5],[.5],color=N);a.text(.15,1.75,r'$\nabla f=(2x,2y)$',color=O);a.set_title(r'Линии уровня $f=x^2+y^2$',color=N);a.set_aspect('equal');a.set_xlabel('x');a.set_ylabel('y')
b.plot_surface(X,Y,X*X+Y*Y,color=T,alpha=.45,linewidth=0);b.plot_surface(X,Y,2*X+2*Y-2,color=O,alpha=.25);b.scatter([1],[1],[2],color=N);b.set_title('График и касательная плоскость',color=N);b.set_xlabel('x');b.set_ylabel('y');b.set_zlabel('z')
save(f,'atlas-multivariable')
f,aa=plt.subplots(1,2,figsize=(9,4.2),constrained_layout=True);a,b=aa
xx=np.linspace(0,1,200);a.fill_between(xx,xx,1,color=T,alpha=.25);a.plot(xx,xx,color=N);a.plot([0,1],[1,1],color=N)
for t in np.arange(.15,1,.2):a.plot([t,t],[t,1],color=O,lw=1)
axis(a,r'$0\leq x\leq y\leq1$');a.set_xlim(-.1,1.1);a.set_ylim(-.1,1.1);a.set_aspect('equal')
for r in [.25,.5,.75,1]:b.add_patch(Circle((0,0),r,fill=False,ec=T,alpha=.6))
for th in np.arange(0,2*np.pi,np.pi/6):b.plot([0,np.cos(th)],[0,np.sin(th)],color=T,alpha=.5)
b.add_patch(Polygon([(0,0),(.7,0),(.7*np.cos(.3),.7*np.sin(.3))],fc=O,alpha=.5));axis(b,r'$dA=r\,dr\,d\theta$');b.set_xlim(-1.1,1.1);b.set_ylim(-1.1,1.1);b.set_aspect('equal')
save(f,'atlas-multiple-integrals')
f,aa=plt.subplots(1,2,figsize=(9,4.3),constrained_layout=True);a,b=aa;t=np.linspace(0,2*np.pi,300);a.plot(np.cos(t),np.sin(t),color=T,lw=2)
for th in [0,np.pi/2,np.pi,3*np.pi/2]:arrow(a,(np.cos(th),np.sin(th)),(np.cos(th)-.4*np.sin(th),np.sin(th)+.4*np.cos(th)),O)
axis(a,r'$F=(-y,x)$: положительная циркуляция');a.set_xlim(-1.6,1.6);a.set_ylim(-1.6,1.6);a.set_aspect('equal')
b.plot([-1,1],[0,0],color=T,lw=4);b.plot([-1,1],[.05,.05],color=T,lw=.7)
for xx in np.linspace(-.8,.8,5):arrow(b,(xx,-.6),(xx,.8),O)
arrow(b,(.3,0),(.3,1.2),N);b.text(.4,1.05,'n');b.text(-.9,-1.05,r'$F\cdot n>0$',color=O);b.set_title('Поток через поверхность',color=N);b.set_xlim(-1.4,1.4);b.set_ylim(-1.3,1.4);b.axis('off')
save(f,'atlas-line-surface')
f,a=plt.subplots(figsize=(9,4.5),constrained_layout=True);a.axis('off');a.set_xlim(0,1);a.set_ylim(0,1)
pts=[(.04,.5),(.4,.76),(.4,.24),(.85,.9),(.85,.63),(.85,.37),(.85,.1)]
for i,j,label in [(0,1,'1/3'),(0,2,'2/3'),(1,3,'3/4'),(1,4,'1/4'),(2,5,'1/4'),(2,6,'3/4')]:
 p,q=pts[i],pts[j];a.plot([p[0],q[0]],[p[1],q[1]],color=T if j in [1,3,5]else O,lw=1.5);a.text((p[0]+q[0])/2,(p[1]+q[1])/2+.03,label,color=N)
for i,text in [(0,'Выбор'),(1,'Мешок 1'),(2,'Мешок 2'),(3,'Красный: 1/4'),(4,'Синий: 1/12'),(5,'Красный: 1/6'),(6,'Синий: 1/2')]:a.text(*pts[i],text,ha='center',va='center',bbox=dict(fc=P,ec='none',pad=3),color=N)
a.set_title(r'Полная вероятность красного: $\frac{1}{4}+\frac{1}{6}=\frac{5}{12}$',color=N,pad=15)
save(f,'atlas-probability')
f,aa=plt.subplots(2,2,figsize=(9,7),constrained_layout=True);a,b,c,d=aa.flat
ks=np.arange(11);pm=np.array([math.comb(10,int(k))*.2**k*.8**(10-k)for k in ks]);a.bar(ks,pm,color=T);a.set_title(r'$X\sim\operatorname{Bin}(10,0.2)$',color=N);a.set_ylabel('Вероятность');a.set_xticks(range(0,11,2))
x=np.linspace(-4,4,500);den=np.exp(-x*x/2)/np.sqrt(2*np.pi);b.plot(x,den,color=T);b.fill_between(x,0,den,where=abs(x)<=1,color=O,alpha=.35);b.set_title('Нормальная плотность',color=N)
c.step(np.r_[-1,ks,12],np.r_[0,np.cumsum(pm),1],where='post',color=T);c.set_title('Дискретная функция распределения',color=N);c.set_ylim(-.03,1.05)
y=np.linspace(0,5,400);d.plot(y,1-np.exp(-y),color=O);d.set_title(r'$F(x)=1-e^{-x}$ при $x\geq0$',color=N);d.set_ylim(-.03,1.05)
for a in aa.flat:a.grid(alpha=.17);a.set_xlabel('x')
save(f,'atlas-random-variables')
f,aa=plt.subplots(1,2,figsize=(9,4.3),constrained_layout=True);a,b=aa
xx=np.array([0,1,2]);yy=np.array([1,2,2]);a.scatter(xx,yy,color=O,s=50,zorder=3);xs=np.linspace(-.2,2.2,100);a.plot(xs,7/6+.5*xs,color=T);a.set_title(r'$\widehat y=\frac{7}{6}+\frac{1}{2}x$',color=N);a.set_xlabel('x');a.set_ylabel('y');a.grid(alpha=.2)
# Schematic repeated 95% intervals, deterministic and explicitly illustrative.
centers=np.array([.15,-.4,.5,-.2,1.25,.1,-.55,.35]);width=.9
for j,m in enumerate(centers):b.plot([m-width,m+width],[j,j],color=O if abs(m)>width else T,lw=2);b.scatter([m],[j],s=18,color=N)
b.axvline(0,color=N,ls='--');b.set_title('Повторные интервалы: схема покрытия',color=N);b.set_xlabel('Неизвестное среднее (пунктир)');b.set_yticks([]);b.invert_yaxis()
save(f,'atlas-statistics')
print('Wrote 10 vector atlases')
