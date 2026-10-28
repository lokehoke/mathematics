from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':3,'ps.fonttype':3,'axes.unicode_minus':False,'axes.labelcolor':'#23384d','text.color':'#23384d','xtick.color':'#23384d','ytick.color':'#23384d'})
fig,axs=plt.subplots(1,2,figsize=(6.7,3.25),layout='constrained');fig.patch.set_facecolor('#fffdf7')
for ax,label in zip(axs,['A','B']):
 ax.set_facecolor('#fffdf7');ax.set_title(label,loc='left',fontweight='bold');ax.grid(True,color='#ced7d1',linewidth=.55);ax.set_axisbelow(True)
 for spine in ax.spines.values():spine.set_color('#74858b')
months=np.arange(1,13); temps=[-6,-4,1,8,15,19,22,20,14,7,0,-3]
ax=axs[0];ax.bar(months,temps,color=['#b78745' if t<0 else '#477d80' for t in temps],width=.68,edgecolor='#23384d',linewidth=.4)
ax.axhline(0,color='#23384d',linewidth=.8);ax.set_xticks(months);ax.tick_params(axis='x',labelsize=9.25);ax.set_yticks(np.arange(-8,25,2));ax.set_ylim(-8,24);ax.set_xlim(.4,12.6);ax.set_xlabel('Месяц');ax.set_ylabel('Температура, °C')
for x,y in zip(months,temps):ax.text(x,y+(.35 if y>=0 else -.35),str(y),ha='center',va='bottom' if y>=0 else 'top',fontsize=9.5,color='#23384d')
ax=axs[1];R=np.linspace(0,5,600);I=12/(R+1);ax.plot(R,I,color='#23384d',linewidth=1.7);ax.set_xticks(np.arange(0,6,1));ax.set_yticks(np.arange(0,13,1));ax.set_xlim(0,5);ax.set_ylim(0,12.5);ax.set_xlabel('Сопротивление R, Ом');ax.set_ylabel('Сила тока I, А')
for x,y in [(0,12),(1,6),(2,4),(3,3),(5,2)]:ax.scatter([x],[y],s=17,color='#b78745',edgecolor='#23384d',linewidth=.4,zorder=5)
out=ROOT/'book/source/images/review-ege-data-reading.pdf';fig.savefig(out,facecolor=fig.get_facecolor());plt.close(fig);print(out)
