"""Independent exact-coordinate checks for the textbook's H/O convention.

These finite checks supplement the manuscript's proofs; they are not proofs.
The quaternion multiplication below uses four real coordinates, independently
of the complex-pair construction used in the text.
"""
from pathlib import Path
import json, random

def add(x,y): return tuple(a+b for a,b in zip(x,y))
def neg(x): return tuple(-a for a in x)
def conjugate(x): return (x[0],)+tuple(-a for a in x[1:])
def norm_squared(x): return sum(a*a for a in x)
def quaternion(x,y):
    a,b,c,d=x; A,B,C,D=y
    return (a*A-b*B-c*C-d*D, a*B+b*A+c*D-d*C,
            a*C-b*D+c*A+d*B, a*D+b*C-c*B+d*A)
def octonion(x,y):
    a,b=x[:4],x[4:]; c,d=y[:4],y[4:]
    return (add(quaternion(a,c),neg(quaternion(conjugate(d),b)))
            +add(quaternion(d,a),quaternion(b,conjugate(c))))

units=[tuple(int(i==j) for i in range(8)) for j in range(8)]
assert octonion(octonion(units[1],units[2]),units[4])==units[7]
assert octonion(units[1],octonion(units[2],units[4]))==neg(units[7])
for k in range(1,8): assert octonion(units[k],units[k])==neg(units[0])
assert octonion((1,0,0,0,0,1,0,0),(0,0,1,0,0,0,0,1))==(0,0,2,0,0,0,0,0)
rng=random.Random(1022)
for _ in range(1000):
    x=tuple(rng.randint(-3,3) for _ in range(8))
    y=tuple(rng.randint(-3,3) for _ in range(8))
    product=octonion(x,y)
    assert norm_squared(product)==norm_squared(x)*norm_squared(y)
    assert conjugate(product)==octonion(conjugate(y),conjugate(x))
    assert octonion(x,conjugate(x))==(norm_squared(x),)+(0,)*7
report=dict(seed=1022,integer_pairs=1000,failed_checks=0,
    convention='(a,b)(c,d)=(ac-conj(d)b, da+b conj(c))',
    checks=['seven basis squares','explicit nonassociativity counterexample',
            'exercise 25.11','norm composition','conjugation reverses product',
            'product with conjugate'],
    limitation='Finite exact checks supplement, and do not replace, the printed proofs.')
root=Path(__file__).resolve().parents[1]
(root/'research/hypercomplex-exact-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
