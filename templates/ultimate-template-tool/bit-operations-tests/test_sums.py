# Stress tests the pair / subarray bit-sum templates against brute force. Run: python3 test_sums.py
import os, random
from functools import reduce
from itertools import combinations
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "bit-operations")
OPS = {"Xor": int.__xor__, "And": int.__and__, "Or": int.__or__}
fns = {}
for kind in ("Pair", "Subarray"):
    for op in OPS:
        for suffix in ("", "Mod"):
            name = f"sumOf{kind}{op}s{suffix}"
            ns = {}
            exec(open(os.path.join(SRC, name + ".py")).read(), ns)
            fns[name] = ns[name]
rng = random.Random(3)
for it in range(3000):
    hi = rng.choice([1, 2, 8, 1000, 1 << 40])
    arr = [rng.randrange(hi) for _ in range(rng.randrange(0, 12))]
    for op, f in OPS.items():
        pair = sum(f(arr[i], arr[j]) for i, j in combinations(range(len(arr)), 2))
        sub = sum(reduce(f, arr[l:r + 1]) for l in range(len(arr)) for r in range(l, len(arr)))
        assert fns[f"sumOfPair{op}s"](arr) == pair
        assert fns[f"sumOfSubarray{op}s"](arr) == sub
        for mod in (10**9 + 7, 7, 1):
            assert fns[f"sumOfPair{op}sMod"](arr, mod) == pair % mod
            assert fns[f"sumOfSubarray{op}sMod"](arr, mod) == sub % mod
print("python sums tests passed")
