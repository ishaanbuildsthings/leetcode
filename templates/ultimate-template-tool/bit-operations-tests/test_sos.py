# Stress tests the SOS DP and convolution templates against brute force. Run: python3 test_sos.py
import os, random
from itertools import combinations
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "bit-operations")
NAMES = ["subsetSums", "supersetSums", "countSubsetsByAnd", "countSubsetsByOr", "countPairsByAnd", "countPairsByOr",
         "orConvolution", "andConvolution", "xorConvolution", "xorConvolutionMod", "countPairsByXor"]
fns = {}
for name in NAMES:
    ns = {}
    exec(open(os.path.join(SRC, name + ".py")).read(), ns)
    fns[name] = ns[name]
rng = random.Random(2)

def size(arr):
    return 1 << max(arr, default=0).bit_length()

for it in range(600):
    B = rng.randrange(0, 7)
    n = 1 << B
    f = [rng.randrange(-50, 50) for _ in range(n)]
    g = [rng.randrange(-50, 50) for _ in range(n)]
    assert fns["subsetSums"](f) == [sum(f[s] for s in range(n) if s & m == s) for m in range(n)]
    assert fns["supersetSums"](f) == [sum(f[s] for s in range(n) if s & m == m) for m in range(n)]
    for name, op in (("orConvolution", int.__or__), ("andConvolution", int.__and__), ("xorConvolution", int.__xor__)):
        want = [0] * n
        for i in range(n):
            for j in range(n):
                want[op(i, j)] += f[i] * g[j]
        assert fns[name](f, g) == want, name
        if name == "xorConvolution":
            for mod in (7, 10**9 + 7, 1):
                assert fns["xorConvolutionMod"](f, g, mod) == [x % mod for x in want]
    arr = [rng.randrange(rng.choice([1, 2, 5, 16, 40])) for _ in range(rng.randrange(0, 9))]
    m = size(arr)
    for name, op in (("countPairsByAnd", int.__and__), ("countPairsByOr", int.__or__), ("countPairsByXor", int.__xor__)):
        want = [0] * m
        for i, j in combinations(range(len(arr)), 2):
            want[op(arr[i], arr[j])] += 1
        assert fns[name](arr) == want, (name, arr)
    for name, op in (("countSubsetsByAnd", int.__and__), ("countSubsetsByOr", int.__or__)):
        for mod in (10**9 + 7, 5):
            want = [0] * m
            for mask in range(1, 1 << len(arr)):
                acc = None
                for i in range(len(arr)):
                    if mask >> i & 1:
                        acc = arr[i] if acc is None else op(acc, arr[i])
                want[acc] += 1
            assert fns[name](arr, mod) == [x % mod for x in want], (name, arr)
for bad in ([1, 2, 3], []):
    try:
        fns["subsetSums"](bad)
        assert False
    except ValueError:
        pass
try:
    fns["xorConvolutionMod"]([1, 2], [3, 4], 10)
    assert False
except ValueError:
    pass
# docstring examples
assert fns["andConvolution"]([1, 2], [3, 4]) == [13, 8]
assert fns["countSubsetsByOr"]([1, 2, 3], 10**9 + 7) == [0, 1, 1, 5]
print("python sos tests passed")
