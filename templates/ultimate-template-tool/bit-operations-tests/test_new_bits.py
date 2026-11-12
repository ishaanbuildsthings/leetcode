# Stress tests XorBasisDeletable.py, the two-group partitions and the arr submask / supermask sums against brute force.
# Run: python3 test_new_bits.py
import os, random
from functools import reduce
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "bit-operations")
ns = {}
for f in ("XorBasisDeletable", "XorBasis", "maxTwoGroupXorSum", "maxTwoGroupAndSum", "countSubmasksForAllMasks",
          "sumSubmasksForAllMasks", "countSupermasksForAllMasks", "sumSupermasksForAllMasks"):
    exec(open(os.path.join(SRC, f + ".py")).read(), ns)
rng = random.Random(11)
MOD = 10**9 + 7


def span(vals):
    s = {0}
    for v in vals:
        s |= {x ^ v for x in s}
    return s


# ---- XorBasisDeletable: random inserts and deletes, every query checked after every step
for trial in range(400):
    bits = rng.randrange(1, 7)
    held = [rng.randrange(1 << bits) for _ in range(rng.randrange(6))] if trial % 3 == 0 else []
    b = ns["XorBasisDeletable"](held)
    for step in range(rng.randrange(1, 60)):
        r = rng.random()
        if r < 0.55 or not held:
            v = rng.randrange(1 << bits) if rng.random() < 0.8 else rng.choice(held or [0])
            grew = b.insert(v)
            assert grew == (v not in span(held)), (held, v)
            held.append(v)
        elif r < 0.9:
            v = rng.choice(held)
            assert b.remove(v)
            held.remove(v)
        else:
            v = rng.randrange(1 << bits)
            assert b.remove(v) == (v in held)
            if v in held:
                held.remove(v)
        s = span(held)
        rank = len(s).bit_length() - 1
        assert b.size() == len(held) and b.rank() == rank and b.countDistinctXors() == len(s)
        assert span(b.basis()) == s and len(b.basis()) == rank and b.basis() == sorted(b.basis(), reverse=True)
        assert b.maxXor() == max(s)
        x = rng.randrange(1 << bits)
        assert b.canMake(x) == (x in s)
        assert b.maxXorWith(x) == max(x ^ y for y in s) and b.minXorWith(x) == min(x ^ y for y in s)
        assert b.minNonzeroXor() == (None if not held else 0 if len(held) > rank else min(s - {0}))
        ordered = sorted(s)
        for k in range(len(ordered) + 2):
            assert b.kthSmallestXor(k) == (ordered[k] if k < len(ordered) else None)
        assert b.countSubsetsMakingMod(x, MOD) == (pow(2, len(held) - rank, MOD) if x in s else 0)

# big values, many operations: the rank and max XOR against XorBasis rebuilt from what is held
for trial in range(30):
    held, b = [], ns["XorBasisDeletable"]()
    pool = [rng.randrange(1 << 60) for _ in range(rng.randrange(1, 80))]
    for step in range(400):
        if held and rng.random() < 0.45:
            v = rng.choice(held)
            b.remove(v)
            held.remove(v)
        else:
            v = rng.choice(pool) if rng.random() < 0.7 else reduce(lambda a, c: a ^ c, rng.sample(pool, min(3, len(pool))))
            b.insert(v)
            held.append(v)
        ref = ns["XorBasis"](held)
        assert b.rank() == ref.rank() and b.maxXor() == ref.maxXor() and b.basis() == ref.basis()

# ---- two-group partitions: every split of small arrays
for trial in range(3000):
    n = rng.randrange(2, 9)
    arr = [rng.randrange(rng.choice([2, 4, 16, 64])) for _ in range(n)]
    xs, ands = [], []
    for mask in range(1, (1 << n) - 1):
        A = [arr[i] for i in range(n) if mask >> i & 1]
        B = [arr[i] for i in range(n) if not mask >> i & 1]
        xs.append(reduce(lambda a, c: a ^ c, A) + reduce(lambda a, c: a ^ c, B))
        ands.append(reduce(lambda a, c: a & c, A) + reduce(lambda a, c: a & c, B))
    assert ns["maxTwoGroupXorSum"](arr) == max(xs), arr
    assert ns["maxTwoGroupAndSum"](arr) == max(ands), arr
assert ns["maxTwoGroupAndSum"]([3, 3, 4, 4]) == 7 and ns["maxTwoGroupXorSum"]([1, 2, 3]) == 6
for fn in ("maxTwoGroupXorSum", "maxTwoGroupAndSum"):
    for bad in ([5], [], [1, -2]):
        try:
            ns[fn](bad)
            assert False, (fn, bad)
        except ValueError:
            pass

# ---- submask / supermask counts and sums of arr's values, for every mask
for trial in range(1500):
    arr = [rng.randrange(rng.choice([1, 2, 8, 33])) for _ in range(rng.randrange(0, 12))]
    size = 1 << max(arr, default=0).bit_length()
    sub = [[v for v in arr if v & m == v] for m in range(size)]
    sup = [[v for v in arr if v & m == m] for m in range(size)]
    assert ns["countSubmasksForAllMasks"](arr) == [len(x) for x in sub]
    assert ns["sumSubmasksForAllMasks"](arr) == [sum(x) for x in sub]
    assert ns["countSupermasksForAllMasks"](arr) == [len(x) for x in sup]
    assert ns["sumSupermasksForAllMasks"](arr) == [sum(x) for x in sup]
try:
    ns["countSubmasksForAllMasks"]([1, -1])
    assert False
except ValueError:
    pass
print("XorBasisDeletable, two-group partitions and submask / supermask sums: all agree with brute force")
