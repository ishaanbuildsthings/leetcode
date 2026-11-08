# Stress tests for the single-function string templates (../strings) against brute force: python3 test_strings.py
import os, random

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["minRotation", "maxRotation", "minRotationIndices", "maxRotationIndices", "zFunction",
         "longestPrefixMatches", "findMatches", "properBorders", "shortestPeriod"]
F = {}
_env = {}
exec(open(os.path.join(HERE, "..", "strings", "shortestPeriod.overflow.py")).read(), _env)
OVERFLOW_PERIOD = _env["shortestPeriod"]
for name in NAMES:
    env = {}
    exec(open(os.path.join(HERE, "..", "strings", name + ".py")).read(), env)
    F[name] = env[name]


def rotations(s):
    return [s[i:] + s[:i] for i in range(len(s))]


def lcp(a, b):
    k = 0
    while k < len(a) and k < len(b) and a[k] == b[k]:
        k += 1
    return k


def randSeq():
    n = random.choice([0, 1, 2, 3, random.randint(0, 12), random.randint(0, 40)])
    sigma = random.choice([1, 2, 3, 26])
    if random.random() < 0.3:  # periodic
        base = [random.randrange(sigma) for _ in range(random.randint(1, 4))]
        seq = (base * (n // len(base) + 1))[:n]
    else:
        seq = [random.randrange(sigma) for _ in range(n)]
    kind = random.choice(["str", "list", "tuple"])
    if kind == "str":
        return "".join(chr(97 + x) for x in seq)
    return seq if kind == "list" else tuple(seq)


cases = 0
for it in range(20000):
    cases += 1
    s = randSeq()
    n = len(s)
    rots = rotations(s)
    if n:
        lo, hi = min(rots), max(rots)
        assert F["minRotation"](s) == lo, s
        assert F["maxRotation"](s) == hi, s
        assert F["minRotationIndices"](s) == [i for i in range(n) if rots[i] == lo], s
        assert F["maxRotationIndices"](s) == [i for i in range(n) if rots[i] == hi], s
    else:
        assert F["minRotation"](s) == s and F["maxRotationIndices"](s) == []
    assert F["zFunction"](s) == [lcp(s, s[i:]) for i in range(n)], s
    assert F["properBorders"](s) == [max([k for k in range(i + 1) if s[:k] == s[i - k + 1 : i + 1]]) for i in range(n)], s
    want = n
    for p in range(1, n + 1):
        if n % p == 0 and s[:p] * (n // p) == s:
            want = p
            break
    assert F["shortestPeriod"](s) == (0 if n == 0 else want), s
    wantOverflow = next((p for p in range(1, n + 1) if all(s[i] == s[i + p] for i in range(n - p))), 0)
    assert OVERFLOW_PERIOD(s) == wantOverflow, s
    t = randSeq()
    if type(t) != type(s):
        t = type(s)(t) if not isinstance(s, str) else "".join(chr(97 + x) if isinstance(x, int) else x for x in t)
    # text = s, pattern = t (also often a piece of s)
    if n and random.random() < 0.5:
        a = random.randint(0, n - 1)
        t = s[a : a + random.randint(0, n - a)]
    assert F["longestPrefixMatches"](s, t) == [lcp(t, s[i:]) for i in range(n)], (s, t)
    want = [i for i in range(n + 1) if s[i : i + len(t)] == t and i + len(t) <= n]
    assert F["findMatches"](s, t) == want, (s, t)
print("all string templates ok:", cases, "random cases")
