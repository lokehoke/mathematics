"""Reproducible vector figures for cotangent and chapters 26–30."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle

OUT=Path(__file__).resolve().parents[2]/'book/source/images'
NAVY='#233f4a';TEAL='#5a7b77';OCHRE='#ae7046';PAPER='#fffcf6'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
 'axes.titlesize':13,'axes.spines.top':False,'axes.spines.right':False,
 'figure.facecolor':PAPER,'axes.facecolor':PAPER,'savefig.bbox':'tight'})
def axes(ax,title,xlim,ylim):
 ax.set_title(title,color=NAVY,pad=13);ax.set_xlim(*xlim);ax.set_ylim(*ylim)
 ax.grid(alpha=.17);ax.axhline(0,lw=.7,color=NAVY);ax.axvline(0,lw=.7,color=NAVY)
 ax.set_xlabel('x',loc='right');ax.set_ylabel('y',rotation=0,loc='top')
def save(fig,name):fig.savefig(OUT/name);plt.close(fig)
def arrow(ax,v,color,label,origin=(0,0),offset=(.08,.08)):
 ax.annotate('',xy=np.array(origin)+v,xytext=origin,
  arrowprops=dict(arrowstyle='->',lw=2,color=color))
 p=np.array(origin)+v+offset;ax.text(*p,label,color=color)

fig,ax=plt.subplots(figsize=(9.6,4.1),constrained_layout=True)
axes(ax,r'$y=\operatorname{ctg}x$',(-3*np.pi,3*np.pi),(-4.5,4.5))
for k in range(-3,3):
 x=np.linspace(k*np.pi+.025,(k+1)*np.pi-.025,800)
 ax.plot(x,1/np.tan(x),color=TEAL,lw=1.8)
for k in range(-3,4):ax.axvline(k*np.pi,color=OCHRE,lw=.8,ls='--',alpha=.7)
ax.set_xticks(np.arange(-6,7)*np.pi/2)
ax.set_xticklabels([r'$-3\pi$',r'$-\frac{5\pi}{2}$',r'$-2\pi$',r'$-\frac{3\pi}{2}$',
 r'$-\pi$',r'$-\frac{\pi}{2}$','0',r'$\frac{\pi}{2}$',r'$\pi$',r'$\frac{3\pi}{2}$',
 r'$2\pi$',r'$\frac{5\pi}{2}$',r'$3\pi$'])
save(fig,'graph-cotangent.pdf')

fig,axs=plt.subplots(1,2,figsize=(9.4,4.0),constrained_layout=True)
for ax,title in zip(axs,[r'$y=\operatorname{th}x$',r'$y=\operatorname{cth}x$']):
 axes(ax,title,(-4,4),(-3.4,3.4))
 for y in (-1,1):ax.axhline(y,color=OCHRE,ls='--',lw=1)
x=np.linspace(-4,4,600);axs[0].plot(x,np.tanh(x),color=TEAL,lw=2)
for a,b in [(-4,-.025),(.025,4)]:
 x=np.linspace(a,b,500);axs[1].plot(x,1/np.tanh(x),color=TEAL,lw=2)
axs[1].axvline(0,color=OCHRE,ls='--',lw=1)
save(fig,'atlas-hyperbolic-ratios.pdf')

fig,axs=plt.subplots(1,2,figsize=(9.4,4.3),constrained_layout=True)
ax=axs[0];axes(ax,'Разные координаты одного вектора',(-.5,4),(-1.7,3))
ax.set_aspect('equal');arrow(ax,(1,1),TEAL,r'$b_1$');arrow(ax,(1,-1),OCHRE,r'$b_2$')
arrow(ax,(3,1),NAVY,r'$v=2b_1+b_2$')
ax.plot([0,2,3],[0,2,1],color=TEAL,ls='--',lw=1)
ax.text(-.35,2.6,r'$[v]_B=(2,1)^{\mathsf{T}}$',color=NAVY)
ax=axs[1];axes(ax,r'$T(x,y)=(x,0)$',(-2,2),(-1.4,2.2))
ax.set_aspect('equal');ax.plot([0,0],[-1.4,2.2],lw=4,color=OCHRE,alpha=.4)
ax.plot([-2,2],[0,0],lw=4,color=TEAL,alpha=.4)
arrow(ax,(1.3,1.5),NAVY,r'$v$');arrow(ax,(1.3,0),TEAL,r'$T(v)$',offset=(.05,-.35))
ax.plot([1.3,1.3],[0,1.5],ls='--',color=NAVY,lw=1)
ax.text(-1.85,1.85,r'$\ker T$: ось y',color=OCHRE,fontsize=10)
ax.text(-1.85,-.8,r'$\operatorname{im}T$: ось x',color=TEAL,fontsize=10)
save(fig,'atlas-spaces.pdf')

fig,axs=plt.subplots(1,2,figsize=(9.4,4.5),constrained_layout=True)
theta=np.linspace(0,2*np.pi,600)
u=np.cos(theta)/np.sqrt(3);v=np.sin(theta)
x=(u+v)/np.sqrt(2);y=(u-v)/np.sqrt(2)
ax=axs[0];axes(ax,r'$2x^2+2xy+2y^2=1$',(-1.25,1.25),(-1.25,1.25))
ax.set_aspect('equal');ax.plot(x,y,color=TEAL,lw=2)
for vector,color,label in [((1/np.sqrt(2),1/np.sqrt(2)),OCHRE,r'$\lambda=3$'),
 ((1/np.sqrt(2),-1/np.sqrt(2)),NAVY,r'$\lambda=1$')]:
 arrow(ax,vector,color,label,offset=(.02,.12 if color==OCHRE else -.23))
 ax.plot([-vector[0],0],[-vector[1],0],color=color,lw=1,ls='--')
ax=axs[1];axes(ax,r'$3u^2+v^2=1$',(-1.25,1.25),(-1.25,1.25))
ax.set_xlabel('u',loc='right');ax.set_ylabel('v',rotation=0,loc='top')
ax.set_aspect('equal');ax.plot(u,v,color=TEAL,lw=2)
ax.annotate(r'$\frac{1}{\sqrt{3}}$',(.577,0),(.72,.3),arrowprops=dict(arrowstyle='->',color=OCHRE),color=OCHRE)
ax.text(.08,1.04,'1',color=NAVY)
save(fig,'atlas-quadratic.pdf')

fig,axs=plt.subplots(1,3,figsize=(10,3.5),constrained_layout=True)
for ax,title in zip(axs,[r'$d_2$: круг',r'$d_1$: ромб',r'$d_\infty$: квадрат']):
 axes(ax,title,(-1.35,1.35),(-1.35,1.35));ax.set_aspect('equal')
 ax.set_xticks([-1,0,1]);ax.set_yticks([-1,0,1])
style=dict(facecolor=TEAL,edgecolor=NAVY,alpha=.28,lw=2,linestyle='--')
axs[0].add_patch(Circle((0,0),1,**style))
axs[1].add_patch(Polygon([(1,0),(0,1),(-1,0),(0,-1)],**style))
axs[2].add_patch(Rectangle((-1,-1),2,2,**style))
fig.supxlabel('Пунктирные границы не входят в открытые шары.',fontsize=11,color=NAVY)
save(fig,'atlas-metric.pdf')

fig,axs=plt.subplots(2,2,figsize=(9.4,7.5),constrained_layout=True)
for ax,left,title in [(axs[0,0],True,'Нижняя сумма: 7/32'),(axs[0,1],False,'Верхняя сумма: 15/32')]:
 axes(ax,title,(-.03,1.04),(-.05,1.15))
 x=np.linspace(0,1,500);ax.plot(x,x*x,color=NAVY,lw=2)
 for k in range(4):
  h=(k/4 if left else (k+1)/4)**2
  ax.add_patch(Rectangle((k/4,0),.25,h,facecolor=TEAL,edgecolor=OCHRE,alpha=.4))
ax=axs[1,0];axes(ax,r'$\int_{-1}^1 x\,dx=0$, площадь = 1',(-1.1,1.1),(-1.2,1.2))
x=np.linspace(-1,1,600);ax.plot(x,x,color=NAVY,lw=2)
ax.fill_between(x,0,x,where=x>=0,color=TEAL,alpha=.35)
ax.fill_between(x,0,x,where=x<=0,color=OCHRE,alpha=.35)
ax.text(.4,.15,'+',color=TEAL,fontsize=20);ax.text(-.6,-.35,'−',color=OCHRE,fontsize=20)
ax=axs[1,1];axes(ax,r'$A(x)=\int_0^x t^2\,dt$',(-.1,1.5),(-.1,1.3))
x=np.linspace(0,1.45,500);ax.plot(x,x**3/3,color=TEAL,lw=2,label=r'$A(x)=\frac{x^3}{3}$')
ax.plot(x,x-2/3,color=OCHRE,ls='--',lw=1.5,label=r'Касательная при x=1: $A^\prime(1)=1$')
ax.plot(1,1/3,'o',color=NAVY);ax.legend(fontsize=9,loc='upper left')
save(fig,'atlas-integral.pdf')

fig,axs=plt.subplots(2,2,figsize=(9.4,7.2),constrained_layout=True)
n=np.arange(1,25)
ax=axs[0,0];axes(ax,'Геометрический ряд: частичные суммы',(0,24),(0,1.15))
ax.set_xlabel('N',loc='right');ax.set_ylabel(r'$S_N$',rotation=0,loc='top')
ax.plot(n,1-2.0**(-n),'o-',ms=3,color=TEAL);ax.axhline(1,ls='--',color=OCHRE,lw=1)
ax=axs[0,1];axes(ax,'Гармонический ряд: рост продолжается',(0,24),(0,4.3))
ax.set_xlabel('N',loc='right');ax.set_ylabel(r'$S_N$',rotation=0,loc='top')
ax.plot(n,np.cumsum(1/n),'o-',ms=3,color=OCHRE)
ax=axs[1,0];axes(ax,'Знакопеременный ряд: две стороны',(0,24),(.4,1.1))
ax.set_xlabel('N',loc='right');ax.set_ylabel(r'$S_N$',rotation=0,loc='top')
sn=np.cumsum((-1.0)**(n-1)/n)
ax.plot(n,sn,color=NAVY,lw=.7,alpha=.5)
ax.plot(n[n%2==0],sn[n%2==0],'o-',ms=3,color=TEAL,label='Чётные суммы')
ax.plot(n[n%2==1],sn[n%2==1],'o-',ms=3,color=OCHRE,label='Нечётные суммы')
ax.legend(fontsize=9)
ax=axs[1,1];ax.set_title('Концы проверяются отдельно',color=NAVY,pad=13)
ax.set_xlim(-1.5,1.5);ax.set_ylim(-.5,2.6);ax.set_xticks([-1,0,1]);ax.set_yticks([])
ax.set_xlabel('x',loc='right')
for y,endclosed,label in [(1.7,False,r'$\sum_{n=1}^\infty\frac{x^n}{n}$'),(.4,True,r'$\sum_{n=1}^\infty\frac{x^n}{n^2}$')]:
 ax.plot([-1,1],[y,y],lw=4,color=TEAL)
 ax.plot(-1,y,'o',mfc=TEAL,mec=NAVY,ms=8)
 ax.plot(1,y,'o',mfc=TEAL if endclosed else PAPER,mec=NAVY,ms=8)
 ax.text(-1.3,y+.23,label,color=NAVY)
save(fig,'atlas-series.pdf')
print('Generated seven edition 8 figure files')
