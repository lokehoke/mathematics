"""Vector figures for the school-exam coverage additions."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'book/source/images'
font=ROOT/'book/source/fonts/NotoSerif-Regular.ttf'
font_manager.fontManager.addfont(str(font))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':10,'axes.titlesize':11,'axes.edgecolor':'#23364b','text.color':'#23364b','axes.labelcolor':'#23364b','xtick.color':'#23364b','ytick.color':'#23364b','axes.unicode_minus':False,'pdf.fonttype':3})
navy='#23364b';teal='#477e79';ochre='#b98542'
def base(ax,title):
 ax.set_title(title,pad=12);ax.axhline(0,color=navy,lw=.7);ax.axvline(0,color=navy,lw=.7);ax.grid(alpha=.2);ax.set_xlabel('$x$');ax.set_ylabel('$y$',rotation=0,labelpad=8)
def finish(fig,name):fig.tight_layout(pad=1.8);fig.savefig(OUT/name,transparent=True);plt.close(fig)
x=np.linspace(-3,5,500)
fig,axs=plt.subplots(1,2,figsize=(9,3.6))
for ax in axs:base(ax,'')
axs[0].set_title('Сдвиг и отражение');axs[0].plot(x,np.abs(x),color=teal,label='$|x|$');axs[0].plot(x,-2*np.abs(x-1)+3,color=ochre,label='$-2|x-1|+3$');axs[0].set_ylim(-5,6);axs[0].legend(fontsize=9)
axs[1].set_title('Модуль значения');axs[1].plot(x,x*x-4,color=teal,label='$x^2-4$');axs[1].plot(x,np.abs(x*x-4),color=ochre,label='$|x^2-4|$');axs[1].set_xlim(-3,3);axs[1].set_ylim(-5,6);axs[1].legend(fontsize=9)
finish(fig,'exam-functions-transform.pdf')
fig,axs=plt.subplots(1,3,figsize=(10,3.5))
for ax in axs:base(ax,'');ax.set_xlim(-2,3);ax.set_ylim(-2,5)
axs[0].set_title('Устранимая особенность');axs[0].plot(x,x+1,color=teal);axs[0].plot([1],[2],'o',mfc='white',mec=teal,ms=7)
axs[1].set_title('Скачок');axs[1].plot([-2,0],[0,0],color=teal);axs[1].plot([0,3],[2,2],color=teal);axs[1].plot([0],[0],'o',mfc='white',mec=teal,ms=7);axs[1].plot([0],[2],'o',color=teal,ms=6)
axs[2].set_title('Вертикальная асимптота')
for xx in [np.linspace(-2,.95,200),np.linspace(1.05,3,200)]:axs[2].plot(xx,1/(xx-1),color=teal)
axs[2].axvline(1,color=ochre,ls='--');finish(fig,'exam-functions-breaks.pdf')
fig,axs=plt.subplots(1,2,figsize=(9,3.5));x=np.linspace(-2,2,400)
base(axs[0],'Функция');axs[0].plot(x,x**3-3*x,color=teal);axs[0].scatter([-1,1],[2,-2],color=ochre,zorder=4);axs[0].set_ylim(-3,3)
base(axs[1],'Её производная');axs[1].plot(x,3*x*x-3,color=teal);axs[1].scatter([-1,1],[0,0],color=ochre,zorder=4);axs[1].set_ylim(-4,7)
finish(fig,'exam-calculus-signs.pdf')
fig,axs=plt.subplots(1,2,figsize=(9,3.5))
axs[0].bar([1,2,5],[2,3,1],width=.6,color=[teal,ochre,navy]);axs[0].set_xticks([1,2,5]);axs[0].set_xlabel('Значение');axs[0].set_ylabel('Частота');axs[0].set_title('Таблица частот как диаграмма');axs[0].set_yticks([0,1,2,3]);axs[0].grid(axis='y',alpha=.2)
axs[1].pie([2,3,1],labels=['1: два','2: три','5: один'],colors=[teal,ochre,navy],startangle=90,textprops={'fontsize':10});axs[1].set_title('Те же данные: доли');finish(fig,'exam-statistics-charts.pdf')
print('Saved five exact vector diagrams')
