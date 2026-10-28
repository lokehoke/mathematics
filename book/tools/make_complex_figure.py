"""Exact complex-plane diagrams; decorative artwork is generated separately."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[2] / 'book/source/images/atlas-complex.pdf'
NAVY, TEAL, OCHRE, PAPER = '#233f4a', '#5a7b77', '#ae7046', '#fffcf6'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.titlesize': 12, 'figure.facecolor': PAPER,
                     'axes.facecolor': PAPER})
fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.9), constrained_layout=True)
for ax in axes:
    ax.set_aspect('equal')
    ax.grid(alpha=.15)
    ax.axhline(0, color=NAVY, lw=.7)
    ax.axvline(0, color=NAVY, lw=.7)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlabel(r'$\operatorname{Re}z$', loc='right')
    ax.set_ylabel(r'$\operatorname{Im}z$', loc='top', rotation=0)

ax = axes[0]
ax.set_title('Сопряжение: отражение относительно Re', color=NAVY, pad=14)
ax.set_xlim(-.8, 4.5)
ax.set_ylim(-4, 4)
ax.plot([2, 2], [-3, 3], '--', color=TEAL, lw=1)
for y, color, label in [(3, TEAL, r'$z=2+3i$'),
                         (-3, OCHRE, r'$\overline{z}=2-3i$')]:
    ax.annotate('', xy=(2, y), xytext=(0, 0),
                arrowprops={'arrowstyle': '->', 'lw': 1.8, 'color': color})
    ax.plot(2, y, 'o', color=color)
    ax.text(2.15, y + .15, label, color=color)
ax.text(2.2, 1.7, r'$|z|=\sqrt{13}$', color=NAVY)

ax = axes[1]
ax.set_title(r'Все три корня уравнения $z^3=8$', color=NAVY, pad=14)
ax.set_xlim(-2.8, 3)
ax.set_ylim(-2.6, 2.6)
theta = np.linspace(0, 2 * np.pi, 501)
ax.plot(2 * np.cos(theta), 2 * np.sin(theta), '--', color=TEAL, lw=1)
roots = [(2, 0, r'$2$', (.12, .15)),
         (-1, np.sqrt(3), r'$-1+i\sqrt{3}$', (-1.35, .2)),
         (-1, -np.sqrt(3), r'$-1-i\sqrt{3}$', (-1.35, -.4))]
for x, y, label, (dx, dy) in roots:
    ax.plot([0, x], [0, y], color=OCHRE, lw=1.2)
    ax.plot(x, y, 'o', color=TEAL, ms=6)
    ax.text(x + dx, y + dy, label, color=NAVY)
fig.savefig(OUT, bbox_inches='tight')
plt.close(fig)
print(OUT)
