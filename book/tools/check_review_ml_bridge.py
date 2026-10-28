#!/usr/bin/env python3
"""Recalculate the 26 original ML-bridge exercises and worked examples.

Standard library only. Exercise specifications are encoded independently of
their LaTeX answers. Exact arithmetic checks algebra; finite differences check
the small network. Finite checks supplement, rather than replace, the written
proofs and manual review of the qualitative answers.
"""
from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'book/source/data/review-ml-bridge.json'
RESULT = ROOT / 'book/references/review-ml-bridge-check-2026-10-25.json'
CHECKS: dict[str, int] = {}


def check(uid, condition):
    CHECKS[uid] = CHECKS.get(uid, 0) + 1
    if not condition:
        raise AssertionError(f'{uid}: assertion {CHECKS[uid]} failed')


def close(a, b, tol=1e-8):
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def sub(a, b):
    return [x-y for x, y in zip(a, b)]


def mv(a, x):
    return [dot(row, x) for row in a]


def transpose(a):
    return list(map(list, zip(*a)))


def mm(a, b):
    return [[dot(row, col) for col in zip(*b)] for row in a]


def solve(a, b):
    """Exact Gaussian elimination, independent of printed normal equations."""
    n = len(a)
    z = [[F(v) for v in row] + [F(value)] for row, value in zip(a, b)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if z[i][j])
        z[j], z[pivot] = z[pivot], z[j]
        scale = z[j][j]
        z[j] = [v/scale for v in z[j]]
        for i in range(n):
            if i != j:
                scale = z[i][j]
                z[i] = [u-scale*v for u, v in zip(z[i], z[j])]
    return [row[-1] for row in z]


def fit(a, b):
    at = transpose(a)
    theta = solve(mm(at, a), mv(at, b))
    errors = sub(mv(a, theta), b)
    return theta, errors, dot(errors, errors)


def sigmoid(z):
    if z >= 0:
        return 1/(1+math.exp(-z))
    e = math.exp(z)
    return e/(1+e)


def logistic(z, y):
    t = (1-2*y)*z
    return max(t, 0)+math.log1p(math.exp(-abs(t)))


def network(theta, x, y):
    w, b, v, c = theta
    z = w*x+b
    h = max(z, 0)
    s = v*h+c
    return z, h, s, (s-y)**2/2


def finite_gradient(fun, theta, eps=1e-6):
    out = []
    for j in range(len(theta)):
        left, right = list(map(float, theta)), list(map(float, theta))
        left[j] -= eps
        right[j] += eps
        out.append((fun(right)-fun(left))/(2*eps))
    return out


def main():
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    fragments = list(data['additions'].values())+[data['chapter']]
    tasks = [t for c in fragments for t in c['tasks']]
    expected = {f'review-ml-c26-{n:02d}' for n in range(1, 5)}
    expected |= {f'review-ml-c27-{n:02d}' for n in range(1, 3)}
    expected |= {f'review-ml-{n:02d}' for n in range(1, 21)}
    assert len(tasks) == 26 and {t['uid'] for t in tasks} == expected
    assert data['chapter']['id'] == 'ml-foundations'
    anchors = []
    for fragment in fragments:
        theory = fragment['theory']
        assert theory.count(r'\begin{theorem}') == theory.count(r'\end{theorem}')
        assert theory.count(r'\begin{proof}') == theory.count(r'\end{proof}')
        for start, end in fragment['art_anchors']:
            assert theory.count(start) == 1
            paragraph = start+theory.split(start, 1)[1].split(end, 1)[0]
            count = len(paragraph.split())
            assert 90 <= count <= 150
            assert r'\begin{' not in paragraph
            anchors.append({'start': start, 'words': count})
    assert len(anchors) == 5

    uid = 'review-ml-c26-01'
    a, b, p = [1, 1, 0], [3, 1, 2], [2, 2, 0]
    r = sub(b, p)
    check(uid, dot(a, r) == 0 and dot(r, r) == 6)
    for t in [F(-2), F(0), F(1), F(2), F(5)]:
        v = [t*x for x in a]
        check(uid, dot(sub(b, v), sub(b, v)) >= 6)

    uid = 'review-ml-c26-02'
    v1, v2 = [1, 1, 0], [1, 0, 1]
    q1 = [v/math.sqrt(2) for v in v1]
    q2 = [v/math.sqrt(6) for v in [1, -1, 2]]
    check(uid, close(dot(q1, q1), 1) and close(dot(q2, q2), 1))
    check(uid, close(dot(q1, q2), 0))
    u2 = sub(v2, [F(1, 2)*v for v in v1])
    check(uid, u2 == [F(1, 2), F(-1, 2), 1])
    check(uid, all(close(x, y/math.sqrt(F(3, 2))) for x, y in zip(q2, u2)))

    uid = 'review-ml-c26-03'
    a, b = [[1, 0], [1, 1], [1, 2]], [1, 2, 4]
    theta, r, error = fit(a, b)
    check(uid, theta == [F(5, 6), F(3, 2)] and error == F(1, 6))
    check(uid, mv(transpose(a), r) == [0, 0])

    uid = 'review-ml-c26-04'
    a, b = [[1, 1], [2, 2]], [1, 0]
    for t in [F(-7), F(-1, 3), F(0), F(1, 5), F(8)]:
        theta = [t, F(1, 5)-t]
        predicted = mv(a, theta)
        r = sub(predicted, b)
        check(uid, predicted == [F(1, 5), F(2, 5)])
        check(uid, dot(r, r) == F(4, 5) and mv(transpose(a), r) == [0, 0])

    uid = 'review-ml-c27-01'
    a = [[-5, 0], [0, 2]]
    u, sigma, v = [[-1, 0], [0, 1]], [[5, 0], [0, 2]], [[1, 0], [0, 1]]
    check(uid, mm(mm(u, sigma), transpose(v)) == a)
    check(uid, mm(transpose(a), a) == [[25, 0], [0, 4]])
    difference = sub([x for row in a for x in row], [-5, 0, 0, 0])
    check(uid, dot(difference, difference) == 4)

    uid = 'review-ml-c27-02'
    x = [[2, 0], [-2, 0], [0, 1], [0, -1]]
    xtx = mm(transpose(x), x)
    check(uid, xtx == [[8, 0], [0, 2]])
    check(uid, F(8, 8+2) == F(4, 5))
    check(uid, sum(row[1]**2 for row in x) == 2)
    for i in range(101):
        angle = i*math.pi/50
        direction = [math.cos(angle), math.sin(angle)]
        check(uid, dot(mv(x, direction), mv(x, direction))/4 <= 2+1e-12)

    uid = 'review-ml-01'
    residuals = [2*x+1-y for x, y in [(0, 1), (1, 2)]]
    check(uid, residuals == [0, 1] and F(dot(residuals, residuals), 4) == F(1, 4))

    uid = 'review-ml-02'
    t = F(0)-F(1, 4)*4*(0-3)
    check(uid, t == 3 and 2*(t-3)**2 == 0 and 2*(0-3)**2 == 18)

    uid = 'review-ml-03'
    for eta in [F(1, 100), F(1, 4), F(49, 100)]:
        check(uid, abs(1-4*eta) < 1)
    t, trajectory = F(1), []
    for _ in range(4):
        trajectory.append(t)
        t -= F(1, 2)*4*t
    check(uid, trajectory == [1, -1, 1, -1])

    uid = 'review-ml-04'
    x, y, eta = F(2), F(1), F(1, 4)
    x, y = x-eta*x, y-eta*4*y
    check(uid, (x, y) == (F(3, 2), 0) and x*x/2+2*y*y == F(9, 8))

    uid = 'review-ml-05'
    x, y, eta = F(0), F(1), F(3, 4)
    x, y = x-eta*x, y-eta*4*y
    check(uid, (x, y) == (0, -2) and x*x/2+2*y*y == 8)

    uid = 'review-ml-06'
    a, y = [[1, 1], [2, 1]], [1, 2]
    direct = lambda t: dot(sub(mv(a, t), y), sub(mv(a, t), y))/4
    g = finite_gradient(direct, [0, 0])
    check(uid, close(direct([0, 0]), F(5, 4)))
    check(uid, all(close(q, r) for q, r in zip(g, [F(-5, 2), F(-3, 2)])))
    check(uid, [F(1, 10)*q for q in [F(5, 2), F(3, 2)]] == [F(1, 4), F(3, 20)])

    uid = 'review-ml-07'
    theta, r, error = fit([[0, 1], [1, 1]], [1, 3])
    check(uid, theta == [2, 1] and error == 0)

    uid = 'review-ml-08'
    for w in [F(-2), F(0), F(7, 3)]:
        predicted = mv([[1, 1], [1, 1]], [w, 2-w])
        r = sub(predicted, [1, 3])
        check(uid, predicted == [2, 2] and dot(r, r)/4 == F(1, 2))

    uid = 'review-ml-09'
    check(uid, all(close(sigmoid(z), p) for z, p in [(0, F(1, 2)), (math.log(3), F(3, 4)), (-math.log(3), F(1, 4))]))

    uid = 'review-ml-10'
    z, eps = math.log(3), 1e-6
    derivative = (sigmoid(z+eps)-sigmoid(z-eps))/(2*eps)
    check(uid, close(derivative, F(3, 16)))
    for y, expected_gradient in [(1, F(-1, 4)), (0, F(3, 4))]:
        derivative = (logistic(z+eps, y)-logistic(z-eps, y))/(2*eps)
        check(uid, close(derivative, expected_gradient))

    uid = 'review-ml-11'
    check(uid, close(logistic(0, 1), math.log(2)))
    check(uid, close(logistic(math.log(3), 1), math.log(F(4, 3))))
    check(uid, close(logistic(math.log(3), 0), math.log(4)))

    uid = 'review-ml-12'
    for z in [-1e6, -1000, -100, 0, 100, 1000, 1e6]:
        for y in [0, 1]:
            check(uid, math.isfinite(logistic(z, y)) and logistic(z, y) >= 0)
        check(uid, 0 <= sigmoid(z) <= 1)
        check(uid, close(sigmoid(z)+sigmoid(-z), 1))
    check(uid, logistic(1000, 0) == 1000 and logistic(1000, 1) == 0)
    # The last zero is floating-point underflow, not an exact zero of the loss.
    for z in [1, 5]:
        check(uid, 0 < logistic(z, 1) < math.exp(-z))
    # At z=100 the strict analytic difference is below float resolution.
    check(uid, 0 < logistic(100, 1) <= math.exp(-100))

    uid = 'review-ml-13'
    loss = lambda t: logistic(2*t[0]+t[1], 1)
    gradient = finite_gradient(loss, [0, 0])
    check(uid, all(close(a, b) for a, b in zip(gradient, [-1, F(-1, 2)])))
    theta = [F(1, 5), F(1, 10)]
    check(uid, 2*theta[0]+theta[1] == F(1, 2) and loss(theta) < loss([0, 0]))

    uid = 'review-ml-14'
    relu = lambda z: max(z, 0)
    check(uid, [relu(z) for z in [-2, 0, 3]] == [0, 0, 3])
    eps = 1e-6
    check(uid, (relu(0)-relu(-eps))/eps == 0 and (relu(eps)-relu(0))/eps == 1)

    uid = 'review-ml-15'
    check(uid, all(logistic(z, 1) > 0 for z in [-10, 0, 10, 100]))
    check(uid, logistic(100, 1) < logistic(10, 1) < logistic(0, 1))
    # The nonattainment proof is analytic and manually checked in the answer.

    uid = 'review-ml-16'
    check(uid, network([2, 3, -2, 1], -1, 0) == (1, 1, -1, F(1, 2)))

    uid = 'review-ml-17'
    theta, x, y = [2, 1, -1, 2], 1, 0
    check(uid, network(theta, x, y) == (3, 3, -1, F(1, 2)))
    g = finite_gradient(lambda t: network(t, x, y)[-1], theta)
    check(uid, all(close(a, b) for a, b in zip(g, [1, 1, -3, -1])))

    uid = 'review-ml-18'
    theta, x, y = [-1, 0, 3, 1], 1, 2
    check(uid, network(theta, x, y) == (-1, 0, 1, F(1, 2)))
    g = finite_gradient(lambda t: network(t, x, y)[-1], theta)
    check(uid, all(close(a, b) for a, b in zip(g, [0, 0, 0, -1])))

    uid = 'review-ml-19'
    for x in [F(-2), F(0), F(1, 7), F(10)]:
        check(uid, 3*(2*x+1)-4 == 6*x-1)
    a, b = [[1, 2], [0, 1]], [[3, 0], [1, -1]]
    bias1, bias2, x = [2, -1], [1, 4], [5, 2]
    left = [q+r for q, r in zip(mv(b, [u+v for u, v in zip(mv(a, x), bias1)]), bias2)]
    right = [q+r+s for q, r, s in zip(mv(mm(b, a), x), mv(b, bias1), bias2)]
    check(uid, left == right)

    uid = 'review-ml-20'
    train = [F(2), F(4)]
    mean = sum(train)/len(train)
    variance = sum((x-mean)**2 for x in train)/len(train)
    check(uid, mean == 3 and variance == 1 and (10-mean) == 7)
    check(uid, F(1, 10) < F(1, 2) and F(1, 100) < F(5, 100))

    # Additional calculations in the theory: they are not exercise-count padding.
    extra = 'worked-examples'
    q1 = [1/math.sqrt(2), 0, 1/math.sqrt(2)]
    q2 = [-1/math.sqrt(6), 2/math.sqrt(6), 1/math.sqrt(6)]
    b = [1, 1, 0]
    p = [dot(b, q1)*a+dot(b, q2)*c for a, c in zip(q1, q2)]
    check(extra, all(close(a, b) for a, b in zip(p, [F(1, 3), F(1, 3), F(2, 3)])))
    check(extra, close(dot(sub(b, p), sub(b, p)), F(4, 3)))
    theta, _, error = fit([[1, -1], [1, 0], [1, 1]], [0, 1, 3])
    check(extra, theta == [F(4, 3), F(3, 2)] and error == F(1, 6))
    theta, _, error = fit([[0, 1], [1, 1], [2, 1]], [1, 2, 2])
    check(extra, theta == [F(1, 2), F(7, 6)] and error/6 == F(1, 36))
    initial = [F(1), F(-1), F(3), F(0)]
    check(extra, network(initial, 2, 1) == (1, 1, 3, 2))
    gradient = finite_gradient(lambda t: network(t, 2, 1)[-1], initial)
    check(extra, all(close(a, b) for a, b in zip(gradient, [12, 6, 2, 2])))
    after = [v-F(1, 100)*g for v, g in zip(initial, [12, 6, 2, 2])]
    z, _, s, loss = network(after, 2, 1)
    check(extra, z == F(7, 10) and s == F(1033, 500) and loss == F(284089, 500000))

    assert set(CHECKS)-{'worked-examples'} == expected
    result = {
        'date': '2026-10-25', 'status': 'passed', 'tasks': len(tasks),
        'assertions': sum(CHECKS.values()), 'checks_per_uid': CHECKS,
        'source': str(SOURCE.relative_to(ROOT)),
        'sha256': hashlib.sha256(raw).hexdigest(), 'art_anchors': anchors,
        'scope_note': 'Manual mathematical review plus exact independent recalculation and finite differences. LaTeX is not executed; finite checks are not proofs of convergence or generalization.',
        'qualitative_review': ['SVD existence scope explicit', 'Rank-deficient least squares', 'ReLU has no derivative at zero', 'No finite logistic minimizer in the separating one-point example', 'Training-only preprocessing and validation/test distinction'],
    }
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(f'PASS: {len(tasks)} tasks, {result["assertions"]} assertions, 5 prose anchors.')
    print(RESULT)


if __name__ == '__main__':
    main()
