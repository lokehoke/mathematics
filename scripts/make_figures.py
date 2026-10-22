from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Arc
ROOT=Path(__file__).resolve().parents[1]/'sources/book/images';ROOT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':13,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight','figure.facecolor':'#fffcf6','axes.facecolor':'#fffcf6'})
NAVY='#233f4a';TEAL='#5a7b77';CORAL='#ae7046';GOLD='#c39b55'
def axes(ax,title,xlim,ylim):
 ax.set_title(title,color=NAVY,pad=12);ax.set_xlim(xlim);ax.set_ylim(ylim)
 ax.axhline(0,color='#70818c',lw=.8);ax.axvline(0,color='#70818c',lw=.8)
 ax.grid(alpha=.17);ax.set_xlabel('x',loc='right');ax.set_ylabel('y',rotation=0,loc='top')
def plot_page(name,items):
 fig,axs=plt.subplots(3,2,figsize=(8,10.2),constrained_layout=True)
 for ax,(title,fun,xl,yl,pieces) in zip(axs.flat,items):
  axes(ax,title,xl,yl)
  for a,b in pieces or [xl]:
   x=np.linspace(a,b,700);ax.plot(x,fun(x),color=TEAL,lw=2)
 fig.savefig(ROOT/(name+'.pdf'));plt.close(fig)
plot_page('atlas-algebra',[
 ('$y=x$',lambda x:x,(-3,3),(-3,3),None),('$y=x^2$',lambda x:x*x,(-3,3),(-.5,8),None),
 ('$y=x^3$',lambda x:x**3,(-2,2),(-8,8),None),('$y=|x|$',abs,(-3,3),(-.5,3.5),None),
 ('$y=\\sqrt{x}$',np.sqrt,(0,5),(-.3,2.5),None),(r'$y=\frac{1}{x}$',lambda x:1/x,(-4,4),(-4,4),[(-4,-.08),(.08,4)])])
plot_page('atlas-exponential',[
 ('$y=2^x$',lambda x:2.**x,(-3,3),(-.5,8.5),None),(r'$y=(\frac{1}{2})^x$',lambda x:.5**x,(-3,3),(-.5,8.5),None),
 ('$y=e^x$',np.exp,(-3,2),(-.5,8),None),('$y=\\ln x$',np.log,(.05,5),(-3.5,2),None),
 ('$y=\\operatorname{sh} x$',np.sinh,(-2,2),(-4,4),None),('$y=\\operatorname{ch} x$',np.cosh,(-2,2),(0,4.5),None)])
plot_page('atlas-trigonometry',[
 ('$y=\\sin x$',np.sin,(-2*np.pi,2*np.pi),(-1.3,1.3),None),('$y=\\cos x$',np.cos,(-2*np.pi,2*np.pi),(-1.3,1.3),None),
 ('$y=\\operatorname{tg} x$',np.tan,(-2*np.pi,2*np.pi),(-4,4),[(max(-2*np.pi,k*np.pi-np.pi/2+.025),min(2*np.pi,k*np.pi+np.pi/2-.025)) for k in range(-2,3)]),
 ('$y=\\arcsin x$',np.arcsin,(-1,1),(-1.8,1.8),None),('$y=\\arccos x$',np.arccos,(-1,1),(-.2,3.4),None),
 ('$y=\\operatorname{arctg} x$',np.arctan,(-5,5),(-1.8,1.8),None)])
# A separate wide plot makes periodic branches and discontinuities legible.
fig,ax=plt.subplots(figsize=(9,4.7),constrained_layout=True)
axes(ax,'$y=\\operatorname{tg}x$',(-3*np.pi,3*np.pi),(-4,4))
for k in range(-3,4):
 a=max(-3*np.pi,k*np.pi-np.pi/2+.02);b=min(3*np.pi,k*np.pi+np.pi/2-.02)
 x=np.linspace(a,b,600);ax.plot(x,np.tan(x),color=TEAL,lw=2)
for k in range(-3,3):ax.axvline(np.pi/2+k*np.pi,color=CORAL,lw=1,ls='--',alpha=.8)
ax.set_xticks(np.arange(-3,4)*np.pi, ['$-3\\pi$','$-2\\pi$','$-\\pi$','$0$','$\\pi$','$2\\pi$','$3\\pi$'])
ax.set_yticks([-3,-2,-1,0,1,2,3]);fig.savefig(ROOT/'graph-tangent.pdf');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(8,3.4),constrained_layout=True)
for ax,title,fun,xl,yl in [(axs[0],'$y=\\sqrt[3]{x}$',np.cbrt,(-8,8),(-2.5,2.5)),(axs[1],'$y=\\sqrt[4]{x}$',lambda x:x**.25,(0,16),(-.2,2.5))]:
 axes(ax,title,xl,yl);x=np.linspace(*xl,700);ax.plot(x,fun(x),color=TEAL,lw=2)
fig.savefig(ROOT/'atlas-roots.pdf');plt.close(fig)
def scene(name):
 f,a=plt.subplots(figsize=(7,3.2));a.axis('off');a.set_aspect('equal');return f,a
def save(f,name):f.savefig(ROOT/(name+'.pdf'));plt.close(f)
f,a=scene('ladder');a.set_xlim(-.7,5);a.set_ylim(-.6,4.8)
a.plot([0,0,4.5],[4.5,0,0],color=NAVY,lw=2);a.plot([0,3],[4,0],color=CORAL,lw=4)
a.plot([0,.25,.25],[.25,.25,0],color=TEAL);a.text(1.5,-.4,'3 м',ha='center',color=NAVY);a.text(-.25,2,'4 м',rotation=90,ha='center',color=NAVY);a.text(1.8,2.5,'Лестница',rotation=-53,color=CORAL);save(f,'diagram-ladder')
f,a=scene('square');a.set_xlim(-1,7);a.set_ylim(-.8,6.5)
a.add_patch(Rectangle((0,0),6,6,facecolor='#f3dfb1',edgecolor=CORAL,lw=2));a.add_patch(Rectangle((0,0),4,4,facecolor='#cce9e7',edgecolor=TEAL,lw=2))
a.text(2,2,'Исходная\nплощадка',ha='center',va='center',color=NAVY);a.text(2,-.45,'x',ha='center');a.text(5,-.45,'3 м',ha='center');a.text(6.3,5,'3 м',rotation=90,ha='center');save(f,'diagram-square')
f,a=scene('wheel');a.set_xlim(-17,17);a.set_ylim(-2,30)
a.plot([-17,17],[0,0],color=NAVY);a.add_patch(Circle((0,15),12,facecolor='#e8f4f3',edgecolor=TEAL,lw=2));a.plot([0,0],[0,15],color=NAVY,lw=2);a.plot([0,12],[15,15],color=CORAL,lw=2);a.text(6,16,'12 м',ha='center',color=CORAL);a.text(-1,7,'15 м',ha='right',color=NAVY);a.plot(12,15,'o',color=CORAL,ms=8);save(f,'diagram-wheel')
f,a=scene('venn');a.set_xlim(-3.4,3.4);a.set_ylim(-2,2.1)
a.add_patch(Rectangle((-3.2,-1.7),6.4,3.5,facecolor='#f8fafb',edgecolor=NAVY));a.add_patch(Circle((-.8,0),1.4,facecolor=TEAL,alpha=.25,edgecolor=TEAL,lw=2));a.add_patch(Circle((.8,0),1.4,facecolor=CORAL,alpha=.25,edgecolor=CORAL,lw=2));a.text(-1.25,0,'A',ha='center',fontsize=16,color=TEAL);a.text(1.25,0,'B',ha='center',fontsize=16,color=CORAL);a.text(0,0,'A ∩ B',ha='center',fontsize=10,color=NAVY);a.text(2.8,1.4,'U',ha='center',color=NAVY);save(f,'diagram-venn')
print('Generated 4 graph atlases and 4 task diagrams')
