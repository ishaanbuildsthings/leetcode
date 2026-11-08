# Stress tests XorBasis.py and RangeXorBasis.py against brute force. Run: python3 test_basis.py
import os, random
from itertools import combinations
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "bit-operations")
ns = {}
for f in ("XorBasis.py", "RangeXorBasis.py"):
    exec(open(os.path.join(SRC, f)).read(), ns)
XorBasis, RangeXorBasis = ns["XorBasis"], ns["RangeXorBasis"]
MOD = 10**9 + 7

def subsetXors(vals):  # list of XORs of every subset by position, the empty one included
    res = [0]
    for x in vals:
        res += [y ^ x for y in res]
    return res

def checkBasis(basis, vals, rng, hi):
    allXors = subsetXors(vals)
    span = sorted(set(allXors))
    assert basis.size() == len(vals)
    assert basis.countDistinctXors() == len(span)
    assert sorted(set(subsetXors(basis.basis()))) == span
    assert basis.basis() == sorted(basis.basis(), reverse=True)
    assert basis.rank() == len(basis.basis())
    assert basis.maxXor() == span[-1]
    for k in range(len(span) + 2):
        assert basis.kthSmallestXor(k) == (span[k] if k < len(span) else None)
    nonempty = allXors[1:]
    assert basis.minNonzeroXor() == (min(nonempty) if nonempty else None)
    for _ in range(10):
        x = rng.randrange(hi * 2)
        assert basis.canMake(x) == (x in set(span))
        assert basis.maxXorWith(x) == max(x ^ s for s in span)
        assert basis.minXorWith(x) == min(x ^ s for s in span)
        assert basis.countSubsetsMakingMod(x, MOD) == allXors.count(x) % MOD

rng = random.Random(1)
for it in range(3000):
    hi = rng.choice([1, 2, 4, 16, 64, 1 << 40])
    basis = XorBasis()
    vals = []
    for _ in range(rng.randrange(0, 10)):
        x = rng.randrange(hi)
        grew = basis.insert(x)
        assert grew == (x not in set(subsetXors(vals)))
        vals.append(x)
    checkBasis(basis, vals, rng, hi)
    assert XorBasis(vals).basis() == basis.basis()
    other = rng.sample(range(hi), min(hi, rng.randrange(0, 5)))
    ob = XorBasis(other)
    basis.merge(ob)
    checkBasis(basis, vals + other, rng, hi)

for it in range(2000):
    hi = rng.choice([1, 2, 8, 32, 1 << 50])
    arr = [rng.randrange(hi) for _ in range(rng.randrange(1, 9))]
    rxb = RangeXorBasis(arr)
    for l in range(len(arr)):
        for r in range(l, len(arr)):
            span = set(subsetXors(arr[l:r + 1]))
            assert rxb.maxXorInRange(l, r) == max(span)
            assert rxb.countDistinctXorsInRange(l, r) == len(span)
            assert rxb.rankInRange(l, r) == len(span).bit_length() - 1
            for _ in range(4):
                x = rng.randrange(hi * 2)
                assert rxb.canMakeInRange(l, r, x) == (x in span)
                assert rxb.maxXorWithInRange(l, r, x) == max(x ^ s for s in span)
    try:
        rxb.maxXorInRange(0, len(arr))
        assert False
    except IndexError:
        pass
print("python basis tests passed")
