"""Test every range-query template, in every language it has, against a brute force.

For each folder in templates/ultimate-template-tool/range-queries, the @operations header says what the template supports. This script
replays random op sequences on a plain Python list (the brute force below knows every op) and checks that
template.py and template.cpp give the same answers. Nothing here is per-template: a new template is covered as
soon as its ops are in BRUTE_UPDATES / BRUTE_QUERIES.

    python3 test_templates.py                 # everything
    python3 test_templates.py rangeGcd beats  # only folders whose name contains one of these
    python3 test_templates.py --py            # Python only (no compiler needed)
    python3 test_templates.py --cpp           # C++ only
    python3 test_templates.py --cpp --fast    # the fast.cpp versions, C++ only
    python3 test_templates.py --trials 300    # more random sequences per template (default 120)
    python3 test_templates.py --shard 3/16    # every 16th folder from the 3rd (run 16 of these side by side)
    python3 test_templates.py --from f.txt    # exactly the folders listed in f.txt (one per line)

A folder's sparse.py / sparse.cpp (dynamic trees over any index range [lo, hi], all positions starting at 0) are
tested too, as an extra "<folder> [sparse]" line: indices are huge (around +-1e12), and the brute force keeps the
array as constant runs (or, for arithmetic-progression adds, as a list of linear updates summed in closed form).

C++ needs a GCC with bits/stdc++.h: set CXX, or it tries g++-15 ... g++-11, then g++.
Each template.cpp is compiled with T = long long and also explicitly instantiated with T = int.
"""
import bisect
import importlib.util
import inspect
import hashlib
import itertools
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from functools import reduce

sys.dont_write_bytecode = True  # never leave __pycache__ inside a template folder
sys.setrecursionlimit(10000)

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(HERE), "range-queries")
FAST = False  # --fast: run each C++ test on the fast version instead
BUILD = os.path.join(tempfile.gettempdir(), "range-query-template-tests")
OPS_PER_TRIAL = 60

# ------------------------------------------------------------------------------------------------ brute force

POINT_UPDATES = ("pointAssign", "pointAdd", "pointChmax", "pointChmin")
RANGE_UPDATES = {  # op -> number of args after (l, r)
    "rangeAdd": 1, "rangeAssign": 1, "rangeAddMod": 1, "rangeAssignMod": 1, "rangeChmax": 1, "rangeChmin": 1, "rangeMultMod": 1, "rangeAffineMod": 2,
    "stridedAdd": 2, "rangeAddArithSeq": 2, "rangeAddArithSeqMod": 2, "rangeMod": 1, "rangeFloorDiv": 1, "rangeFloorSqrt": 0,
    "rangeAndApply": 1, "rangeOrApply": 1, "rangeXorApply": 1, "rangeFlip": 0, "rangeReplace": 2,
}
# sequence edits (implicit treap): op -> arg kind; they change the array's length
SEQ_OPS = {"append": "v", "appendLeft": "v", "insertAt": "iv", "pop": "none", "popLeft": "none", "eraseRange": "lr", "rangeReverse": "lr", "rangeRotateLeft": "lrk", "rangeRotateRight": "lrk", "moveRange": "lri",
           "cut": "lr", "paste": "ib", "split": "k", "trisect": "lr", "merge": "b", "insertCopiesAt": "ivk",
           "rangeTwinSpin": "lr", "rangeSortAsc": "lr", "rangeSortDesc": "lr", "copyRange": "lrc", "copy": "lr"}
# cut(l, r) hands a[l..r] back as a new structure, which the test keeps on a stack; split(k) / trisect(l, r) hand back
# every part (the structure itself is left empty): the test merges the first part back into it and stacks the rest.
# paste(i, rv) and merge(rv) pop the newest piece, reverse it first when rv (so the piece is used as a structure of its
# own), and put it back in at index i / at the end
PIECE_OPS = ("cut", "paste", "split", "trisect", "merge", "copy")
SEQ_OUT = {"pop", "popLeft"}  # sequence edits that also return something (the removed value)
MOD_OPS = {"rangeMultMod", "rangeAffineMod", "rangeAddArithSeqMod", "rangeAddMod", "rangeAssignMod", "rangeSumMod", "productAllMod"}  # any: values live mod p


# ops that only compare, copy, move or hash values: they make sense on letters (a list of characters), not just numbers.
# --letters reruns every template on order-preserving letters using just these ops (the others do arithmetic).
CHAR_SAFE = {
    "pointGet", "pointAssign", "pointChmax", "pointChmin", "rangeAssign", "rangeChmax", "rangeChmin", "rangeSortAsc",
    "rangeSortDesc", "getAll", "size", "append", "appendLeft", "insertAt", "insertCopiesAt", "pop", "popLeft", "eraseRange",
    "rangeReverse", "rangeRotateLeft", "rangeRotateRight", "moveRange", "cut", "paste", "split", "trisect", "merge",
    "copyRange", "copy", "rangeTwinSpin", "rangeMin", "rangeMax", "minAll", "maxAll", "countDistinct", "allDistinct", "rangeMode", "countOccurrences",
    "leftmostIndexOf", "rightmostIndexOf", "leftmostIndexOfInRange", "rightmostIndexOfInRange", "longestEqualRun", "rangeLIS", "rangeLNDS", "rangeLDS", "rangeLNIS", "isRBS", "rangeFlip", "isPalindrome", "rangeHash",
    "rangeHashReversed", "rangesEqual", "hashAll", "hashAllReversed", "longestPalCenteredAtI", "longestPalCenteredAtIPlusOne", "doAllElementsAppearEvenFrequency", "kthSmallest", "kthLargest", "medianLow",
    "medianHigh", "countLtX", "countLteX", "countGtX", "countGteX", "countInValRange", "smallestGtX", "smallestGteX",
    "largestLtX", "largestLteX", "kthLtX", "kthLteX", "kthGtX", "kthGteX", "rangeReplace",
} | {f"{side}{c}X" for side in ("leftmost", "rightmost") for c in ("Gt", "Gte", "Lt", "Lte")}


LETTER_BASE = int(os.environ.get("LETTER_BASE", 0x4E00))  # LETTER_BASE=91: plain ASCII ("(", digits, capitals, "[", ...)


def letter(v):
    """An order-preserving one-character string for value v (clamped: domains this wide are numbers-only anyway)."""
    if LETTER_BASE < 128:  # ASCII: printable only (33 .. 126), so C++ chars print exactly what Python expects
        return chr(max(33, min(126, LETTER_BASE + v)))
    return chr(LETTER_BASE + max(1 - LETTER_BASE, min(9000, v)))


def char_letter_base(folder, ops):
    """The ASCII LETTER_BASE for a C++ letters run (T = char holds one byte, not '丁'): the template's sampled value
    range shifted into the printable 33 .. 126, or centred there when wider (letter() clamps the rest)."""
    if LETTER_BASE < 128:  # (already ASCII: C++ and Python test the very same letters)
        return LETTER_BASE
    gen, rng = domain(folder, ops)[0], random.Random(0)
    vals = [gen(rng) for _ in range(2000)]
    lo, hi = min(vals), max(vals)
    return 33 - lo if hi - lo <= 93 else 79 - (lo + hi) // 2


def run_cpp_letters(folder, ops, trials_n, ctor_extra, cxx, stem):
    """--letters in C++: fresh trials on ASCII letters (same seeds, same ops), checked against their own brute force"""
    global LETTER_BASE
    saved, LETTER_BASE = LETTER_BASE, char_letter_base(folder, ops)
    try:  # (the brute force reads LETTER_BASE too: the brackets are letter(40) and letter(41))
        trials, ctx = make_trials(folder, ops, trials_n, letters=True)
        exp = expected_outputs(trials, ctx)
        got, warn = run_cpp(folder, ops, trials, letters_extra(folder, ops, ctor_extra), cxx, stem, chars=True)
        return first_mismatch(got, exp, trials, False), warn
    finally:
        LETTER_BASE = saved


def is_update(op):
    return op in POINT_UPDATES or op in RANGE_UPDATES or op in SEQ_OPS


def _pal_around(a, l, r):  # (l', r') of the longest palindrome a[l-k..r+k]; (l, l - 1) when a[l..r] itself isn't one (or r is past the end)
    best = (r, r - 1) if l == r - 1 else (l, r)  # (even case, nothing: the empty range (i + 1, i))
    while l >= 0 and r < len(a) and a[l] == a[r]:
        best = (l, r)
        l, r = l - 1, r + 1
    return best


def _first(a, idxs, pred):
    return next((i for i in idxs if pred(a[i])), -1)


def _kth(a, l, r, k, pred):
    hits = [i for i in range(l, r + 1) if pred(a[i])]
    return hits[k - 1] if 0 < k <= len(hits) else -1


def _max_sub(seg):
    best = cur = seg[0]
    for v in seg[1:]:
        cur = max(v, cur + v)
        best = max(best, cur)
    return best


def _prefix_search(a, l, r, x, strict):
    run = 0
    for i in range(l, r + 1):
        run += a[i]
        if run > x or (not strict and run == x):
            return i
    return -1


def _suffix_search(a, l, r, x, strict):
    run = 0
    for i in range(r, l - 1, -1):
        run += a[i]
        if run > x or (not strict and run == x):
            return i
    return -1


def _rbs(seq):  # brackets are tested as character codes, 40 is "(" and 41 is ")" (or their letters, in --letters)
    bal = 0
    for v in seq:
        bal += 1 if v in (40, letter(40)) else -1
        if bal < 0:
            return False
    return bal == 0


def _lis(seq, strict=True):
    tails = []
    for v in seq:
        k = (bisect.bisect_left if strict else bisect.bisect_right)(tails, v)
        if k == len(tails):
            tails.append(v)
        else:
            tails[k] = v
    return len(tails)


def _cost_mono_dec(seg):
    return _cost_mono_inc(seg[::-1])


def _longest_run(seg):
    best = run = 1
    for x, y in zip(seg, seg[1:]):
        run = run + 1 if x == y else 1
        best = max(best, run)
    return best


def _max_alt(seg):
    plus = minus = float("-inf")  # best sum of a non-empty alternating subsequence ending on + / on -
    for v in seg:
        plus, minus = max(plus, v, minus + v), max(minus, plus - v)
    return max(plus, minus)


def _cost_mono_inc(seg):
    mx, cost = seg[0], 0
    for v in seg:
        mx = max(mx, v)
        cost += mx - v
    return cost


SIDE = {"leftmost": lambda l, r: range(l, r + 1), "rightmost": lambda l, r: range(r, l - 1, -1)}
CMP = {"Gte": lambda v, x: v >= x, "Gt": lambda v, x: v > x, "Lte": lambda v, x: v <= x, "Lt": lambda v, x: v < x}

# Order statistics of a[l..r] (the sets picker's queries, asked about a subarray): answered from the multiset
# {value: copies}, so the dense and sparse brute forces share them. op -> arg kind.
ORDER_OPS = {
    "kthSmallest": "lrkv", "kthLargest": "lrkv", "medianLow": "lr", "medianHigh": "lr",
    "countLtX": "lrx", "countLteX": "lrx", "countGtX": "lrx", "countGteX": "lrx",
    "smallestGteX": "lrx", "smallestGtX": "lrx", "largestLteX": "lrx", "largestLtX": "lrx",
    "sumLtX": "lrx", "sumLteX": "lrx", "sumGtX": "lrx", "sumGteX": "lrx", "sumSmallestK": "lrk0", "sumLargestK": "lrk0",
    "sumKthSmallestRange": "lrij", "sumKthLargestRange": "lrij", "sumAbsDiffToX": "lrx", "sumAbsDiffToMedian": "lr",
    "rangeMex": "lr",
}
# xor / OR / AND of the values in a value range inside a[l..r] (xor: copies count; AND of nothing: -1, every bit)
BIT_AGG = {"xor": (lambda x, y: x ^ y, 0), "or": (lambda x, y: x | y, 0), "and": (lambda x, y: x & y, -1)}
ORDER_OPS.update({f"{a}{s}X": "lrx" for a in BIT_AGG for s in ("Lt", "Lte", "Gt", "Gte")})
ORDER_OPS.update({f"{a}InValRange": "lrlohi" for a in BIT_AGG})
# v ^ x over the values v of a[l..r] (the sets picker's trie queries, asked about a subarray). Values and x live in
# [0, 2^XOR_BITS); k / m / lo / hi can be anything. op -> arg kind.
XOR_BITS = 4
XOR_X_OPS = {"maxXorAgainstX": "lrx", "minXorAgainstX": "lrx", "mexXor": "lrx", "sumXor": "lrx", "kthXor": "lrxi"}
XOR_X_OPS.update({f"countXor{c}K": "lrxk" for c in ("Lt", "Lte", "Gt", "Gte")})
XOR_X_OPS.update({"largestXorLtK": "lrxk", "largestXorLteK": "lrxk", "smallestXorGtK": "lrxk", "smallestXorGteK": "lrxk"})
XOR_X_OPS.update({f"{mm}XorWithV{c}M": "lrxk" for mm in ("max", "min") for c in ("Lt", "Lte", "Gt", "Gte")})
XOR_X_OPS.update({"maxXorWithVInValRange": "lrxlohi", "minXorWithVInValRange": "lrxlohi"})
ORDER_OPS.update(XOR_X_OPS)


def order_stat(op, tot, n, xs):
    """op on the multiset tot ({value: copies}, n values in all); xs are the args after (l, r)."""
    keys = sorted(v for v, c in tot.items() if c)

    def kth(k):
        for v in keys:
            if k <= tot[v]:
                return v
            k -= tot[v]

    def first(k):  # sum of the k smallest
        s_ = 0
        for v in keys:
            t = min(k, tot[v])
            s_, k = s_ + t * v, k - t
        return s_

    cnt = lambda p: sum(tot[v] for v in keys if p(v))  # noqa: E731
    sm = lambda p: sum(tot[v] * v for v in keys if p(v))  # noqa: E731
    x = xs[0] if xs else None
    if op == "kthSmallest": return kth(x)
    if op == "kthLargest": return kth(n + 1 - x)
    if op == "medianLow": return kth((n + 1) // 2)
    if op == "medianHigh": return kth(n // 2 + 1)
    for name, cmp in CMP.items():
        if op == f"count{name}X": return cnt(lambda v: cmp(v, x))
        if op == f"sum{name}X": return sm(lambda v: cmp(v, x))
    if op == "smallestGteX": return min((v for v in keys if v >= x), default=None)
    if op == "smallestGtX": return min((v for v in keys if v > x), default=None)
    if op == "largestLteX": return max((v for v in keys if v <= x), default=None)
    if op == "largestLtX": return max((v for v in keys if v < x), default=None)
    if op == "sumSmallestK": return first(x)
    if op == "sumLargestK": return first(n) - first(n - x)
    if op == "sumKthSmallestRange": return first(xs[1]) - first(xs[0] - 1)
    if op == "sumKthLargestRange": return first(n - xs[0] + 1) - first(n - xs[1])
    if op == "sumAbsDiffToX": return sum(tot[v] * abs(v - x) for v in keys)
    if op == "sumAbsDiffToMedian":
        m = kth((n + 1) // 2)
        return sum(tot[v] * abs(v - m) for v in keys)
    if op == "rangeMex":
        v = 0
        while tot.get(v):
            v += 1
        return v
    if op in XOR_X_OPS:
        ys = sorted(v ^ x for v in keys for _ in range(tot[v]))
        if op == "maxXorAgainstX": return ys[-1]
        if op == "minXorAgainstX": return ys[0]
        if op == "sumXor": return sum(ys)
        if op == "kthXor": return ys[xs[1]]
        if op == "mexXor":
            have, t = set(ys), 0
            while t in have:
                t += 1
            return t
        k = xs[1] if len(xs) > 1 else None
        for name, cmp in CMP.items():
            if op == f"countXor{name}K": return sum(cmp(y, k) for y in ys)
        if op == "largestXorLtK": return max((y for y in ys if y < k), default=None)
        if op == "largestXorLteK": return max((y for y in ys if y <= k), default=None)
        if op == "smallestXorGtK": return min((y for y in ys if y > k), default=None)
        if op == "smallestXorGteK": return min((y for y in ys if y >= k), default=None)
        keep = (lambda v: xs[1] <= v <= xs[2]) if op.endswith("InValRange") else (lambda v, c=CMP[op[op.index("WithV") + 5:-1]]: c(v, k))
        cand = [v ^ x for v in keys if keep(v)]
        if not cand: return None
        return max(cand) if op.startswith("max") else min(cand)
    for agg, (f, ident) in BIT_AGG.items():
        if op.startswith(agg) and op[len(agg):len(agg) + 1].isupper():
            suf = op[len(agg):]
            keep = (lambda v: xs[0] <= v <= xs[1]) if suf == "InValRange" else (lambda v, c=CMP[suf[:-1]]: c(v, x))
            res = ident
            for v in keys:
                if keep(v) and (agg != "xor" or tot[v] % 2):
                    res = f(res, v)
            return res
    raise KeyError(op)


# query op -> (arg kind, brute(a, l, r, *args, ctx)); arg kinds: "lr", "lrx", "lrk", "lrkx", "lrlohi", plus "lrkv" (a k
# in [1, r - l + 1]), "lrk0" (a k in [0, r - l + 1]) and "lrij" (1 <= i <= j <= r - l + 1): those ops error outside them
BRUTE_QUERIES = {
    # hashAll(): compared with a fresh structure built from the current a[l..r] (equal only when that is the whole array)
    "hashAll": ("hall", lambda a, l, r, c: a == a[l:r + 1]),
    # hashAllReversed(): compared with rangeHashReversed(l, r) (equal only when a[l..r] is the whole array)
    "hashAllReversed": ("hall", lambda a, l, r, c: a == a[l:r + 1]),
    "sumAll": ("all", lambda a, c: sum(a)),
    "minAll": ("all", lambda a, c: min(a)),
    "maxAll": ("all", lambda a, c: max(a)),
    "gcdAll": ("all", lambda a, c: reduce(math.gcd, (abs(v) for v in a), 0)),
    "xorAll": ("all", lambda a, c: reduce(lambda x, y: x ^ y, a)),
    "andAll": ("all", lambda a, c: reduce(lambda x, y: x & y, a)),
    "orAll": ("all", lambda a, c: reduce(lambda x, y: x | y, a)),
    # (the LCM templates take a cap and answer -1 past it: the tests pass a small one, so both cases come up)
    "lcmAll": ("all", lambda a, c: (lambda l: l if l <= c["lcmCap"] else -1)(reduce(math.lcm, (abs(v) for v in a), 1))),
    "productAllMod": ("all", lambda a, c: reduce(lambda x, y: x * y % c["mod"], a, 1) % c["mod"]),
    "longestPalCenteredAtI": ("i", lambda a, i, c: _pal_around(a, i, i)),
    "longestPalCenteredAtIPlusOne": ("i", lambda a, i, c: _pal_around(a, i, i + 1)),
    "stridedSum": ("lrs", lambda a, l, r, s, c: sum(a[l:r + 1:s])),
    "stridedMin": ("lrs", lambda a, l, r, s, c: min(a[l:r + 1:s])),
    "stridedMax": ("lrs", lambda a, l, r, s, c: max(a[l:r + 1:s])),
    "stridedGcd": ("lrs", lambda a, l, r, s, c: reduce(math.gcd, a[l:r + 1:s], 0)),
    "stridedXorQuery": ("lrs", lambda a, l, r, s, c: reduce(lambda x, y: x ^ y, a[l:r + 1:s])),
    "stridedAndQuery": ("lrs", lambda a, l, r, s, c: reduce(lambda x, y: x & y, a[l:r + 1:s])),
    "stridedOrQuery": ("lrs", lambda a, l, r, s, c: reduce(lambda x, y: x | y, a[l:r + 1:s])),
    "rangeSum": ("lr", lambda a, l, r, c: sum(a[l:r + 1])),
    "rangeSumMod": ("lr", lambda a, l, r, c: sum(a[l:r + 1]) % c["mod"]),
    "rangeMin": ("lr", lambda a, l, r, c: min(a[l:r + 1])),
    "rangeMax": ("lr", lambda a, l, r, c: max(a[l:r + 1])),
    "rangeGcd": ("lr", lambda a, l, r, c: reduce(math.gcd, (abs(v) for v in a[l:r + 1]), 0)),
    "rangeAndQuery": ("lr", lambda a, l, r, c: reduce(lambda x, y: x & y, a[l:r + 1])),
    "rangeOrQuery": ("lr", lambda a, l, r, c: reduce(lambda x, y: x | y, a[l:r + 1])),
    "rangeXorQuery": ("lr", lambda a, l, r, c: reduce(lambda x, y: x ^ y, a[l:r + 1])),
    "maxSubarraySum": ("lr", lambda a, l, r, c: _max_sub(a[l:r + 1])),
    "getAll": ("all", lambda a, c: list(a)),
    "size": ("all", lambda a, c: len(a)),
    "isPalindrome": ("lr", lambda a, l, r, c: a[l:r + 1] == a[l:r + 1][::-1]),
    "rangesEqual": ("lr2", lambda a, l, r, l2, r2, c: a[l:r + 1] == a[l2:r2 + 1]),
    # hashes are random per run, so the test asks what they promise: rangeHash(l, r) == rangeHash(l2, r2) exactly when the
    # ranges are equal, and rangeHashReversed(l, r) == rangeHash(l2, r2) when the second is the first reversed
    "rangeHash": ("lr2", lambda a, l, r, l2, r2, c: a[l:r + 1] == a[l2:r2 + 1]),
    "rangeHashReversed": ("lr2", lambda a, l, r, l2, r2, c: a[l:r + 1][::-1] == a[l2:r2 + 1]),
    "maxPrefixSum": ("lr", lambda a, l, r, c: max(sum(a[l:i + 1]) for i in range(l, r + 1))),
    "maxSuffixSum": ("lr", lambda a, l, r, c: max(sum(a[i:r + 1]) for i in range(l, r + 1))),
    "minPrefixSum": ("lr", lambda a, l, r, c: min(sum(a[l:i + 1]) for i in range(l, r + 1))),
    "minSuffixSum": ("lr", lambda a, l, r, c: min(sum(a[i:r + 1]) for i in range(l, r + 1))),
    "countOccurrences": ("lrx", lambda a, l, r, x, c: a[l:r + 1].count(x)),
    "leftmostIndexOf": ("x", lambda a, x, c: _first(a, range(len(a)), lambda v: v == x)),
    "find": ("xv", lambda a, x, c: a.index(x) if x in a else -1),  # (values are kept distinct for it: see domain)
    "rightmostIndexOf": ("x", lambda a, x, c: _first(a, range(len(a) - 1, -1, -1), lambda v: v == x)),
    "leftmostIndexOfInRange": ("lrx", lambda a, l, r, x, c: _first(a, range(l, r + 1), lambda v: v == x)),
    "rightmostIndexOfInRange": ("lrx", lambda a, l, r, x, c: _first(a, range(r, l - 1, -1), lambda v: v == x)),
    "countDistinct": ("lr", lambda a, l, r, c: len(set(a[l:r + 1]))),
    "allDistinct": ("lr", lambda a, l, r, c: len(set(a[l:r + 1])) == r - l + 1),
    "rangeMode": ("lr", None),  # ties may return any mode: checked by _check_mode
    "rangeLIS": ("lr", lambda a, l, r, c: _lis(a[l:r + 1])),
    "isRBS": ("lr", lambda a, l, r, c: _rbs(a[l:r + 1])),
    "rangeLNDS": ("lr", lambda a, l, r, c: _lis(a[l:r + 1], False)),
    "rangeLDS": ("lr", lambda a, l, r, c: _lis(a[l:r + 1][::-1])),
    "rangeLNIS": ("lr", lambda a, l, r, c: _lis(a[l:r + 1][::-1], False)),
    "costMonoIncreasing": ("lr", lambda a, l, r, c: _cost_mono_inc(a[l:r + 1])),
    "costMonoDecreasing": ("lr", lambda a, l, r, c: _cost_mono_dec(a[l:r + 1])),
    "costStrictIncreasing": ("lr", lambda a, l, r, c: _cost_mono_inc([v - i for i, v in enumerate(a[l:r + 1])])),
    "costStrictDecreasing": ("lr", lambda a, l, r, c: _cost_mono_dec([v + i for i, v in enumerate(a[l:r + 1])])),
    "longestEqualRun": ("lr", lambda a, l, r, c: _longest_run(a[l:r + 1])),
    "maxAltSubseqSum": ("lr", lambda a, l, r, c: _max_alt(a[l:r + 1])),
    "doAllElementsAppearEvenFrequency": ("lr", lambda a, l, r, c: all(v % 2 == 0 for v in Counter(a[l:r + 1]).values())),
    "countInValRange": ("lrlohi", lambda a, l, r, lo, hi, c: sum(lo <= v <= hi for v in a[l:r + 1])),
    "sumInValRange": ("lrlohi", lambda a, l, r, lo, hi, c: sum(v for v in a[l:r + 1] if lo <= v <= hi)),
    "leftmostPrefixSumGteX": ("lrx", lambda a, l, r, x, c: _prefix_search(a, l, r, x, False)),
    "leftmostPrefixSumGtX": ("lrx", lambda a, l, r, x, c: _prefix_search(a, l, r, x, True)),
    "rightmostSuffixSumGteX": ("lrx", lambda a, l, r, x, c: _suffix_search(a, l, r, x, False)),
    "rightmostSuffixSumGtX": ("lrx", lambda a, l, r, x, c: _suffix_search(a, l, r, x, True)),
    # (< / <= searches: the > / >= ones on -a with -x)
    "leftmostPrefixSumLteX": ("lrx", lambda a, l, r, x, c: _prefix_search([-v for v in a], l, r, -x, False)),
    "leftmostPrefixSumLtX": ("lrx", lambda a, l, r, x, c: _prefix_search([-v for v in a], l, r, -x, True)),
    "rightmostSuffixSumLteX": ("lrx", lambda a, l, r, x, c: _suffix_search([-v for v in a], l, r, -x, False)),
    "rightmostSuffixSumLtX": ("lrx", lambda a, l, r, x, c: _suffix_search([-v for v in a], l, r, -x, True)),
    "minSubarraySum": ("lr", lambda a, l, r, c: -_max_sub([-v for v in a[l:r + 1]])),
}
for _side, _idx in SIDE.items():
    for _name, _cmp in CMP.items():
        BRUTE_QUERIES[f"{_side}{_name}X"] = ("lrx", lambda a, l, r, x, c, _idx=_idx, _cmp=_cmp: _first(a, _idx(l, r), lambda v: _cmp(v, x)))
for _op, _kind in ORDER_OPS.items():
    BRUTE_QUERIES[_op] = (_kind, lambda a, l, r, *xs, _op=_op: order_stat(_op, Counter(a[l:r + 1]), r - l + 1, xs[:-1]))
for _name, _cmp in CMP.items():
    BRUTE_QUERIES[f"kth{_name}X"] = ("lrkx", lambda a, l, r, k, x, c, _cmp=_cmp: _kth(a, l, r, k, lambda v: _cmp(v, x)))


def _check_mode(a, l, r, got):
    """got is (value, freq); any value with the max frequency is a correct answer."""
    cnt = Counter(a[l:r + 1])
    best = max(cnt.values())
    return got[1] == best and cnt.get(got[0], 0) == best


def brute_update(a, op, args, ctx):
    mod, full = ctx["mod"], ctx["full"]
    if op == "stridedAdd":
        for i in range(args[0], args[1] + 1, args[2]):
            a[i] += args[3]
        return
    if op in SEQ_OPS:
        if op == "cut":
            ctx["pieces"].append(a[args[0]:args[1] + 1])
            del a[args[0]:args[1] + 1]
            return
        if op == "copy":  # (a piece holding a[l..r]; a is unchanged)
            ctx["pieces"].append(a[args[0]:args[1] + 1])
            return
        if op == "paste":
            seg = ctx["pieces"].pop()
            a[args[0]:args[0]] = seg[::-1] if args[1] else seg
            return
        if op == "split":
            ctx["pieces"].append(a[args[0]:])
            del a[args[0]:]
            return
        if op == "trisect":
            ctx["pieces"] += [a[args[0]:args[1] + 1], a[args[1] + 1:]]
            del a[args[0]:]
            return
        if op == "merge":
            seg = ctx["pieces"].pop()
            a += seg[::-1] if args[0] else seg
            return
        if op == "copyRange":
            a[args[2]:args[2]] = a[args[0]:args[1] + 1]
            return
        if op == "insertCopiesAt":
            a[args[0]:args[0]] = [args[1]] * max(0, args[2])
            return
        if op == "append":
            a.append(args[0])
        elif op == "appendLeft":
            a.insert(0, args[0])
        elif op == "insertAt":
            a.insert(args[0], args[1])
        elif op == "pop":
            return a.pop()
        elif op == "popLeft":
            return a.pop(0)
        else:
            l, r = args[0], args[1]
            seg = a[l:r + 1]
            del a[l:r + 1]
            if op == "rangeReverse":
                seg.reverse()
            elif op in ("rangeSortAsc", "rangeSortDesc"):
                seg.sort(reverse=op == "rangeSortDesc")
            elif op == "rangeTwinSpin":
                for p in range(0, len(seg) - 1, 2):
                    seg[p], seg[p + 1] = seg[p + 1], seg[p]
            elif op in ("rangeRotateLeft", "rangeRotateRight"):
                k = (args[2] if op == "rangeRotateLeft" else -args[2]) % len(seg)
                seg = seg[k:] + seg[:k]
            if op != "eraseRange":
                at = args[2] if op == "moveRange" else l
                a[at:at] = seg
        return
    if op in POINT_UPDATES:
        i, v = args
        a[i] = {"pointAssign": v, "pointAdd": a[i] + v, "pointChmax": max(a[i], v), "pointChmin": min(a[i], v)}[op]
        if full is not None:
            a[i] &= full
        if mod:
            a[i] %= mod
        return
    l, r, *xs = args
    for i in range(l, r + 1):
        v = a[i]
        if op in ("rangeAdd", "rangeAddMod"): v += xs[0]
        elif op in ("rangeAssign", "rangeAssignMod"): v = xs[0]
        elif op == "rangeChmax": v = max(v, xs[0])
        elif op == "rangeChmin": v = min(v, xs[0])
        elif op == "rangeMultMod": v *= xs[0]
        elif op == "rangeAffineMod": v = v * xs[0] + xs[1]
        elif op in ("rangeAddArithSeq", "rangeAddArithSeqMod"): v += xs[0] + (i - l) * xs[1]
        elif op == "rangeMod": v %= xs[0]
        elif op == "rangeFloorDiv": v //= xs[0]
        elif op == "rangeFloorSqrt": v = math.isqrt(v)
        elif op == "rangeAndApply": v &= xs[0]
        elif op == "rangeOrApply": v |= xs[0]
        elif op == "rangeXorApply": v ^= xs[0]
        elif op == "rangeReplace": v = xs[1] if v == xs[0] else v
        elif op == "rangeFlip": v = {40: 41, 41: 40, letter(40): letter(41), letter(41): letter(40)}[v]  # brackets: ( <-> )
        a[i] = v % mod if mod else v


# ------------------------------------------------------------------------------------------------ value domains

def rbs_extra(folder, as_letters=False):
    """ctor args after the brackets: openChar, and closeChar too for the templates that take one"""
    takes_close = "closeChar" in open(os.path.join(DIR, folder, "template.py")).read()
    return [(letter if as_letters else int)(v) for v in ((40, 41) if takes_close else (40,))]


def letters_extra(folder, ops, extra):
    """the ctor args after the array when the values are letters: the bracket characters, or a value range
    [valLo, valHi] as letters (the mass change templates)"""
    if "isRBS" in ops:
        return rbs_extra(folder, True)
    return [letter(v) if isinstance(v, int) else v for v in extra] if "rangeReplace" in ops else extra


def domain(folder, ops):
    """Random-input rules for one template: values, point-add deltas, ctor extra args, and the brute context.
    Keeps inputs inside each template's documented preconditions (e.g. shrink ops need values >= 0)."""
    ctx = {"mod": None, "full": None, "lcmCap": None}
    small = lambda r: r.randint(-10, 10)  # noqa: E731
    nonneg_small = lambda r: r.randint(0, 10)  # noqa: E731
    if "lcmAll" in ops:  # small values and a cap of 500 (passed to the ctor): LCMs land on both sides of it
        ctx["lcmCap"] = 500
        if MOD_OPS & set(ops):
            ctx["mod"] = 97
        if ctx["mod"]:  # (mod templates report values mod p: keep them in [0, p))
            return (lambda r: r.randint(0, 12)), nonneg_small, [97, 500], ctx
        return (lambda r: r.randint(-12, 12)), small, [500], ctx
    if folder.startswith("merge-sort-tree-updates-offline"):  # every pointAssign listed up front (per trial: see trial_extra)
        return (lambda r: r.randint(-50, 50)), small, ["UPDATES"], ctx
    if folder.startswith("merge-sort-tree-updates-hashfenwick"):  # a value range
        return (lambda r: r.randint(-50, 50)), small, [-10**9, 10**9], ctx
    if set(XOR_X_OPS) & set(ops):  # xor with x: values in [0, 2^bits), the bit count passed to the ctor
        return (lambda r: r.randint(0, (1 << XOR_BITS) - 1)), nonneg_small, [XOR_BITS], ctx
    if {"stridedXorQuery", "stridedAndQuery", "stridedOrQuery", "stridedGcd"} & set(ops):  # bit ops and gcd: values >= 0
        return (lambda r: r.randint(0, 63)), nonneg_small, [], ctx
    if "find" in ops:  # find needs distinct values: each new one 1000 above the last (point adds move them by at most 3)
        fresh = itertools.count()
        return (lambda r: 1000 * next(fresh) + r.randint(0, 9)), (lambda r: r.randint(-3, 3)), [], ctx
    if "isRBS" in ops:  # brackets: "(" and ")" as character codes, with "(" passed as the opening character (and ")" as the
        return (lambda r: r.choice((40, 41))), small, rbs_extra(folder), ctx  # closing one, to the templates that take it)
    if "rangeSortAsc" in ops:  # range sort: a value range for its value trees, values with many repeats
        return (lambda r: r.randint(0, 2) if "isPalindrome" in ops else r.randint(-8, 8)), small, [-10**9, 10**9], ctx
    if MOD_OPS & set(ops):
        ctx["mod"] = 97
        return (lambda r: r.randint(0, 96)), (lambda r: r.randint(0, 96)), [97], ctx
    if {"rangeAndApply", "rangeOrApply", "rangeXorApply", "rangeAndQuery", "rangeOrQuery"} & set(ops):
        if "rangeSum" in ops or "rangeMin" in ops:  # the bit-beats tree masks values to 20 bits
            ctx["full"] = (1 << 20) - 1
        return (lambda r: r.randint(0, 63)), nonneg_small, [], ctx
    if "leftmostPrefixSumGteX" in ops:
        return (lambda r: r.randint(0, 6)), nonneg_small, [], ctx
    sums = {"rangeSum", "maxAltSubseqSum", "maxSubarraySum", "maxPrefixSum", "maxSuffixSum", "minPrefixSum",
            "minSuffixSum", "minSubarraySum"} & set(ops)  # (these add values up)
    if "rangeFloorSqrt" in ops and not sums:
        return (lambda r: r.choice([r.randint(0, 200), r.randint(0, (1 << 62) - 1)])), nonneg_small, [], ctx
    if "rangeFloorDiv" in ops and not sums:
        return (lambda r: r.choice([r.randint(-60, 60), r.randint(-10**17, 10**17)])), small, [], ctx
    if {"rangeMod", "rangeFloorSqrt", "rangeFloorDiv"} & set(ops):
        return (lambda r: r.randint(0, 200)), nonneg_small, [], ctx
    if "rangeGcd" in ops:
        return (lambda r: r.randint(0, 60)), nonneg_small, [], ctx
    # order statistics: templates with updates take the value range [valLo, valHi] too, or (offline) every value
    # that will ever be added
    if "rangeMex" in ops or "kthSmallest" in ops:
        lo, hi = (-3, 14) if "rangeMex" in ops else (-12, 12)
        extra = []
        if "offline" in folder:
            extra = [list(range(lo, hi + 1))]
        elif ("pointAssign" in ops or "append" in ops) and "cut" not in ops and not folder.startswith("sqrt-movable"):  # (a sequence that cuts, or the movable sqrt blocks, keep no value range)
            extra = [-10**9, 10**9]
        return (lambda r: r.randint(lo, hi)), small, extra, ctx
    if "isPalindrome" in ops:
        return (lambda r: r.randint(0, 2)), (lambda r: r.randint(-1, 1)), [], ctx
    if {"orLtX", "andLtX"} & set(ops):  # by-value OR / AND with point updates (seg tree of value trees): a value range too
        return (lambda r: r.randint(-30, 30)), small, ([-10**9, 10**9] if "pointAssign" in ops else []), ctx
    if "rangeReplace" in ops:  # mass change: few values, so most changes hit something; a value range [valLo, valHi] to
        takes_range = "valLo" in open(os.path.join(DIR, folder, "template.py")).read()  # the templates that take one
        return (lambda r: r.randint(-3, 6)), small, ([-3, 6] if takes_range else []), ctx
    if {"countDistinct", "allDistinct", "rangeMode", "doAllElementsAppearEvenFrequency", "countOccurrences", "leftmostIndexOf"} & set(ops):
        return (lambda r: r.randint(0, 6)), nonneg_small, [], ctx
    if "longestEqualRun" in ops:
        return (lambda r: r.randint(0, 2)), (lambda r: r.randint(-1, 1)), [], ctx
    if "costMonoIncreasing" in ops:
        return (lambda r: r.randint(0, 50)), small, [], ctx
    return (lambda r: r.randint(-50, 50)), small, [], ctx


def random_step(rng, n):  # mostly small steps, but some past any cutoff (and past the end of the array)
    return rng.choice((1, 1, 2, 2, 3, 4, 5, rng.randint(1, n + 3)))


def update_args(op, rng, gen, mod):
    if op == "stridedAdd":
        return [rng.choice((1, 2, 3, 4, 5, 7, 11, 40)), gen(rng)]
    if op in ("rangeAddArithSeq", "rangeAddArithSeqMod"):
        return [gen(rng), rng.randint(0, mod - 1) if mod else rng.randint(-20, 20)]
    if op == "rangeAffineMod":
        return [gen(rng), gen(rng)]
    if op == "rangeFloorDiv":
        return [rng.choice([2, 2, 3, 5, 7, 10**6, 10**12])]
    if op == "rangeMod":
        return [rng.randint(1, 60)]
    if op in ("rangeFloorSqrt", "rangeFlip"):
        return []
    return [gen(rng)]


def bad_calls(seq, lo, hi, rng, k=4):
    """a few calls with an index outside [lo, hi] (inserts: outside [lo, hi + 1]), each a copy of the last call the
    trial made to that op with one index moved out; they are sent as "!op" and must raise (IndexError / out_of_range),
    which the drivers print as OOR. Pieces, hashes and value-only ops are left out."""
    last = {}
    for op, args in seq:
        if op in PIECE_OPS or op in ("rangeHash", "rangeHashReversed", "find", "append", "appendLeft") or not args:
            continue
        kind = SEQ_OPS.get(op) or (BRUTE_QUERIES[op][0] if op in BRUTE_QUERIES else "lr")
        if op == "pointGet" or op in POINT_UPDATES or kind in ("iv", "ivk", "i") or kind.startswith("lr"):
            last[op] = (kind, list(args))
    out = []
    for op in rng.sample(sorted(last), min(k, len(last))):
        kind, args = last[op]
        if op == "pointGet" or op in POINT_UPDATES or kind == "i":
            args[0] = rng.choice([lo - 1, hi + 1])
        elif kind in ("iv", "ivk"):  # (an insert position may be one past the end)
            args[0] = rng.choice([lo - 1, hi + 2])
        elif kind == "lr2" and rng.random() < 0.5:
            args[3] = hi + 1
        else:
            which = rng.randrange(3)
            if which == 0:
                args[1] = hi + 1
            elif which == 1:
                args[0] = lo - 1
            else:
                args[0] = args[1] + 1  # (l > r)
        out.append(("!" + op, args))
    return out


def make_trials(folder, ops, trials, letters=False):
    """Deterministic random op sequences: [(initial array, [(op, args)])]. letters: every value is a letter instead."""
    gen, delta, _, ctx = domain(folder, ops)
    if letters:
        gen = (lambda g: lambda r: letter(g(r)))(gen)
    updates = [o for o in ops if is_update(o)]
    queries = [o for o in ops if o not in updates]
    lazy = [o for o in updates if o in RANGE_UPDATES]  # (half the updates are range ones: their tags interact the most)
    if "isRBS" in ops:  # (a wrong bracket aggregate only shows on a balanced range: rare, so many more trials)
        trials *= 40
    out = []
    for t in range(trials):
        rng = random.Random(t)
        n = rng.randint(1, 8 if "isRBS" in ops and t % 2 else 30)  # (short bracket runs are often balanced: hard cases)
        a = [gen(rng) for _ in range(n)]
        seen = list(a)  # (find asks mostly for values that were in the array at some point)
        seq, pieces = [], []  # (lengths of the pieces cut and not yet pasted)
        for _ in range(OPS_PER_TRIAL):
            if updates and rng.random() < 0.5:
                op = rng.choice(lazy) if lazy and rng.random() < 0.5 else rng.choice(updates)
            else:
                op = rng.choice(queries or updates)
            # every structure and piece keeps at least one value; at most 4 pieces at once
            if (op in ("paste", "merge") and not pieces or op in ("cut", "split", "trisect", "copy") and len(pieces) >= 3 or op == "copy" and n >= 40
                    or op in ("cut", "split") and n < 2 or op == "trisect" and n < 3):
                op = rng.choice([o for o in ("paste", "merge") if o in ops]) if pieces else "pointGet"
            if op == "cut":
                l = rng.randrange(n)
                r = rng.randint(l, min(n - 1, l + n - 2))
                pieces.append(r - l + 1)
                n -= r - l + 1
                seq.append((op, [l, r]))
                continue
            if op == "copy":
                l, r = sorted((rng.randrange(n), rng.randrange(n)))
                pieces.append(r - l + 1)
                seq.append((op, [l, r]))
                continue
            if op == "split":
                k = rng.randint(1, n - 1)
                pieces.append(n - k)
                n = k
                seq.append((op, [k]))
                continue
            if op == "trisect":
                l = rng.randint(1, n - 2)
                r = rng.randint(l, n - 2)
                pieces += [r - l + 1, n - 1 - r]
                n = l
                seq.append((op, [l, r]))
                continue
            if op in ("paste", "merge"):
                rv = rng.randint(0, 1) if "rangeReverse" in ops else 0  # (a piece is reversed first only if it can be)
                seq.append((op, [rng.randint(0, n), rv] if op == "paste" else [rv]))
                n += pieces.pop()
                continue
            if op in ("pop", "popLeft", "eraseRange") and n == 1 or op in ("insertAt", "append", "appendLeft", "insertCopiesAt", "copyRange") and n >= 40:  # keep 1 <= n <= 40
                grow = next((o for o in ("insertAt", "append", "appendLeft") if o in ops), "pointGet")
                op = grow if n == 1 else "pop" if "pop" in ops else "pointGet"
            if op in SEQ_OPS:
                l, r = sorted((rng.randrange(n), rng.randrange(n)))
                kind = SEQ_OPS[op]
                if kind == "v":
                    args = [gen(rng)]
                elif kind == "none":
                    args = []
                elif kind == "ivk":  # (one copy at most when find needs distinct values)
                    args = [rng.randint(0, n), gen(rng), rng.randint(-1, 1 if "find" in ops else 3)]
                elif kind == "iv":
                    args = [rng.randint(0, n), gen(rng)]
                elif kind == "i":
                    args = [rng.randrange(n)]
                elif op == "eraseRange":
                    args = [l, r - (r - l + 1 == n)]  # never empty the array
                elif kind == "lrk":
                    args = [l, r, rng.randint(-2 * (r - l + 1), 2 * (r - l + 1))]
                elif kind == "lrc":
                    args = [l, r, rng.randint(0, n)]
                elif kind == "lri":
                    args = [l, r, rng.randint(0, n - (r - l + 1))]
                else:
                    args = [l, r]
                n += (1 if op in ("insertAt", "append", "appendLeft") else -1 if op in ("pop", "popLeft") else -(args[1] - args[0] + 1) if op == "eraseRange"
                      else max(0, args[2]) if op == "insertCopiesAt" else args[1] - args[0] + 1 if op == "copyRange" else 0)
            elif op == "pointGet":
                args = [rng.randrange(n)]
            elif op in POINT_UPDATES:
                args = [rng.randrange(n), delta(rng) if op == "pointAdd" else gen(rng)]
            else:
                l, r = sorted((rng.randrange(n), rng.randrange(n)))
                kind = "upd" if op in RANGE_UPDATES else BRUTE_QUERIES[op][0]
                if kind == "all":
                    args = []
                elif kind == "x":  # a value only (the whole array)
                    args = [gen(rng)]
                elif kind == "xv":  # mostly a value that has been in the array
                    args = [rng.choice(seen) if rng.random() < 0.85 else gen(rng)]
                elif kind == "lr2":  # a second range, mostly of the same length
                    m = r - l + 1
                    l2 = rng.randint(0, n - m) if rng.random() < 0.8 else rng.randrange(n)
                    r2 = l2 + m - 1 if l2 + m - 1 < n and rng.random() < 0.9 else rng.randint(l2, n - 1)
                    args = [l, r, l2, r2]
                elif op == "rangeReplace":  # (x mostly a value that has been in the array, so something changes)
                    args = [l, r, rng.choice(seen) if rng.random() < 0.85 else gen(rng), gen(rng)]
                    seen.append(args[3])
                elif kind == "upd":
                    args = [l, r] + update_args(op, rng, gen, ctx["mod"])
                elif kind == "lrx":
                    args = [l, r, rng.randint(-2, 25) if "PrefixSum" in op or "SuffixSum" in op else gen(rng)]
                elif kind == "lrs":
                    args = [l, r, random_step(rng, n)]
                elif kind == "hall":  # (half the time the whole array, so the hashes must agree)
                    args = [0, n - 1] if rng.random() < 0.5 else [l, r]
                elif kind == "i":
                    args = [rng.randrange(n)]
                elif kind == "lrkx":
                    args = [l, r, rng.randint(1, 5), gen(rng)]
                elif kind == "lrk":
                    args = [l, r, rng.randint(0, 6)]
                elif kind == "lrkv":
                    args = [l, r, rng.randint(1, r - l + 1)]
                elif kind == "lrk0":
                    args = [l, r, rng.randint(0, r - l + 1)]
                elif kind == "lrij":
                    args = [l, r, *sorted((rng.randint(1, r - l + 1), rng.randint(1, r - l + 1)))]
                elif kind == "lrlohi":
                    args = [l, r, *sorted((gen(rng), gen(rng)))]
                elif kind == "lrxk":  # (k / m anywhere around the value range, past both ends too)
                    args = [l, r, gen(rng), rng.randint(-2, (1 << XOR_BITS) + 2)]
                elif kind == "lrxi":  # (a 0-indexed rank in a[l..r])
                    args = [l, r, gen(rng), rng.randint(0, r - l)]
                elif kind == "lrxlohi":
                    args = [l, r, gen(rng), *sorted((rng.randint(-2, (1 << XOR_BITS) + 2), rng.randint(-2, (1 << XOR_BITS) + 2)))]
                else:
                    args = [l, r]
            seq.append((op, args))
            if SEQ_OPS.get(op) in ("v", "iv", "ivk") or op in ("pointAssign", "pointChmax", "pointChmin"):
                seen.append(args[0] if SEQ_OPS.get(op) == "v" else args[1])  # (a value that may now be in the array)
        seq += bad_calls(seq, 0, n - 1, rng)
        out.append((a, seq))
    return out, ctx


def expected_outputs(trials, ctx):
    """Replay every sequence on the brute force; returns per query either a value or ("mode", a, l, r)."""
    exp = []
    for a0, seq in trials:
        a = list(a0)
        ctx["pieces"] = []
        if ctx["mod"]:
            a = [v % ctx["mod"] for v in a]
        for op, args in seq:
            if op.startswith("!"):  # (an index out of range: the template must raise)
                exp.append("OOR")
            elif op == "pointGet":
                exp.append(a[args[0]])
            elif op in SEQ_OUT:
                exp.append(brute_update(a, op, args, ctx))
            elif is_update(op):
                brute_update(a, op, args, ctx)
            elif op == "rangeMode":
                exp.append(("mode", list(a), *args))
            else:
                exp.append(BRUTE_QUERIES[op][1](a, *args, ctx))
    return exp


def matches(got_text, want, wrap64=False):
    if isinstance(want, tuple) and want and want[0] == "modecounts":
        parts = got_text.split()
        tot = want[1]
        return len(parts) == 2 and int(parts[1]) == max(tot.values()) == tot.get(int(parts[0]), -1)
    if wrap64 and type(want) is int and not -2**63 <= want < 2**63:
        want = (want + 2**63) % 2**64 - 2**63  # C++ sums wrap: exact whenever the true value fits in 64 bits
    if isinstance(want, tuple) and want and want[0] == "mode":
        _, a, l, r = want
        parts = got_text.split()
        value = int(parts[0]) if parts and parts[0].lstrip("-").isdigit() else parts[0] if parts else None  # (a letter, in --letters)
        return len(parts) == 2 and _check_mode(a, l, r, (value, int(parts[1])))
    return got_text == norm(want)


def norm(v):
    if isinstance(v, bool):
        return str(int(v))
    if isinstance(v, list):
        return " ".join(norm(x) for x in v)
    if isinstance(v, tuple):
        return " ".join(norm(x) for x in v)
    return str(v)


def first_mismatch(got, exp, trials, wrap64=False):
    if len(got) != len(exp):
        return f"{len(got)} outputs, expected {len(exp)}"
    for k, (g, e) in enumerate(zip(got, exp)):
        if not matches(g, e, wrap64):
            want = "a mode with its frequency" if isinstance(e, tuple) and e and e[0] == "mode" else norm(e)
            return f"query #{k} ({describe_query(trials, k)}): got {g}, expected {want}"
    return None


def describe_query(trials, k):
    seen = 0
    for t, (a0, seq) in enumerate(trials):
        for step, (op, args) in enumerate(seq):
            if is_update(op):
                continue
            if seen == k:
                return f"trial {t}, step {step}: {op}({', '.join(map(str, args))}), initial array {a0}"
            seen += 1
    return "?"



# ------------------------------------------------------------------------------------------------ sparse brute force

class Runs:
    """An array over [lo, hi] kept as constant runs: starts[k] .. starts[k+1]-1 all equal vals[k]. Every range update
    the sparse templates support maps a constant run to a constant run, so a run never has to be split by value."""
    def __init__(self, lo, hi):
        self.lo, self.hi, self.starts, self.vals = lo, hi, [lo], [0]

    def _split(self, x):  # make x start a run; returns its index
        if x > self.hi:
            return len(self.starts)
        k = bisect.bisect_right(self.starts, x) - 1
        if self.starts[k] != x:
            self.starts.insert(k + 1, x)
            self.vals.insert(k + 1, self.vals[k])
            k += 1
        return k

    def update(self, l, r, f):
        a = self._split(l)
        b = self._split(r + 1)
        for k in range(a, b):
            self.vals[k] = f(self.vals[k])

    def get(self, i):
        return self.vals[bisect.bisect_right(self.starts, i) - 1]

    def runs(self, l, r):  # [(start, end, value)] clipped to [l, r]
        k = bisect.bisect_right(self.starts, l) - 1
        out = []
        while k < len(self.starts) and self.starts[k] <= r:
            end = (self.starts[k + 1] - 1) if k + 1 < len(self.starts) else self.hi
            out.append((max(l, self.starts[k]), min(r, end), self.vals[k]))
            k += 1
        return out


def _block(v, n):  # (sum, best prefix, best suffix, best subarray) of n copies of v, pieces non-empty
    s = v * n
    b = s if v > 0 else v
    return s, b, b, b


def _merge4(a, b):
    return a[0] + b[0], max(a[1], a[0] + b[1]), max(b[2], b[0] + a[2]), max(a[3], b[3], a[2] + b[1])


def _runs_sub(runs):
    acc = None
    for s_, e, v in runs:
        blk = _block(v, e - s_ + 1)
        acc = blk if acc is None else _merge4(acc, blk)
    return acc


def _runs_longest(runs):
    best, cur, prev = 0, 0, object()
    for s_, e, v in runs:
        cur = cur + (e - s_ + 1) if v == prev else (e - s_ + 1)
        prev = v
        best = max(best, cur)
    return best


def _runs_prefix_search(runs, x, strict):
    acc = 0
    for s_, e, v in runs:
        n = e - s_ + 1
        if v == 0:
            if acc > x or (not strict and acc == x):
                return s_
            continue
        if v < 0:  # the sums only fall along this run: just its first position can pass
            if acc + v > x or (not strict and acc + v == x):
                return s_
            acc += v * n
            continue
        need = x - acc  # smallest t >= 1 with acc + v * t >= x (or > x)
        t = max(1, (need // v + 1) if strict else -(-need // v))
        if t <= n:
            return s_ + t - 1
        acc += v * n
    return None


def sparse_query(op, R, args, ctx):
    if op in ("leftmostIndexOf", "rightmostIndexOf"):  # (the whole index range)
        op, args = op + "InRange", [R.lo, R.hi, *args]
    l, r, *xs = args
    runs = R.runs(l, r)
    vals = [v for _, _, v in runs]
    if op == "rangeSum": return sum(v * (e - s_ + 1) for s_, e, v in runs)
    if op == "rangeSumMod": return sum(v * (e - s_ + 1) for s_, e, v in runs) % ctx["mod"]
    if op == "rangeMin": return min(vals)
    if op == "rangeMax": return max(vals)
    if op == "rangeGcd": return reduce(math.gcd, (abs(v) for v in vals), 0)
    if op == "rangeAndQuery": return reduce(lambda a, b: a & b, vals)
    if op == "rangeXorQuery": return reduce(lambda a, b: a ^ b, (v for s_, e, v in runs if (e - s_) % 2 == 0), 0)
    if op in ("rangeHash", "rangeHashReversed", "rangesEqual", "isPalindrome"):  # (what hashes promise: equal sequences)
        def seq(a, b):
            out = []
            for s_, e, v in R.runs(a, b):
                if out and out[-1][0] == v:
                    out[-1][1] += e - s_ + 1
                else:
                    out.append([v, e - s_ + 1])
            return out
        if op == "isPalindrome":
            return seq(l, r) == seq(l, r)[::-1]
        first = seq(l, r)
        return (first[::-1] if op == "rangeHashReversed" else first) == seq(xs[0], xs[1])
    if op == "rangeOrQuery": return reduce(lambda a, b: a | b, vals)
    if op == "maxSubarraySum": return _runs_sub(runs)[3]
    if op == "maxPrefixSum": return _runs_sub(runs)[1]
    if op == "maxSuffixSum": return _runs_sub(runs)[2]
    if op == "minPrefixSum": return -_runs_sub([(s_, e, -v) for s_, e, v in runs])[1]  # (min of a = -max of -a)
    if op == "minSuffixSum": return -_runs_sub([(s_, e, -v) for s_, e, v in runs])[2]
    if op == "minSubarraySum": return -_runs_sub([(s_, e, -v) for s_, e, v in runs])[3]
    if op.endswith(("SumLtX", "SumLteX")):  # (the > / >= search on -a with -x)
        neg = [(s_, e, -v) for s_, e, v in runs]
        if op.startswith("rightmost"):
            hit = _runs_prefix_search([(-e, -s_, v) for s_, e, v in neg[::-1]], -xs[0], op.endswith("LtX"))
            return R.lo - 1 if hit is None else -hit
        hit = _runs_prefix_search(neg, -xs[0], op.endswith("LtX"))
        return R.lo - 1 if hit is None else hit
    if op == "longestEqualRun": return _runs_longest(runs)
    if op == "maxAltSubseqSum": return _max_alt([v for s_, e, v in runs for _ in range(min(3, e - s_ + 1))])
    if op in ("rightmostSuffixSumGteX", "rightmostSuffixSumGtX"):  # mirror the runs and search from r leftwards
        hit = _runs_prefix_search([(-e, -s_, v) for s_, e, v in runs[::-1]], xs[0], op.endswith("GtX"))
        return R.lo - 1 if hit is None else -hit
    if op in ("leftmostPrefixSumGteX", "leftmostPrefixSumGtX"):  # not found: lo - 1 (-1 when lo = 0)
        hit = _runs_prefix_search(runs, xs[0], op.endswith("GtX"))
        return R.lo - 1 if hit is None else hit
    for side in ("leftmost", "rightmost"):
        for name, cmp in CMP.items():
            if op == f"{side}{name}X":
                order = runs if side == "leftmost" else runs[::-1]
                hit = next(((s_, e) for s_, e, v in order if cmp(v, xs[0])), None)
                return R.lo - 1 if hit is None else (hit[0] if side == "leftmost" else hit[1])
    if op in ("leftmostIndexOfInRange", "rightmostIndexOfInRange"):  # not found: lo - 1
        order = runs if op.startswith("left") else runs[::-1]
        hit = next(((s_, e) for s_, e, v in order if v == xs[0]), None)
        return R.lo - 1 if hit is None else (hit[0] if op.startswith("left") else hit[1])
    n_of = lambda run: run[1] - run[0] + 1  # noqa: E731
    if op == "countOccurrences": return sum(n_of(x) for x in runs if x[2] == xs[0])
    if op == "countDistinct": return len(set(vals))
    if op == "allDistinct": return all(n_of(x) == 1 for x in runs) and len(set(vals)) == len(vals)
    if op == "doAllElementsAppearEvenFrequency":
        tot = Counter()
        for x in runs:
            tot[x[2]] += n_of(x)
        return all(c % 2 == 0 for c in tot.values())
    if op == "rangeMode":
        tot = Counter()
        for x in runs:
            tot[x[2]] += n_of(x)
        return ("modecounts", tot)
    if op == "rangeLIS": return _lis(vals)
    if op == "rangeLDS": return _lis(vals[::-1])
    if op == "countInValRange": return sum(n_of(x) for x in runs if xs[0] <= x[2] <= xs[1])
    if op == "sumInValRange": return sum(n_of(x) * x[2] for x in runs if xs[0] <= x[2] <= xs[1])
    if op in ORDER_OPS:
        tot = Counter()
        for x in runs:
            tot[x[2]] += n_of(x)
        return order_stat(op, tot, r - l + 1, xs)
    if op == "costMonoIncreasing": return _cost_pieces([(v, e - s_ + 1, 0) for s_, e, v in runs])
    if op == "costMonoDecreasing": return _cost_pieces([(v, e - s_ + 1, 0) for s_, e, v in runs[::-1]])
    if op == "costStrictIncreasing": return _cost_pieces([(v - (s_ - l), e - s_ + 1, -1) for s_, e, v in runs])
    if op == "costStrictDecreasing": return _cost_pieces([(v + (e - l), e - s_ + 1, -1) for s_, e, v in runs[::-1]])
    for name, cmp in CMP.items():
        if op == f"kth{name}X":
            return _runs_kth(runs, xs[0], lambda v, cmp=cmp: cmp(v, xs[1]), R.lo)
    raise KeyError(f"no sparse brute force for {op}")


def _runs_kth(runs, k, pred, lo):  # index of the k-th i (1-indexed) whose value passes pred, or lo - 1
    if k <= 0:
        return lo - 1
    for s_, e, v in runs:
        if pred(v):
            n = e - s_ + 1
            if k <= n:
                return s_ + k - 1
            k -= n
    return lo - 1


def _cost_pieces(pieces):
    """min +1 increments to make a sequence non-decreasing, given as pieces (start value, length, slope) whose
    values are start + slope * t with slope 0 or -1 (so a piece's own max is its first value)."""
    mx, cost = None, 0
    for sv, n, slope in pieces:
        mx = sv if mx is None else max(mx, sv)
        cost += n * (mx - sv) - slope * n * (n - 1) // 2
    return cost


AP_OPS = {"rangeAddArithSeq", "rangeAddArithSeqMod"}


class Linear:
    """For arithmetic-progression adds: the array as disjoint pieces [a, b] holding c0 + c1 * i (assign overwrites)."""
    def __init__(self, lo=None, hi=None):
        self.pieces = [[lo, hi, 0, 0]] if lo is not None else []

    def _split(self, i):  # make a piece start at i
        for k, (a, b, c0, c1) in enumerate(self.pieces):
            if a < i <= b:
                self.pieces[k:k + 1] = [[a, i - 1, c0, c1], [i, b, c0, c1]]
                return

    def _inside(self, l, r):
        self._split(l)
        self._split(r + 1)
        return [p for p in self.pieces if l <= p[0] and p[1] <= r]

    def add(self, l, r, c0, c1):
        for p in self._inside(l, r):
            p[2] += c0
            p[3] += c1

    def assign(self, l, r, v):
        for p in self._inside(l, r):
            p[2], p[3] = v, 0

    def get(self, i):
        return next(c0 + c1 * i for a, b, c0, c1 in self.pieces if a <= i <= b)

    def sum(self, l, r):
        tot = 0
        for a, b, c0, c1 in self.pieces:
            a, b = max(a, l), min(b, r)
            if a <= b:
                tot += c0 * (b - a + 1) + c1 * (a + b) * (b - a + 1) // 2
        return tot


def sparse_expected(trials, ctx, ops):
    linear = bool(AP_OPS & set(ops))
    mod, full = ctx["mod"], ctx["full"]
    exp = []
    for head, seq in trials:
        lo, hi = head[:2]
        R = Linear(lo, hi) if linear else Runs(lo, hi)
        for i, v in (head[2] if len(head) > 2 else []):
            R.update(i, i, lambda _v, v=v: v)
        get = (lambda i: R.get(i) % mod) if (linear and mod) else R.get
        for op, args in seq:
            if op.startswith("!"):
                exp.append("OOR")
            elif op == "pointGet":
                exp.append(get(args[0]))
            elif op in POINT_UPDATES:
                i, v = args
                cur = get(i)
                new = {"pointAssign": v, "pointAdd": cur + v, "pointChmax": max(cur, v), "pointChmin": min(cur, v)}[op]
                if full is not None:
                    new &= full
                if mod:
                    new %= mod
                if linear:
                    R.add(i, i, new - cur, 0)
                else:
                    R.update(i, i, lambda _v, new=new: new)
            elif op in RANGE_UPDATES:
                l, r, *xs = args
                if linear:
                    if op in AP_OPS:
                        R.add(l, r, xs[0] - xs[1] * l, xs[1])
                    elif op in ("rangeAssign", "rangeAssignMod"):
                        R.assign(l, r, xs[0])
                    else:
                        R.add(l, r, xs[0], 0)
                else:
                    def f(v, op=op, xs=xs):
                        tmp = [v]
                        brute_update(tmp, op, [0, 0, *xs], ctx)
                        return tmp[0]
                    R.update(l, r, f)
            elif linear:
                s_ = R.sum(*args)
                exp.append(s_ % mod if op == "rangeSumMod" else s_)
            else:
                exp.append(sparse_query(op, R, args, ctx))
    return exp


def make_sparse_trials(folder, ops, trials):
    """[((lo, hi), [(op, args)])] with indices from a small pool of huge coordinates, so updates and queries overlap."""
    gen, delta, _, ctx = domain(folder, ops)
    updates = [o for o in ops if o in POINT_UPDATES or o in RANGE_UPDATES]
    queries = [o for o in ops if o not in updates]
    out = []
    for t in range(trials):
        rng = random.Random(10**6 + t)
        lo = -rng.randint(1, 10**12)
        hi = rng.randint(1, 10**12)
        pool = {lo, hi} | {rng.randint(lo, hi) for _ in range(rng.randint(1, 12))}
        pool |= {min(hi, p + 1) for p in list(pool)[:4]}  # neighbours, to hit run boundaries
        pool = sorted(pool)
        head = (lo, hi)
        if not updates:  # static: built from (index, value) points, every other index 0
            head = (lo, hi, [(i, gen(rng)) for i in sorted(rng.sample(pool, rng.randint(0, len(pool))))])
        seq = []
        for _ in range(OPS_PER_TRIAL):
            op = rng.choice(updates) if updates and rng.random() < 0.5 else rng.choice(queries or updates)
            if op == "pointGet":
                args = [rng.choice(pool)]
            elif op in POINT_UPDATES:
                args = [rng.choice(pool), delta(rng) if op == "pointAdd" else gen(rng)]
            else:
                l, r = sorted((rng.choice(pool), rng.choice(pool)))
                if op in RANGE_UPDATES:
                    args = [l, r] + update_args(op, rng, gen, ctx["mod"])
                else:
                    kind = BRUTE_QUERIES.get(op, ("lr",))[0]
                    k = rng.choice([rng.randint(0, 5), rng.randint(1, 10**12)])
                    if kind == "x":
                        args = [gen(rng)]
                    elif kind == "lrx":
                        args = [l, r, rng.randint(-2, 25) if "PrefixSum" in op or "SuffixSum" in op else gen(rng)]
                    elif kind == "lrkx":
                        args = [l, r, k, gen(rng)]
                    elif kind == "lrk":
                        args = [l, r, k]
                    elif kind in ("lrkv", "lrk0", "lrij"):  # mostly near either end, where the given values sit around the zeros
                        n = r - l + 1
                        pick = lambda: rng.choice([rng.randint(1, min(n, 6)), n + 1 - rng.randint(1, min(n, 6)), rng.randint(1, n)])  # noqa: E731
                        if kind == "lrkv":
                            args = [l, r, pick()]
                        elif kind == "lrk0":
                            args = [l, r, rng.choice([0, n, pick()])]
                        else:
                            args = [l, r, *sorted((pick(), pick()))]
                    elif kind == "lrlohi":
                        args = [l, r, *sorted((gen(rng), gen(rng)))]
                    elif kind == "lr2":  # a second range, mostly of the same length (equal when both are all zeros)
                        l2 = rng.choice(pool)
                        r2 = l2 + (r - l) if l2 + (r - l) <= hi and rng.random() < 0.9 else max(l2, rng.choice(pool))
                        args = [l, r, l2, r2]
                    else:
                        args = [l, r]
            seq.append((op, args))
        seq += bad_calls(seq, lo, hi, rng)
        out.append((head, seq))
    return out, ctx


# ------------------------------------------------------------------------------------------------ Python side

def owner(op, table):
    """The class/struct implementing op, preferring the one implementing the most ops overall, then the one defined
    last in the file (a wrapper is defined after the class it wraps). table is in file order."""
    order = {n: k for k, n in enumerate(table)}
    cands = [n for n, ms in table.items() if op in ms]
    return max(cands, key=lambda n: (len(table[n]), order[n])) if cands else None


def trial_extra(ctor_extra, seq):
    """["UPDATES"] (the offline merge sort trees): the list of every (i, v) this trial's pointAssigns use."""
    if ctor_extra == ["UPDATES"]:
        return [[tuple(args) for op, args in seq if op == "pointAssign"]]
    return ctor_extra


def run_python(folder, ops, trials, ctor_extra, stem="template"):
    path = os.path.join(DIR, folder, f"{stem}.py")
    spec = importlib.util.spec_from_file_location("t_" + re.sub(r"\W", "_", folder), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    classes = {n: c for n, c in inspect.getmembers(mod, inspect.isclass) if c.__module__ == mod.__name__}
    src = open(path).read()
    classes = dict(sorted(classes.items(), key=lambda kv: src.find(f"class {kv[0]}")))  # file order
    table = {n: {o for o in ops if hasattr(c, o)} for n, c in classes.items()}
    missing = [o for o in ops if owner(o, table) is None]
    if missing:
        raise RuntimeError(f"{stem}.py has no method for {missing}")
    def can_start_empty(cls):  # (an optional initial array and append: then every other trial starts empty and appends)
        try:
            first = next(iter(list(inspect.signature(cls.__init__).parameters.values())[1:]), None)
        except (TypeError, ValueError):
            return False
        return first is not None and first.default is not inspect.Parameter.empty and hasattr(cls, "append")

    def build(name, a0, extra, k):
        cls = classes[name]
        if stem == "sparse":
            return cls(*a0, *extra)
        if k % 2 and not extra and can_start_empty(cls):  # (regression: values typed only once they arrive, e.g. chars)
            obj = cls()
            for v in a0:
                obj.append(v)
            return obj
        return cls(list(a0), *extra)

    out = []
    for k, (a0, seq) in enumerate(trials):
        objs, pieces = {}, []
        extra = trial_extra(ctor_extra, seq)
        for op, args in seq:
            if op.startswith("!"):  # (must raise IndexError)
                name = owner(op[1:], table)
                if name not in objs:
                    objs[name] = build(name, a0, extra, k)
                try:
                    res = getattr(objs[name], op[1:])(*args)
                    out.append(f"no error, returned {norm(res)}")
                except IndexError:
                    out.append("OOR")
                continue
            name = owner(op, table)
            if op in PIECE_OPS:
                if name not in objs:  # (built once: a throwaway build would still share the class's node pool)
                    objs[name] = build(name, a0, extra, k)
                obj = objs[name]
                if op == "cut":
                    pieces.append(obj.cut(*args))
                elif op == "copy":
                    pieces.append(obj.copy() if args == [0, obj.size() - 1] else obj.copy(*args))
                elif op in ("split", "trisect"):
                    first, *rest = getattr(obj, op)(*args)
                    if obj.size():
                        raise RuntimeError(f"{op} left {obj.size()} values behind")
                    obj.merge(first)
                    pieces += rest
                else:
                    piece = pieces.pop()
                    if args[-1]:
                        piece.rangeReverse(0, piece.size() - 1)
                    if op == "paste":
                        obj.paste(args[0], piece)
                    else:
                        obj.merge(piece)
                continue
            if name not in objs:
                objs[name] = build(name, a0, extra, k)
            if op in ("rangeHash", "rangeHashReversed"):
                res = getattr(objs[name], op)(*args[:2]) == objs[name].rangeHash(*args[2:])
            elif op == "hashAllReversed":  # (against rangeHashReversed(l, r): equal only on the whole array)
                res = objs[name].hashAllReversed() == objs[name].rangeHashReversed(*args)
            elif op == "hashAll":  # (against the hash of a[l..r]: equal only when that is the whole array)
                if "rangeHash" in ops:
                    res = objs[name].hashAll() == objs[name].rangeHash(*args)
                else:  # (a second structure over a[l..r]: the same base and mod per run, so equal content hashes equal)
                    piece = objs[name].getAll()[args[0]:args[1] + 1]
                    res = objs[name].hashAll() == classes[name](piece, *extra).hashAll()
            else:
                res = getattr(objs[name], op)(*args)
            if not is_update(op) or op in SEQ_OUT:
                out.append(norm(res))
    return out


# ------------------------------------------------------------------------------------------------ C++ side

def find_cxx():
    cands = [os.environ["CXX"]] if os.environ.get("CXX") else [f"g++-{v}" for v in range(15, 10, -1)] + ["g++"]
    for c in cands:
        exe = shutil.which(c) or (c if os.path.exists(c) else None)
        if not exe:
            continue
        probe = subprocess.run([exe, "-std=c++17", "-x", "c++", "-fsyntax-only", "-"], input="#include <bits/stdc++.h>\n",
                               capture_output=True, text=True)
        if probe.returncode == 0:
            return exe
    return None


def cpp_structs(path):
    """{struct name: set of method names} for each top-level `template <typename T> struct X`."""
    lines = open(path).read().split("\n")
    out, i = {}, 0
    while i < len(lines):
        if re.match(r"\s*template\s*<\s*typename\s+T", lines[i]) and i + 1 < len(lines):
            m = re.match(r"\s*struct\s+(\w+)", lines[i + 1])
            if m:
                name, depth, methods, j = m.group(1), 0, set(), i + 1
                while j < len(lines):
                    mm = re.match(r"\s*(?:[\w:<>,\s\*&]+?)\s+(\w+)\s*\(", lines[j]) if depth == 1 else None
                    if mm:
                        methods.add(mm.group(1))
                    depth += lines[j].count("{") - lines[j].count("}")
                    if depth == 0 and "}" in lines[j]:
                        break
                    j += 1
                out[name] = methods
                i = j
        i += 1
    return out


def cpp_driver(folder, ops, structs, ctor_extra, stem="template", chars=False):
    table = {n: ms & set(ops) for n, ms in structs.items()}  # rank structs by the operations they implement
    owners = {op: owner(op, table) for op in ops}
    missing = [op for op, o in owners.items() if o is None]
    if missing:
        raise RuntimeError(f"{stem}.cpp has no method for {missing}")
    used = sorted(set(owners.values()))
    updates = ctor_extra == ["UPDATES"]  # (read per trial: m, then m pairs (i, v), after the array)
    extra = ", ups" if updates else "".join(f", vector<long long>{{{', '.join(map(str, e))}}}" if isinstance(e, list) else
                    f", (char){ord(e)}" if isinstance(e, str) else f", {e}" for e in ctor_extra)
    lines = ["#include <bits/stdc++.h>", "using namespace std;", f'#include "{cpp_path(folder, stem)}"']
    lines += [f"template struct {s}<int>;" for s in used]  # type-check the generic code for int too
    if stem == "letters":  # and for char: the letters version runs with T = char
        lines += [f"template struct {s}<char>;" for s in used]
    lines += [
        "template <class X> void out(const X& x) { cout << x << '\\n'; }",
        "void out(bool b) { cout << (b ? 1 : 0) << '\\n'; }",
        "template <class A, class B> void out(const pair<A, B>& p) { cout << p.first << ' ' << p.second << '\\n'; }",
        "template <class X> void out(const optional<X>& o) { if (o) cout << *o << '\\n'; else cout << \"None\\n\"; }",
        "template <class X> void out(const vector<X>& v) { for (size_t i = 0; i < v.size(); i++) cout << (i ? \" \" : \"\") << v[i]; cout << '\\n'; }",
        "int main() {",
        "  ios::sync_with_stdio(false); cin.tie(nullptr);",
        "  int cases; cin >> cases;",
        "  while (cases--) {",
    ]
    if stem == "sparse" and not any(o in POINT_UPDATES or o in RANGE_UPDATES for o in ops):
        lines += ["    long long lo, hi; cin >> lo >> hi;", "    int np; cin >> np; vector<pair<long long, long long>> pts(np);",
                  "    for (auto& [i, v] : pts) cin >> i >> v;", "    int q; cin >> q;"]
        lines += [f"    {s}<long long> s_{s}(lo, hi, pts{extra});" for s in used]
    elif stem == "sparse":
        lines += ["    long long lo, hi; cin >> lo >> hi;", "    int q; cin >> q;"]
        lines += [f"    {s}<long long> s_{s}(lo, hi{extra});" for s in used]
    else:
        elem = "char" if chars else "long long"  # chars: values come in as their codes, the structure holds char
        lines += [f"    int n; cin >> n; vector<{elem}> a(n); for (auto& x : a) {{ long long v; cin >> v; x = ({elem})v; }}"]
        if updates:
            lines += [f"    int m; cin >> m; vector<pair<int, {elem}>> ups(m); for (auto& [i, v] : ups) cin >> i >> v;"]
        lines += ["    int q; cin >> q;"]
        lines += [f"    {s}<{elem}> s_{s}(a{extra});" for s in used]
    if any(o in ops for o in PIECE_OPS):
        lines += [f"    vector<{owners[next(o for o in PIECE_OPS if o in ops)]}<{'char' if chars else 'long long'}>> pieces;"]
    lines += ["    while (q--) {", "      string op; cin >> op;", "      bool bad = op[0] == '!';  // (an index out of range: must throw)",
              "      if (bad) op = op.substr(1);", "      try {", "      if (false) {}"]
    for op in ops:
        s = f"s_{owners[op]}"
        if op == "cut":
            body = f"long long l, r; cin >> l >> r; pieces.push_back({s}.cut(l, r));"
        elif op == "copy":
            body = f"long long l, r; cin >> l >> r; pieces.push_back(l == 0 && r == {s}.size() - 1 ? {s}.copy() : {s}.copy(l, r));"
        elif op == "split":
            body = (f"long long k; cin >> k; auto [x, y] = {s}.split(k); if ({s}.size()) return 2; "
                    f"{s}.merge(x); pieces.push_back(std::move(y));")
        elif op == "trisect":
            body = (f"long long l, r; cin >> l >> r; auto [x, y, z] = {s}.trisect(l, r); if ({s}.size()) return 2; "
                    f"{s}.merge(x); pieces.push_back(std::move(y)), pieces.push_back(std::move(z));")
        elif op in ("paste", "merge"):
            read = "long long i, rv; cin >> i >> rv;" if op == "paste" else "long long rv; cin >> rv;"
            body = (f"{read} auto p = std::move(pieces.back()); pieces.pop_back(); " +
                    (f"if (rv) p.rangeReverse(0, p.size() - 1); " if "rangeReverse" in ops else "(void)rv; ") +
                    (f"{s}.paste(i, p);" if op == "paste" else f"{s}.merge(p);"))
        elif op in SEQ_OPS:
            names = {"v": ["v"], "iv": ["i", "v"], "i": ["i"], "lr": ["l", "r"], "lrk": ["l", "r", "k"], "lri": ["l", "r", "i"],
                     "ivk": ["i", "v", "k"], "lrc": ["l", "r", "i"], "none": []}[SEQ_OPS[op]]
            call = f"{s}.{op}({', '.join(names)})"
            body = ((f"long long {', '.join(names)}; cin{''.join(f' >> {x}' for x in names)}; " if names else "") +
                    (f"out({call});" if op in SEQ_OUT else f"{call};"))
        elif op == "pointGet":
            body = f"long long i; cin >> i; out({s}.pointGet(i));"
        elif op in POINT_UPDATES:
            body = f"long long i, v; cin >> i >> v; {s}.{op}(i, v);"
        elif op in RANGE_UPDATES:
            names = ["x", "y"][:RANGE_UPDATES[op]]
            decl = ", ".join(names)
            reads = "".join(f" >> {nm}" for nm in names)
            body = (f"long long l, r, {decl}; cin >> l >> r{reads}; {s}.{op}(l, r, {decl});" if names
                    else f"long long l, r; cin >> l >> r; {s}.{op}(l, r);")
        else:
            kind = BRUTE_QUERIES[op][0]
            if kind == "all":
                body = f"out({s}.{op}());"
            elif kind in ("x", "xv"):
                body = f"long long x; cin >> x; out({s}.{op}(x));"
            elif op in ("rangeHash", "rangeHashReversed"):
                body = f"long long l, r, l2, r2; cin >> l >> r >> l2 >> r2; out({s}.{op}(l, r) == {s}.rangeHash(l2, r2));"
            elif kind == "lr2":
                body = f"long long l, r, l2, r2; cin >> l >> r >> l2 >> r2; out({s}.{op}(l, r, l2, r2));"
            elif kind == "lr":
                body = f"long long l, r; cin >> l >> r; out({s}.{op}(l, r));"
            elif kind == "lrs":
                body = f"long long l, r, step; cin >> l >> r >> step; out({s}.{op}(l, r, step));"
            elif op == "hashAllReversed":
                body = f"long long l, r; cin >> l >> r; out({s}.{op}() == {s}.rangeHashReversed(l, r));"
            elif kind == "hall":
                body = (f"long long l, r; cin >> l >> r; out({s}.{op}() == {s}.rangeHash(l, r));" if "rangeHash" in ops else
                        f"long long l, r; cin >> l >> r; auto w = {s}.getAll(); "
                        f"{owners[op]}<{elem}> tmp(vector<{elem}>(w.begin() + l, w.begin() + r + 1){extra}); out({s}.{op}() == tmp.{op}());")
            elif kind == "i":
                body = f"long long i; cin >> i; out({s}.{op}(i));"
            elif kind == "lrx":
                body = f"long long l, r, x; cin >> l >> r >> x; out({s}.{op}(l, r, x));"
            elif kind == "lrkx":
                body = f"long long l, r, k, x; cin >> l >> r >> k >> x; out({s}.{op}(l, r, k, x));"
            elif kind in ("lrk", "lrkv", "lrk0"):
                body = f"long long l, r, k; cin >> l >> r >> k; out({s}.{op}(l, r, k));"
            elif kind == "lrij":
                body = f"long long l, r, i, j; cin >> l >> r >> i >> j; out({s}.{op}(l, r, i, j));"
            elif kind in ("lrxk", "lrxi"):
                body = f"long long l, r, x, k; cin >> l >> r >> x >> k; out({s}.{op}(l, r, x, k));"
            elif kind == "lrxlohi":
                body = f"long long l, r, x, lo, hi; cin >> l >> r >> x >> lo >> hi; out({s}.{op}(l, r, x, lo, hi));"
            else:
                body = f"long long l, r, lo, hi; cin >> l >> r >> lo >> hi; out({s}.{op}(l, r, lo, hi));"
        lines.append(f'      else if (op == "{op}") {{ {body} }}')
    lines += ["      else { cerr << \"unknown op \" << op << '\\n'; return 1; }",
              "      if (bad) cout << \"no error\\n\";",
              "      } catch (const out_of_range&) { if (!bad) throw; cout << \"OOR\\n\"; }", "    }", "  }", "}"]
    return "\n".join(lines) + "\n"


def code(v):  # a value as the C++ driver reads it: characters go in as their codes
    return str(ord(v)) if isinstance(v, str) else str(v)


def cpp_path(folder, stem):
    """The C++ file a test runs: with --fast, its fast version."""
    name = stem + ".cpp" if not FAST else "fast.cpp" if stem == "template" else f"{stem}-fast.cpp"
    return os.path.join(DIR, folder, name)


def run_cpp(folder, ops, trials, ctor_extra, cxx, stem="template", chars=False):
    path = cpp_path(folder, stem)
    os.makedirs(BUILD, exist_ok=True)
    tag = hashlib.md5(folder.encode()).hexdigest()[:8] if len(folder) > 140 else ""  # (long names cut short stay distinct)
    src = os.path.join(BUILD, (folder[:140] + tag + ("" if stem == "template" else "__" + stem) + ("__chars" if chars else "")) + ".cpp")
    exe = src[:-4]
    open(src, "w").write(cpp_driver(folder, ops, cpp_structs(path), ctor_extra, stem, chars))
    comp = subprocess.run([cxx, "-std=c++17", "-O2", "-Wall", "-o", exe, src], capture_output=True, text=True)
    if comp.returncode:
        raise RuntimeError("compile error:\n" + comp.stderr[:3000])
    inp = [str(len(trials))]
    for a0, seq in trials:
        if stem == "sparse":
            inp += [f"{a0[0]} {a0[1]}"] + ([f"{len(a0[2])} " + " ".join(f"{i} {v}" for i, v in a0[2])] if len(a0) > 2 else [])
        else:
            inp += [str(len(a0)), " ".join(map(code, a0))]
            if ctor_extra == ["UPDATES"]:
                ups = trial_extra(ctor_extra, seq)[0]
                inp += [f"{len(ups)} " + " ".join(f"{i} {v}" for i, v in ups)]
        inp += [str(len(seq))]
        inp += [f"{op} {' '.join(map(code, args))}" for op, args in seq]
    run = subprocess.run([exe], input="\n".join(inp) + "\n", capture_output=True, text=True, timeout=300)
    if run.returncode:
        raise RuntimeError(f"binary exited {run.returncode}: {run.stderr[:500]}")
    return run.stdout.split("\n")[:-1], comp.stderr.strip()


# ------------------------------------------------------------------------------------------------ main

def parse_ops(path, comment):
    m = re.search(rf"^{re.escape(comment)} @operations: (.*)$", open(path).read(), re.M)
    return m.group(1).split() if m else None


def main():
    args = sys.argv[1:]
    want_py = "--cpp" not in args
    want_cpp = "--py" not in args
    global FAST
    FAST = "--fast" in args
    trials_n = 120
    if "--trials" in args:
        trials_n = int(args[args.index("--trials") + 1])
        args = [x for k, x in enumerate(args) if x != "--trials" and (k == 0 or args[k - 1] != "--trials")]
    exact = None
    if "--from" in args:  # --from FILE: exactly the folders listed in FILE (one per line)
        k = args.index("--from")
        exact = set(open(args[k + 1]).read().split())
        args = args[:k] + args[k + 2:]
    shard = None
    if "--shard" in args:  # --shard k/n: the k-th of n interleaved slices of the folder list (k from 0)
        k = args.index("--shard")
        shard = tuple(int(x) for x in args[k + 1].split("/"))
        args = args[:k] + args[k + 2:]
    letters = "--letters" in args
    filters = [x for x in args if not x.startswith("--")]
    cxx = find_cxx() if want_cpp else None
    if want_cpp and not cxx:
        print("no GCC with bits/stdc++.h found (set CXX); running Python only\n")
        want_cpp = False

    folders = sorted(f for f in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, f)))
    if filters:
        folders = [f for f in folders if any(x in f for x in filters)]
    if exact is not None:
        folders = [f for f in folders if f in exact]
    if shard is not None:
        folders = folders[shard[0]::shard[1]]
    failed, total_queries = [], 0
    for folder in folders:
        py = os.path.join(DIR, folder, "template.py")
        cpp = os.path.join(DIR, folder, "template.cpp")
        ops = parse_ops(py, "#") if os.path.exists(py) else parse_ops(cpp, "//")
        unknown = [o for o in ops if o not in BRUTE_QUERIES and o not in RANGE_UPDATES and o not in POINT_UPDATES and o not in SEQ_OPS and o != "pointGet"]
        if unknown:
            failed.append(folder)
            print(f"FAIL  {folder}\n      no brute force for {unknown}: add it to BRUTE_QUERIES / RANGE_UPDATES")
            continue
        ctor_extra = num_extra = domain(folder, ops)[2]
        if letters:  # each template as it is offered for characters: its letters version, or itself if it takes them
            if os.path.exists(os.path.join(DIR, folder, "letters.py")):
                stem0, ops = "letters", parse_ops(os.path.join(DIR, folder, "letters.py"), "#")
            else:
                stem0, ops = "template", [o for o in ops if o in CHAR_SAFE]
                if "@letters: same" not in open(py).read():
                    continue  # numbers only
            ctor_extra = letters_extra(folder, ops, ctor_extra)
            variants = [(stem0, *make_trials(folder, ops, trials_n, letters))]
        else:
            variants = [("template", *make_trials(folder, ops, trials_n))]
        sparse_ops = [o for o in ops if o != "getAll"]  # a sparse tree over a huge index range has no getAll
        spath = os.path.join(DIR, folder, "sparse.py")
        if os.path.exists(spath) and set(parse_ops(spath, "#")) < set(sparse_ops):
            sparse_ops = parse_ops(spath, "#")  # (and may lack ops it has no version of: the beats searches)
        if not letters and any(os.path.exists(os.path.join(DIR, folder, f"sparse.{x}")) for x in ("py", "cpp")):
            variants.append(("sparse", *make_sparse_trials(folder, sparse_ops, trials_n)))
        lpath = os.path.join(DIR, folder, "letters.py")
        lops = parse_ops(lpath, "#") if not letters and os.path.exists(lpath) else None
        if lops:  # a letters version: Python on letters; C++ (generic over T) on the usual numbers
            variants.append(("letters", *make_trials(folder, lops, trials_n, letters=True)))
        for stem, trials, ctx in variants:
            vops = ops if stem == "template" or letters else lops if stem == "letters" else sparse_ops
            exp = sparse_expected(trials, ctx, vops) if stem == "sparse" else expected_outputs(trials, ctx)
            total_queries += len(exp)
            results = []
            for lang, ok_lang, path in (("py", want_py, os.path.join(DIR, folder, f"{stem}.py")),
                                        ("cpp", want_cpp, cpp_path(folder, stem))):
                if not ok_lang or not os.path.exists(path):
                    continue
                try:
                    if not letters and parse_ops(path, "#" if lang == "py" else "//") != vops:
                        raise RuntimeError(f"{stem}.{lang} @operations differ from template.py's" + (" (less getAll)" if stem == "sparse" else ""))
                    if letters and lang == "cpp":  # the real thing: T = char, so ASCII letters (see char_letter_base)
                        results.append((lang, *run_cpp_letters(folder, vops, trials_n, num_extra, cxx, stem)))
                        continue
                    if stem == "letters" and lang == "cpp":
                        ntrials, nctx = make_trials(folder, vops, trials_n)
                        got, warn = run_cpp(folder, vops, ntrials, ctor_extra, cxx, stem)
                        results.append((lang, first_mismatch(got, expected_outputs(ntrials, nctx), ntrials, False), warn))
                        continue
                    if lang == "py":
                        extra = letters_extra(folder, vops, ctor_extra) if stem == "letters" else ctor_extra
                        got, warn = run_python(folder, vops, trials, extra, stem), ""
                    else:
                        got, warn = run_cpp(folder, vops, trials, ctor_extra, cxx, stem)
                    results.append((lang, first_mismatch(got, exp, trials, lang == "cpp" and stem == "sparse"), warn))
                except Exception as e:  # noqa: BLE001 -- report and keep going
                    results.append((lang, f"{type(e).__name__}: {e}", ""))
            if not results:
                continue  # nothing to run: a --fast test of a folder with no fast version
            bad = [(lang, msg) for lang, msg, _ in results if msg]
            warns = [(lang, w) for lang, _, w in results if w]
            label = folder + ("  [sparse]" if stem == "sparse" else "  [letters]" if stem == "letters" else "")
            print(f"{'FAIL' if bad else 'PASS'}  {label}  [{' '.join(lang for lang, _, _ in results)}]")
            for lang, msg in bad:
                print(f"      {lang}: {msg}")
            for lang, w in warns:
                print(f"      {lang} compiler warnings: {w[:400]}")
            if bad:
                failed.append(label)
    print(f"\n{len(failed)} failed across {len(folders)} templates ({total_queries} brute-force answers each checked per language)" if failed
          else f"\nall {len(folders)} templates passed, sparse versions included ({total_queries} brute-force answers each checked per language)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
