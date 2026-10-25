"""Exact, vector coordinate figures for the independently reviewed exercises."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'sources/book/data/review-ege-figures.json').read_text())
OUT=ROOT/'sources/book/images'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,
 'axes.titlesize':14,'pdf.fonttype':3,'axes.unicode_minus':False,
 'text.color':'#233F4A','axes.labelcolor':'#233F4A'})
navy='#233F4A';teal='#5A7B77';ochre='#AE7046'

def axes(ax,p):
 ax.set_xlim(*p['xlim']);ax.set_ylim(*p['ylim'])
 ax.xaxis.set_major_locator(MultipleLocator(1));ax.yaxis.set_major_locator(MultipleLocator(1))
 ax.grid(color=teal,alpha=.24,lw=.6)
 ax.axhline(0,color=navy,lw=.8);ax.axvline(0,color=navy,lw=.8)
 ax.set_title('Рисунок '+p['label'],loc='left',fontweight='bold',pad=10)
 ax.set_xlabel('$x$');ax.set_ylabel('$y$',rotation=0,labelpad=12)
 for point in p['points']:
  x,y=point['xy'];ax.plot(x,y,'o',ms=5,color=ochre,zorder=5)
  if point['name']:ax.annotate('$'+point['name']+'$',(x,y),xytext=(6,7),textcoords='offset points',fontsize=12,color=ochre,zorder=6)

fig,axs=plt.subplots(2,2,figsize=(9,7.8))
for i,(ax,p)in enumerate(zip(axs.flat,DATA['functions']['panels'])):
 axes(ax,p);x=np.linspace(*p['xlim'],1200)
 if i==0:ax.plot(x,2*(x+1)**2-3,color=navy,lw=1.7)
 elif i==1:
  for a,b in [(p['xlim'][0],-.05),(.05,p['xlim'][1])]:
   t=np.linspace(a,b,600);ax.plot(t,-8/t,color=navy,lw=1.7)
 elif i==2:ax.plot(x,3.**x,color=navy,lw=1.7)
 else:
  ax.plot(x,x*x-4*x,color=navy,lw=1.7);ax.plot(x,x,color=teal,lw=1.7)
fig.tight_layout(pad=2.1,h_pad=2.6,w_pad=2.1)
fig.savefig(OUT/'review-ege-functions.pdf',transparent=True);plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(9,3.9))
for i,(ax,p)in enumerate(zip(axs,DATA['calculus']['panels'])):
 axes(ax,p);x=np.linspace(*p['xlim'],1800)
 if i==0:
  ax.plot(x,.1*(x+2)*(x-1)**2*(x-3),color=navy,lw=1.8,label="$f'(x)$")
 else:
  ax.plot(x,.125*(x-2)**2-.5*x+2,color=navy,lw=1.7,label='$f(x)$')
  ax.plot(x,-.5*x+2,color=teal,lw=1.7,label='Касательная')
 ax.legend(loc='upper right',fontsize=10,framealpha=.95)
fig.tight_layout(pad=2,w_pad=2.2)
fig.savefig(OUT/'review-ege-calculus.pdf',transparent=True);plt.close(fig)
print('Saved two vector PDFs; six exact coordinate panels')
