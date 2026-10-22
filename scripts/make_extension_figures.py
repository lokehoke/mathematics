"""Exact vector diagrams for the six introductory university chapters."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

OUT=Path(__file__).resolve().parents[1]/'sources/book/images'
NAVY='#233f4a';TEAL='#5a7b77';OCHRE='#ae7046';PAPER='#fffcf6'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
    'axes.titlesize':12,'axes.spines.top':False,'axes.spines.right':False,
    'figure.facecolor':PAPER,'axes.facecolor':PAPER,'savefig.bbox':'tight'})
def setup(ax,title,xlim,ylim):
    ax.set_title(title,color=NAVY,pad=12)
    ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.grid(alpha=.15)
    ax.axhline(0,color=NAVY,lw=.6);ax.axvline(0,color=NAVY,lw=.6)
    ax.set_xlabel('x',loc='right');ax.set_ylabel('y',loc='top',rotation=0)
def point(ax,x,y,closed=True,color=TEAL):
    ax.plot(x,y,'o',ms=7,mec=color,mfc=color if closed else PAPER,zorder=6)

fig,axs=plt.subplots(1,2,figsize=(8.2,3.6),constrained_layout=True)
ax=axs[0];setup(ax,'Сложение векторов',(-.4,3.8),(-.4,3.8));ax.set_aspect('equal')
for dx,dy,color,label in [(2,1,TEAL,'u'),(1,2,OCHRE,'v'),(3,3,NAVY,'u+v')]:
    ax.annotate('',xy=(dx,dy),xytext=(0,0),arrowprops={'arrowstyle':'->','lw':2,'color':color})
    ax.text(dx+.06,dy+.04,label,color=color)
ax.plot([2,3,1],[1,3,2],'--',color=TEAL,lw=1)
ax=axs[1];setup(ax,'Матрица A: (x, y) ↦ (2x+y, y)',(-.4,3.6),(-.4,2.2))
ax.set_aspect('equal')
ax.add_patch(Polygon([(0,0),(1,0),(1,1),(0,1)],facecolor=TEAL,alpha=.22,edgecolor=TEAL,lw=2,label='Единичный квадрат'))
ax.add_patch(Polygon([(0,0),(2,0),(3,1),(1,1)],facecolor=OCHRE,alpha=.25,edgecolor=OCHRE,lw=2,label='Его образ'))
ax.legend(loc='upper left',fontsize=8)
fig.savefig(OUT/'atlas-linear.pdf');plt.close(fig)

fig,axs=plt.subplots(2,2,figsize=(8.2,7.4),constrained_layout=True)
ax=axs[0,0];setup(ax,'Предел и значение могут различаться',(-1,3),(-.5,4.5))
for a,b in [(-1,.99),(1.01,3)]:
    x=np.linspace(a,b,250);ax.plot(x,x+1,color=TEAL,lw=2)
point(ax,1,2,False);point(ax,1,0,True,OCHRE)
ax.annotate(r'$\lim_{x\to1}f(x)=2$',(1,2),(-.8,3.7),arrowprops={'arrowstyle':'->','color':NAVY},color=NAVY)
ax.text(1.15,.25,r'$f(1)=0$',color=OCHRE)
ax=axs[0,1];setup(ax,'Скачок: односторонние пределы разные',(-2,2),(-.4,1.5))
ax.plot([-2,0],[0,0],color=TEAL,lw=2);ax.plot([0,2],[1,1],color=OCHRE,lw=2)
point(ax,0,0,False);point(ax,0,1,True,OCHRE)
ax.text(-1.8,.2,r'$\lim_{x\to0-}f(x)=0$',color=TEAL)
ax.text(.2,1.2,r'$\lim_{x\to0+}f(x)=1$',color=OCHRE)
ax=axs[1,0];setup(ax,r'$f(x)=1/x$: поведение у нуля',(-2,2),(-5,5))
for a,b in [(-2,-.04),(.04,2)]:
    x=np.linspace(a,b,400);ax.plot(x,1/x,color=TEAL,lw=2)
ax.text(.35,3.8,r'$x\to0+:\ f(x)\to+\infty$',fontsize=9,color=NAVY)
ax.text(-1.9,-3.8,r'$x\to0-:\ f(x)\to-\infty$',fontsize=9,color=NAVY)
ax=axs[1,1];setup(ax,r'$f(x)=|x|$: непрерывность в нуле',(-2,2),(-.3,2.4))
x=np.linspace(-2,2,400);ax.plot(x,abs(x),color=TEAL,lw=2);point(ax,0,0)
ax.text(-1.8,2.05,r'$\lim_{x\to0}|x|=0=f(0)$',color=NAVY)
fig.savefig(OUT/'atlas-limits.pdf');plt.close(fig)

fig,axs=plt.subplots(2,2,figsize=(8.2,7.5),constrained_layout=True)
ax=axs[0,0];setup(ax,'Секущая и касательная к y=x²',(-.3,2.4),(-1.2,5.8))
x=np.linspace(-.3,2.4,400)
ax.plot(x,x*x,color=TEAL,lw=2,label=r'$y=x^2$')
ax.plot(x,3*x-2,color=OCHRE,lw=1.5,ls='--',label='Секущая: k=3')
ax.plot(x,2*x-1,color=NAVY,lw=1.5,label='Касательная: k=2')
point(ax,1,1);point(ax,2,4);ax.legend(fontsize=8,loc='upper left')
ax=axs[0,1];setup(ax,'Наклон секущей при h → 0',(-1,1),(1,3))
ax.set_xlabel('h',loc='right');ax.set_ylabel('k',loc='top',rotation=0)
h=np.linspace(-1,1,400);ax.plot(h,2+h,color=TEAL,lw=2)
point(ax,0,2,False);ax.text(-.9,2.65,r'$k(h)=\frac{(1+h)^2-1}{h}=2+h$',fontsize=10,color=NAVY)
ax.text(.12,1.55,r'$k(h)\to2$',color=NAVY)
ax=axs[1,0];setup(ax,r'Приближение $\sqrt{x}$ около 4',(2,6),(1.2,2.8))
x=np.linspace(2,6,400);ax.plot(x,np.sqrt(x),color=TEAL,lw=2,label=r'$y=\sqrt{x}$')
ax.plot(x,2+(x-4)/4,color=OCHRE,lw=1.5,ls='--',label=r'$y=2+\frac{x-4}{4}$')
point(ax,4,2);ax.legend(loc='upper left',fontsize=9)
ax=axs[1,1];setup(ax,r'$|x|$: в нуле нет одной касательной',(-2,2),(-.4,2.5))
ax.plot([-2,0],[2,0],color=OCHRE,lw=2,label='Наклон слева: −1')
ax.plot([0,2],[0,2],color=TEAL,lw=2,label='Наклон справа: 1')
point(ax,0,0);ax.legend(fontsize=8,loc='upper center')
fig.savefig(OUT/'atlas-derivative.pdf');plt.close(fig)
print('Generated linear, limit and derivative atlases')
