#!/usr/bin/env python3
"""Reproduce the exact auxiliary figures for the examination geometry chapters."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "sources" / "book" / "images"
NAVY = "#203b49"
TEAL = "#5d807c"
OCHRE = "#b88a4d"
CREAM = "#fbf8ef"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "text.color": NAVY,
        "axes.edgecolor": NAVY,
        "mathtext.fontset": "dejavusans",
        "pdf.fonttype": 3,
    }
)


def line(ax, points, color=NAVY, **kwargs):
    points = np.asarray(points)
    ax.plot(*points.T, color=color, linewidth=1.7, **kwargs)


def label(ax, point, text, offset=(0, 0)):
    ax.annotate(
        text,
        point,
        xytext=offset,
        textcoords="offset points",
        ha="center",
        va="center",
        fontsize=11,
    )


def plane_figure():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.8))
    fig.patch.set_facecolor(CREAM)
    for ax in axes:
        ax.set_facecolor(CREAM)
        ax.set_aspect("equal")
        ax.axis("off")

    ax = axes[0]
    a, b, c = np.array((0., 0.)), np.array((8., 0.)), np.array((2., 5.))
    m, n = (a + b) / 2, (a + c) / 2
    p, g = (b + c) / 2, (a + b + c) / 3
    line(ax, [a, b, c, a])
    line(ax, [a, p], color=OCHRE)
    line(ax, [c, m], color=OCHRE)
    line(ax, [m, n], color=TEAL, linestyle="--")
    ax.scatter(*g, s=25, color=TEAL, zorder=4)
    for point, name, offset in [
        (a, "$A$", (-10, -7)), (b, "$B$", (10, -7)),
        (c, "$C$", (0, 10)), (m, "$M$", (0, -11)),
        (n, "$N$", (-11, 2)), (p, "$P$", (11, 3)),
        (g, "$G$", (9, 2)),
    ]:
        label(ax, point, name, offset)
    ax.set_xlim(-.7, 8.7)
    ax.set_ylim(-.6, 5.7)
    ax.set_title("Медианы и средняя линия", pad=10)
    ax.text(.5, -.04, r"$AG:GP=CG:GM=2:1,\quad MN=\frac{BC}{2}$",
            transform=ax.transAxes, ha="center", fontsize=11)

    ax = axes[1]
    a, b, c, d = [np.array(x, dtype=float) for x in [(0, 0), (10, 0), (8, 4), (2, 4)]]
    m, n, k = (a + d) / 2, (b + c) / 2, (a + c) / 2
    line(ax, [a, b, c, d, a])
    line(ax, [a, c], color=OCHRE)
    line(ax, [m, n], color=TEAL)
    ax.scatter(*k, s=25, color=TEAL, zorder=4)
    for point, name, offset in [
        (a, "$A$", (-8, -9)), (b, "$B$", (8, -9)),
        (c, "$C$", (5, 10)), (d, "$D$", (-5, 10)),
        (m, "$M$", (-11, 1)), (n, "$N$", (11, 1)),
        (k, "$K$", (0, -12)),
    ]:
        label(ax, point, name, offset)
    label(ax, (5, 0), "$10$", (0, -12))
    label(ax, (5, 4), "$6$", (0, 11))
    label(ax, (2.5, 2), "$3$", (0, 10))
    label(ax, (6.5, 2), "$5$", (0, 10))
    ax.set_xlim(-.8, 10.8)
    ax.set_ylim(-.7, 4.8)
    ax.set_title("Диагональ делит среднюю линию", pad=10)
    ax.text(.5, -.04, r"$MK=\frac{CD}{2}=3,\quad KN=\frac{AB}{2}=5$",
            transform=ax.transAxes, ha="center", fontsize=11)
    fig.subplots_adjust(left=.035, right=.965, top=.86, bottom=.18, wspace=.20)
    fig.savefig(OUT / "exam-geometry-plane.pdf", facecolor=CREAM)
    plt.close(fig)


def label3(ax, point, text, offset=(0, 0, 0)):
    ax.text(*(np.asarray(point) + np.asarray(offset)), text, ha="center", va="center", fontsize=10)


def spatial_figure():
    fig = plt.figure(figsize=(10.4, 4.6), facecolor=CREAM)
    ax = fig.add_subplot(1, 2, 1, projection="3d", facecolor=CREAM)
    vertices = np.array([(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0),
                         (0, 0, 2), (2, 0, 2), (2, 2, 2), (0, 2, 2)], dtype=float)
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6),
             (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    for i, j in edges:
        hidden = (i, j) in [(2, 3), (3, 0), (3, 7)]
        line(ax, vertices[[i, j]], color=TEAL if hidden else NAVY,
             linestyle="--" if hidden else "-", alpha=.6 if hidden else 1)
    section = np.array([(2, 1, 0), (1, 2, 0), (0, 2, 1),
                        (0, 1, 2), (1, 0, 2), (2, 0, 1)])
    ax.add_collection3d(Poly3DCollection([section], facecolor=TEAL, edgecolor=OCHRE,
                                       linewidth=2, alpha=.28))
    line(ax, np.vstack((section, section[0])), color=OCHRE)
    for i, name in enumerate(["$A$", "$B$", "$C$", "$D$", "$A_1$", "$B_1$", "$C_1$", "$D_1$"]):
        offset = (.04, -.12, -.16) if i < 4 else (.03, .02, .13)
        label3(ax, vertices[i], name, offset)
    ax.set_title(r"Куб: $x+y+z=\frac{3a}{2}$", y=.98, pad=4)
    ax.text2D(.5, -.01, r"Шесть середин рёбер; сторона сечения $\frac{a}{\sqrt{2}}$",
              transform=ax.transAxes, ha="center", fontsize=10)
    ax.set_xlim(-.25, 2.25)
    ax.set_ylim(-.25, 2.25)
    ax.set_zlim(-.25, 2.25)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=32, azim=-20)
    ax.set_axis_off()

    ax = fig.add_subplot(1, 2, 2, projection="3d", facecolor=CREAM)
    base = np.array([(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0)], dtype=float)
    s = np.array((1, 1, 3.), dtype=float)
    mids = (base + s) / 2
    for i in range(4):
        hidden = i in (2, 3)
        line(ax, base[[i, (i + 1) % 4]], color=TEAL if hidden else NAVY,
             linestyle="--" if hidden else "-", alpha=.6 if hidden else 1)
        line(ax, [base[i], s], color=TEAL if i == 3 else NAVY,
             linestyle="--" if i == 3 else "-", alpha=.6 if i == 3 else 1)
    ax.add_collection3d(Poly3DCollection([mids], facecolor=TEAL, edgecolor=OCHRE,
                                       linewidth=2, alpha=.3))
    line(ax, np.vstack((mids, mids[0])), color=OCHRE)
    for point, name in zip(base, ["$A$", "$B$", "$C$", "$D$"]):
        label3(ax, point, name, (0, -.06, -.13))
    for point, name, offset in zip(mids, ["$M$", "$N$", "$P$", "$Q$"],
                                    [(-.13, -.05, 0), (.13, -.05, 0),
                                     (.14, .06, .05), (-.14, .06, .05)]):
        label3(ax, point, name, offset)
    label3(ax, s, "$S$", (0, 0, .16))
    ax.set_title("Пирамида: сечение через середины", y=.98, pad=4)
    ax.text2D(.5, -.01, r"$MNPQ\parallel ABCD,\quad S_{MNPQ}=\frac{S_{ABCD}}{4}$",
              transform=ax.transAxes, ha="center", fontsize=10)
    ax.set_xlim(-.25, 2.25)
    ax.set_ylim(-.25, 2.25)
    ax.set_zlim(-.2, 3.4)
    ax.set_box_aspect((1, 1, 1.3))
    ax.view_init(elev=19, azim=-58)
    ax.set_axis_off()
    fig.subplots_adjust(left=.01, right=.99, top=.92, bottom=.13, wspace=.02)
    fig.savefig(OUT / "exam-geometry-sections.pdf", facecolor=CREAM)
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    plane_figure()
    spatial_figure()
