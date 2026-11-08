# Stress test for the Eertree template (../strings/Eertree.py) against brute force, for every subset of ops:
# python3 test_eertree.py
import os, random, itertools, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eertree_strip import strip, MARK

SRC = open(os.path.join(HERE, "..", "strings", "Eertree.py")).read()
QUERIES = ["leftmostLForPalEndingAtR", "leftmostLForPalEndingAtEachR", "rightmostRForPalStartingAtL", "rightmostRForPalStartingAtEachL",
           "numDistinctPalsInPrefixEndingAtEachR", "numPalsEndingAtEachR", "numDistinctPals", "numDistinctPalsInPrefixEndingAtR",
           "numPalsEndingAtR", "numPalsTotal", "distinctPalsWithCounts", "minPalPartition", "longestPalEndingAtCurrentR",
           "longestPalStartingAtCurrentL", "longestPal", "numPalsEndingAtCurrentR", "numPalsStartingAtCurrentL"]
MUTATIONS = ["append", "pop"]

isPal = lambda t: list(t) == list(t)[::-1]


def check(t, seq, chosen):
    n = len(seq)
    pals = lambda a, b: isPal(seq[a:b + 1])
    want = [min(l for l in range(r + 1) if pals(l, r)) for r in range(n)]
    if "leftmostLForPalEndingAtEachR" in chosen:
        assert t.leftmostLForPalEndingAtEachR() == want
    if "leftmostLForPalEndingAtR" in chosen:
        assert all(t.leftmostLForPalEndingAtR(r) == want[r] for r in range(n))
    want = [max(r for r in range(l, n) if pals(l, r)) for l in range(n)]
    if "rightmostRForPalStartingAtEachL" in chosen:
        assert t.rightmostRForPalStartingAtEachL() == want
    if "rightmostRForPalStartingAtL" in chosen:
        assert all(t.rightmostRForPalStartingAtL(l) == want[l] for l in range(n))
    distinct = lambda m: len({tuple(seq[a:b + 1]) for a in range(m) for b in range(a, m) if pals(a, b)})
    if "numDistinctPals" in chosen:
        assert t.numDistinctPals() == distinct(n)
    want = [distinct(r + 1) for r in range(n)]
    if "numDistinctPalsInPrefixEndingAtEachR" in chosen:
        assert t.numDistinctPalsInPrefixEndingAtEachR() == want
    if "numDistinctPalsInPrefixEndingAtR" in chosen:
        assert all(t.numDistinctPalsInPrefixEndingAtR(r) == want[r] for r in range(n))
    want = [sum(pals(l, r) for l in range(r + 1)) for r in range(n)]
    if "numPalsEndingAtEachR" in chosen:
        assert t.numPalsEndingAtEachR() == want
    if "numPalsEndingAtR" in chosen:
        assert all(t.numPalsEndingAtR(r) == want[r] for r in range(n))
    if "numPalsTotal" in chosen:
        assert t.numPalsTotal() == sum(pals(a, b) for a in range(n) for b in range(a, n))
    if "distinctPalsWithCounts" in chosen:
        got = t.distinctPalsWithCounts()
        want = {}
        for a in range(n):
            for b in range(a, n):
                if pals(a, b):
                    key = tuple(seq[a:b + 1])
                    if key not in want:
                        want[key] = [a, b, 0]
                    want[key][2] += 1
        assert sorted(got) == sorted(tuple(v) for v in want.values()), (seq, got)
    if "longestPalEndingAtCurrentR" in chosen:
        assert t.longestPalEndingAtCurrentR() == max([n - l for l in range(n) if pals(l, n - 1)], default=0)
    if "longestPalStartingAtCurrentL" in chosen:
        assert t.longestPalStartingAtCurrentL() == max([r + 1 for r in range(n) if pals(0, r)], default=0)
    if "longestPal" in chosen:
        assert t.longestPal() == max([b - a + 1 for a in range(n) for b in range(a, n) if pals(a, b)], default=0)
    if "numPalsEndingAtCurrentR" in chosen:
        assert t.numPalsEndingAtCurrentR() == sum(pals(l, n - 1) for l in range(n))
    if "numPalsStartingAtCurrentL" in chosen:
        assert t.numPalsStartingAtCurrentL() == sum(pals(0, r) for r in range(n))
    if "minPalPartition" in chosen:
        dp = [0] + [10**9] * n
        for b in range(1, n + 1):
            dp[b] = min(dp[a] + 1 for a in range(b) if pals(a, b - 1))
        assert t.minPalPartition() == dp[n]


def randItem(kind, sigma):
    v = random.randrange(sigma)
    return chr(97 + v) if kind == "str" else (v - 1 if kind == "list" else (v, -v))


subsets = 0
LINKS = ["quickLinks", "itemLinks", "persistentLinks"]  # which link structure append uses when pop is in too
for mut, linkTag in [(m, tag) for m in itertools.chain.from_iterable(itertools.combinations(MUTATIONS, k) for k in range(3))
                     for tag in (LINKS if len(m) == 2 else [None])]:
    for qmask in [0, (1 << len(QUERIES)) - 1] + [random.randrange(1 << len(QUERIES)) for _ in range(1500)]:
        chosen = set(mut) | {QUERIES[b] for b in range(len(QUERIES)) if qmask >> b & 1} | ({linkTag} if linkTag else set())
        code = strip(SRC, chosen)
        assert not any(MARK.match(line) for line in code.split("\n"))
        env = {}
        exec(code, env)
        E = env["Eertree"]
        for name in ["append", "pop"] + QUERIES:
            assert hasattr(E, name) == (name in chosen), (name, chosen)
        subsets += 1
        if random.random() < 0.9 and len(mut) < 2 and qmask != (1 << len(QUERIES)) - 1:
            continue  # spot-check most subsets by structure only; run brute force on a spread of them
        for _ in range(15):
            kind = random.choice(["str", "list", "tuple"])
            sigma = random.choice([1, 2, 3, 26])
            init = [randItem(kind, sigma) for _ in range(random.randint(0, 10))]
            start = "".join(init) if kind == "str" else (init if kind == "list" else tuple(init))
            t = E(start)
            seq = list(init)
            check(t, seq, chosen)
            for _ in range(random.randint(0, 25)):
                if "pop" in chosen and seq and random.random() < 0.45:
                    assert t.pop() == seq.pop()
                elif "append" in chosen:
                    x = randItem(kind, sigma)
                    t.append(x)
                    seq.append(x)
                else:
                    break
                check(t, seq, chosen)
print("eertree ok:", subsets, "op subsets")

# the double-ended eertree, for every subset of its ops
DSRC = open(os.path.join(HERE, "..", "strings", "DoubleEndedEertree.py")).read()
DOPS = ["append", "appendLeft", "numDistinctPals", "numPalsTotal", "longestPalEndingAtCurrentR", "longestPalStartingAtCurrentL",
        "longestPal", "numPalsEndingAtCurrentR", "numPalsStartingAtCurrentL"]
for mask in range(1 << len(DOPS)):
    chosen = {DOPS[b] for b in range(len(DOPS)) if mask >> b & 1}
    env = {}
    exec(strip(DSRC, chosen), env)
    D = env["DoubleEndedEertree"]
    for name in DOPS:
        assert hasattr(D, name) == (name in chosen), (name, chosen)
    for _ in range(40):
        kind = random.choice(["str", "list", "tuple"])
        sigma = random.choice([1, 2, 3, 26])
        init = [randItem(kind, sigma) for _ in range(random.randint(0, 8))]
        t = D("".join(init) if kind == "str" else (init if kind == "list" else tuple(init)))
        seq = list(init)
        for step in range(random.randint(0, 30)):
            n = len(seq)
            pals = lambda a, b: isPal(seq[a:b + 1])
            if "numDistinctPals" in chosen:
                assert t.numDistinctPals() == len({tuple(seq[a:b + 1]) for a in range(n) for b in range(a, n) if pals(a, b)})
            if "numPalsTotal" in chosen:
                assert t.numPalsTotal() == sum(pals(a, b) for a in range(n) for b in range(a, n))
            if "longestPalEndingAtCurrentR" in chosen:
                assert t.longestPalEndingAtCurrentR() == max([n - l for l in range(n) if pals(l, n - 1)], default=0)
            if "longestPalStartingAtCurrentL" in chosen:
                assert t.longestPalStartingAtCurrentL() == max([r + 1 for r in range(n) if pals(0, r)], default=0)
            if "longestPal" in chosen:
                assert t.longestPal() == max([b - a + 1 for a in range(n) for b in range(a, n) if pals(a, b)], default=0)
            if "numPalsEndingAtCurrentR" in chosen:
                assert t.numPalsEndingAtCurrentR() == sum(pals(l, n - 1) for l in range(n))
            if "numPalsStartingAtCurrentL" in chosen:
                assert t.numPalsStartingAtCurrentL() == sum(pals(0, r) for r in range(n))
            moves = [m for m in ("append", "appendLeft") if m in chosen]
            if not moves:
                break
            x = randItem(kind, sigma)
            if random.choice(moves) == "append":
                t.append(x)
                seq.append(x)
            else:
                t.appendLeft(x)
                seq.insert(0, x)
print("double-ended eertree ok:", 1 << len(DOPS), "op subsets")
