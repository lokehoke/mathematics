#!/usr/bin/env python3
"""Independent exact/finite checks for seven final EGE exercises; stdlib only."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from math import inf, isclose, sqrt
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources/book/data/review-ege-parameters-final.json"
RESULT = ROOT / "research/review-ege-parameters-final-check-2026-10-25.json"
checks = Counter()


def check(condition, group):
    assert condition, group
    checks[group] += 1


def count_restricted_system(a, slope, intercept):
    # Solve the two factors directly, retain the original radicand condition,
    # and identify coincident pairs. This does not use the asserted table.
    points = [(float(a) - intercept) / slope]
    if a >= 0:
        for x in {sqrt(float(a)), -sqrt(float(a))}:
            if slope * x + intercept - float(a) >= -1e-10:
                points.append(x)
    return len({round(x, 11) for x in points})


def claimed_restricted(a, last):
    if a < 0 or a >= last:
        return 1
    if a == 0 or a >= 1:
        return 2
    return 3


def level_preimages(t, r):
    if t < 2 * r:
        return 0
    if t == 2 * r:
        return 1 if r == 0 else inf
    return 2


def count_sum_abs_quadratic(r, center):
    # Distinct roots of (t-center)^2=r^2, followed by exact preimage counts.
    return sum(level_preimages(t, r) for t in {center - r, center + r})


def claimed_sum_abs(r, center):
    if r == 0:
        return 2
    if r < center / 3:
        return 4
    if r in {center / 3, center}:
        return inf
    if r < center:
        return 2
    return 0


def bisect(fun, lo, hi):
    flo = fun(lo)
    for _ in range(100):
        mid = (lo + hi) / 2
        fm = fun(mid)
        if flo * fm > 0:
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def numerical_c_count(d):
    # Independent numerical roots of both polynomial pieces. The derivative
    # of the quartic has one positive zero, giving two monotone intervals.
    # Differentiation is used only by this check, not in the book's proof.
    roots = []
    if 0 <= d <= 2:
        u = (d * (2 - d)) ** 0.25
        if u <= d + 1e-9:
            roots.append(u)
    fun = lambda u: u**4 - 2 * u + d * d
    stationary = 2 ** (-1 / 3)
    value = fun(stationary)
    if d == 0:
        roots.extend([0.0, 2 ** (1 / 3)])
    elif value < -1e-12:
        roots.extend([
            bisect(fun, 0.0, stationary),
            bisect(fun, stationary, 2.0 + d),
        ])
    elif abs(value) <= 1e-12:
        roots.append(stationary)
    roots = [u for u in roots if u <= d + 1e-9 and abs(u**4 + d*d - 2*d) < 1e-7
             or u >= d - 1e-9 and abs(fun(u)) < 1e-7]
    unique = []
    for u in roots:
        if all(abs(u - v) > 1e-7 for v in unique):
            unique.append(u)
    return sum(1 if abs(u) < 1e-8 else 2 for u in unique)


def polynomial_count(a):
    roots = [3.0]
    if a != 0:
        roots.append(float(2 / a))
    if abs(a) <= 1:
        v = sqrt(float(1 - a*a))
        roots.extend([v, -v])
    return len({round(x, 10) for x in roots})


def digit_sum(n):
    return sum(map(int, str(n)))


data = json.loads(SOURCE.read_text())
tasks = [t for value in data.values() for t in value["tasks"]]
labels = re.findall(r"\\label\{([^}]+)\}", "\n".join(v["theory"] for v in data.values()))
check(len(tasks) == 7, "structure")
check({t["uid"] for t in tasks} == {f"review-ege-final.G1.{i}" for i in range(1, 8)}, "structure")
check(len(labels) == len(set(labels)) == 3, "structure")
for value in data.values():
    for text in [value["theory"]] + [s for t in value["tasks"] for s in [t["q"], t["a"]]]:
        check("\x00" not in text, "structure")
        check(text.count(r"\(") == text.count(r"\)"), "structure")
        check(text.count(r"\[") == text.count(r"\]"), "structure")
        check(text.count("{") == text.count("}"), "structure")

for slope, intercept, last in [(1, 2, 4), (2, 3, 9)]:
    for k in range(-2048, 4097):
        a = F(k, 256)
        check(count_restricted_system(a, slope, intercept) == claimed_restricted(a, last), "A")

for center in [F(2), F(3)]:
    for r in {F(k, 600) for k in range(3001)} | {center/3, center, F(0)}:
        check(count_sum_abs_quadratic(r, center) == claimed_sum_abs(r, center), "B")
    for a in [F(-7, 3), F(-1), F(0), F(1, 3), F(2), F(4)]:
        for x in [F(-5), F(-1), F(0), F(1, 3), F(3), F(5)]:
            check(abs(x-a) + abs(x+a) == 2 * max(abs(x), abs(a)), "B")

for k in range(2001):
    d = k / 500
    claimed = 3 if d == 0 else 2 if d < 2 else 1 if d == 2 else 0
    check(numerical_c_count(d) == claimed, "C")
for u in [F(k, 10) for k in range(51)]:
    for d in [F(k, 10) for k in range(31)]:
        check(abs(u-d) + abs(u+d) == 2 * max(u, d), "C")

first, second = [3, 3, 3, 3, 3, 9], [36, 36]
check(F(sum(first), len(first)) == 4 and F(sum(second), len(second)) == 36, "P1")
check(F(sum(first)-9, len(first)-1) == 3, "P1")
check(F(sum(second)+9, len(second)+1) == 27, "P1")
candidates = []
for m in range(2, 7):
    n = 8 - m
    for aa in range(1, 101):
        if m == 3:
            continue
        bb, t = F((n+3)*aa, 3-m), F((n+3)*aa, 4)
        if bb > 0 and bb.denominator == 1 and t > 0 and t.denominator == 1:
            if n*aa-t >= n-1:
                candidates.append(bb)
check(min(candidates) == 36, "P1")

groups = {}
for n in range(1, 20001):
    ds = digit_sum(n)
    if len(groups.setdefault(ds, [])) < 5:
        groups[ds].append(n)
check([sum(groups[s]) for s in [1, 2, 3]] == [11111, 244, 168], "P2")
check(groups[4] == [4, 13, 22, 31, 40], "P2")
check(min(sum(v) for v in groups.values() if len(v) == 5) == 110, "P2")

feasible = [(n,m) for n in range(1,101) for m in range(4,201,4)
            if n <= F(m,4)+5 and m <= n+10]
check(max(n+m for n,m in feasible) == 30, "P3")
check(all(m-n <= 10 for n,m in feasible), "P3")
blue, red = list(range(-16,21,4)), list(range(-18,21,2))
check(len(blue) == 10 and len(red) == 20, "P3")
check(max(blue) == len(red) and max(red) == 2*len(blue), "P3")

for a in {F(k,300) for k in range(-900,901)} | {F(2,3), F(-1), F(0), F(1)}:
    claimed = 2 if abs(a)>1 else 3 if a in {F(-1),F(0),F(2,3),F(1)} else 4
    check(polynomial_count(a) == claimed, "P4")
    for x in [F(-3),F(-1),F(0),F(1),F(3),F(7,2)]:
        q = a*x**3 - 2*x*x + a*(a*a-1)*x - 2*(a*a-1)
        check((x-3)*q == (x-3)*(a*x-2)*(x*x+a*a-1), "P4")

result = {
    "checked_at": "2026-10-25", "source": str(SOURCE.relative_to(ROOT)),
    "source_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
    "tasks": 7, "worked_examples": 3, "status": "PASS",
    "assertions": sum(checks.values()), "groups": dict(checks),
    "limits": "Finite checks supplement the exact written arguments; they do not prove continuum statements.",
    "answers": {
        "G1.1": "two pairs at b=0 or 1<=b<9",
        "G1.2": "r=|b|: 2 at 0; 4 on(0,1); infinity at1,3; 2 on(1,3); 0 above3",
        "G1.3": "three at b=-1; two on(-3,1) except-1; one at-3,1; zero outside[-3,1]",
        "G1.4": 36, "G1.5": 110, "G1.6": "difference11 impossible; maximum30",
        "G1.7": "two iff |a|>1; three at-1,0,2/3,1; four otherwise in0<|a|<1"
    }
}
RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ["status", "tasks", "worked_examples", "assertions", "groups"]}, ensure_ascii=False, indent=2))
