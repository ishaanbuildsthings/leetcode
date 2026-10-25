"""Order statistics over a[l..r] of a static array: every query the sets picker answers about one multiset, asked about
the multiset of a subarray instead. Writes template.* and sparse.* for each folder.

    python3 gen_wavelet.py

The Pareto frontier:
  wavelet-order-stats            counts, k-th, medians, min / max, predecessor / successor   N log N
  wavelet-order-stats-sums       + every sum (k smallest, value ranges, |a[i] - x|)          2 N log N
  wavelet-order-stats-mex        + rangeMex (a persistent seg tree; a wavelet can't do mex)   4 N log N
  wavelet-order-stats-sums-mex   all of it                                                    5 N log N
  pointGet-rangeMex              the persistent mex tree alone                                3 N log N
A persistent count / sum tree answers the same counts, k-th and sums in the same O(log N), but needs 4 N log N
against the wavelet's 2 N log N, so it isn't kept. Mex is not a count: it needs, per value, its last index in the
prefix, which only the persistent tree stores.

The op lists are too long for folder names (255 bytes), so these folders are named by structure.
"""
import os

from note_lang import write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")

BASE = ["countGtX", "countGteX", "countInValRange", "countLtX", "countLteX", "countOccurrences", "kthLargest", "kthSmallest",
        "largestLtX", "largestLteX", "medianHigh", "medianLow", "pointGet", "rangeMax", "rangeMin", "smallestGtX", "smallestGteX"]
SUMS = ["rangeSum", "sumAbsDiffToMedian", "sumAbsDiffToX", "sumGtX", "sumGteX", "sumInValRange", "sumKthLargestRange",
        "sumKthSmallestRange", "sumLargestK", "sumLtX", "sumLteX", "sumSmallestK"]
MEX = ["rangeMex"]
LOGN = "1*N*log(N)"


def header(cm, ops, dtype, sparse, node, other, note):
    lines = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {dtype}", "@complexities:"]
    lines += [f"  {op}: {'1' if op == 'pointGet' and not sparse else 'log(N)'}" for op in ops] + ["  build: N*log(N)"]
    lines += ["@memory:", f"  layout: {'sparse' if sparse else 'none'}", f"  node: {node}", "  tags: none", f"  other: {other}",
              "  note: " + (("built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; "
                             "costs are in N; ") if sparse else "") + note]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def memory(sums, mex, sparse):
    if sums is None:  # persistent mex alone
        node, other = f"ML[{LOGN}] MR[{LOGN}] MN[{LOGN}]", "root[1*N] arr[1*N]"
    else:  # no nodes in a wavelet matrix: every array is listed together
        node = f"zeros[{LOGN}]" + (f" zsum[{LOGN}]" if sums else "") + " arr[1*N] srt[1*N]" + \
            (f" mexRoot[1*N] ML[{LOGN}] MR[{LOGN}] MN[{LOGN}]" if mex else "")
        if sparse:
            node = "idx[1*N] vals[1*N] " + node
        return node, "none"
    if sparse:
        other = "idx[1*N] vals[1*N] " + other
    return node, other


def note(sums, mex, sparse):
    if sums is None:
        n = ("persistent seg tree over the values 0..N+1; version p holds each value's last index before p, and the mex of "
             "a[l..r] is the first value whose last index is < l")
    else:
        n = ("wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value"
             + (", plus one row of prefix sums of the values that go left" if sums else "")
             + ("; rangeMex uses a persistent seg tree over the values 0..N+1 holding each value's last index" if mex else ""))
    if sparse:
        n += "; the structure is over the given values only, and the zeros of [l, r] are added in closed form (they sit " \
             "between the negatives and the positives)"
    return n


# ================================================================================================ Python, dense

PY_DOC = '''# Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
# 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x, lowVal,
# ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the ranks
# with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0, so a window
# [lo, hi) maps to [zeros[d][lo], zeros[d][hi]) among the 0s and to [nz + lo - zeros[d][lo], ...) among the 1s.
'''
PY_SUM_DOC = '''# zsum[d][i] = sum of the values among the first i elements of level d's order whose bit is 0.
'''
PY_MEX_DOC = '''# rangeMex: a persistent seg tree over the values 0..N+1; version p holds, per value, its last index before p (-1 if
# none). The mex of a[l..r] is the first value whose last index in version r + 1 is < l.
'''

PY_OPS = {
    "pointGet": '''    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]
''',
    "countOccurrences": '''    # O(logN) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        return self.countInValRange(l, r, x, x)
''',
    "countInValRange": '''    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    def countInValRange(self, l, r, lowVal, highVal):
        if lowVal > highVal:
            return 0
        return self._countBelow(l, r, bisect_right(self.srt, highVal)) - self._countBelow(l, r, bisect_left(self.srt, lowVal))
''',
    "countLtX": '''    # O(logN) -- # of values < x in a[l..r]
    def countLtX(self, l, r, x):
        return self._countBelow(l, r, bisect_left(self.srt, x))
''',
    "countLteX": '''    # O(logN) -- # of values <= x in a[l..r]
    def countLteX(self, l, r, x):
        return self._countBelow(l, r, bisect_right(self.srt, x))
''',
    "countGtX": '''    # O(logN) -- # of values > x in a[l..r]
    def countGtX(self, l, r, x):
        return r - l + 1 - self._countBelow(l, r, bisect_right(self.srt, x))
''',
    "countGteX": '''    # O(logN) -- # of values >= x in a[l..r]
    def countGteX(self, l, r, x):
        return r - l + 1 - self._countBelow(l, r, bisect_left(self.srt, x))
''',
    "kthSmallest": '''    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else IndexError
    def kthSmallest(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)
''',
    "kthLargest": '''    # O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else IndexError
    def kthLargest(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthLargest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, r - l + 2 - k)
''',
    "medianLow": '''    # O(logN) -- lower median of a[l..r]: its ceil(len / 2)-th smallest
    def medianLow(self, l, r):
        return self._kth(l, r, (r - l + 2) // 2)
''',
    "medianHigh": '''    # O(logN) -- upper median of a[l..r]: its (floor(len / 2) + 1)-th smallest
    def medianHigh(self, l, r):
        return self._kth(l, r, (r - l + 1) // 2 + 1)
''',
    "rangeMin": '''    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        return self._kth(l, r, 1)
''',
    "rangeMax": '''    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        return self._kth(l, r, r - l + 1)
''',
    "smallestGteX": '''    # O(logN) -- smallest value >= x in a[l..r], or None
    def smallestGteX(self, l, r, x):
        c = self._countBelow(l, r, bisect_left(self.srt, x))
        return None if c == r - l + 1 else self._kth(l, r, c + 1)
''',
    "smallestGtX": '''    # O(logN) -- smallest value > x in a[l..r], or None
    def smallestGtX(self, l, r, x):
        c = self._countBelow(l, r, bisect_right(self.srt, x))
        return None if c == r - l + 1 else self._kth(l, r, c + 1)
''',
    "largestLteX": '''    # O(logN) -- largest value <= x in a[l..r], or None
    def largestLteX(self, l, r, x):
        c = self._countBelow(l, r, bisect_right(self.srt, x))
        return None if c == 0 else self._kth(l, r, c)
''',
    "largestLtX": '''    # O(logN) -- largest value < x in a[l..r], or None
    def largestLtX(self, l, r, x):
        c = self._countBelow(l, r, bisect_left(self.srt, x))
        return None if c == 0 else self._kth(l, r, c)
''',
    "rangeSum": '''    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._sumFirst(l, r, r - l + 1)
''',
    "sumInValRange": '''    # O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    def sumInValRange(self, l, r, lowVal, highVal):
        if lowVal > highVal:
            return 0
        return self._sumBelow(l, r, bisect_right(self.srt, highVal)) - self._sumBelow(l, r, bisect_left(self.srt, lowVal))
''',
    "sumLtX": '''    # O(logN) -- sum of the values < x in a[l..r]
    def sumLtX(self, l, r, x):
        return self._sumBelow(l, r, bisect_left(self.srt, x))
''',
    "sumLteX": '''    # O(logN) -- sum of the values <= x in a[l..r]
    def sumLteX(self, l, r, x):
        return self._sumBelow(l, r, bisect_right(self.srt, x))
''',
    "sumGtX": '''    # O(logN) -- sum of the values > x in a[l..r]
    def sumGtX(self, l, r, x):
        return self._sumFirst(l, r, r - l + 1) - self._sumBelow(l, r, bisect_right(self.srt, x))
''',
    "sumGteX": '''    # O(logN) -- sum of the values >= x in a[l..r]
    def sumGteX(self, l, r, x):
        return self._sumFirst(l, r, r - l + 1) - self._sumBelow(l, r, bisect_left(self.srt, x))
''',
    "sumSmallestK": '''    # O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= k <= r - l + 1, else IndexError
    def sumSmallestK(self, l, r, k):
        if not 0 <= k <= r - l + 1:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, k)
''',
    "sumLargestK": '''    # O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else IndexError
    def sumLargestK(self, l, r, k):
        n = r - l + 1
        if not 0 <= k <= n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n) - self._sumFirst(l, r, n - k)
''',
    "sumKthSmallestRange": '''    # O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 1 <= kFrom <= kTo <= r - l + 1,
    # else IndexError
    def sumKthSmallestRange(self, l, r, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= r - l + 1:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, kTo) - self._sumFirst(l, r, kFrom - 1)
''',
    "sumKthLargestRange": '''    # O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest); needs
    # 1 <= kFrom <= kTo <= r - l + 1, else IndexError
    def sumKthLargestRange(self, l, r, kFrom, kTo):
        n = r - l + 1
        if not 1 <= kFrom <= kTo <= n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n - kFrom + 1) - self._sumFirst(l, r, n - kTo)
''',
    "sumAbsDiffToX": '''    # O(logN) -- sum of |a[i] - x| over i in [l, r]
    def sumAbsDiffToX(self, l, r, x):
        rk = bisect_left(self.srt, x)
        c, s = self._countBelow(l, r, rk), self._sumBelow(l, r, rk)
        return x * c - s + (self._sumFirst(l, r, r - l + 1) - s) - x * (r - l + 1 - c)
''',
    "sumAbsDiffToMedian": '''    # O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    def sumAbsDiffToMedian(self, l, r):
        return self.sumAbsDiffToX(l, r, self._kth(l, r, (r - l + 2) // 2))
''',
    "rangeMex": '''    # O(logN) -- smallest integer >= 0 that is not in a[l..r]
    def rangeMex(self, l, r):
        return self._mexFrom(l, r, 0)
''',
}

PY_CORE = '''
    # ---- internals ----

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        lo, hi, rank, d = l, r + 1, 0, self.bits
        for z in self.zeros:
            d -= 1
            zl, zh = z[lo], z[hi]
            if k <= zh - zl:  # enough 0s at this bit: the answer has it 0
                lo, hi = zl, zh
            else:
                k -= zh - zl
                rank |= 1 << d
                lo, hi = z[-1] + lo - zl, z[-1] + hi - zh
        return self.srt[rank]

    # # of i in [l, r] whose rank is < x
    def _countBelow(self, l, r, x):
        if x <= 0:
            return 0
        if x >= self.m:
            return r - l + 1
        lo, hi, res, d = l, r + 1, 0, self.bits
        for z in self.zeros:
            d -= 1
            zl, zh = z[lo], z[hi]
            if (x >> d) & 1:  # everything with this bit 0 is below x; keep going among the 1s
                res += zh - zl
                lo, hi = z[-1] + lo - zl, z[-1] + hi - zh
            else:
                lo, hi = zl, zh
        return res
'''
PY_SUM_CORE = '''
    # sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    def _sumFirst(self, l, r, k):
        if k <= 0:
            return 0
        lo, hi, rank, res, d = l, r + 1, 0, 0, self.bits
        for z, zs in zip(self.zeros, self.zsum):
            d -= 1
            zl, zh = z[lo], z[hi]
            if k <= zh - zl:
                lo, hi = zl, zh
            else:  # all of this window's 0s are among the k smallest
                k -= zh - zl
                res += zs[hi] - zs[lo]
                rank |= 1 << d
                lo, hi = z[-1] + lo - zl, z[-1] + hi - zh
        return res + k * self.srt[rank]  # the last k all equal the k-th smallest

    # sum of the a[i], i in [l, r], whose rank is < x
    def _sumBelow(self, l, r, x):
        if x <= 0:
            return 0
        if x >= self.m:
            return self._sumFirst(l, r, r - l + 1)
        lo, hi, res, d = l, r + 1, 0, self.bits
        for z, zs in zip(self.zeros, self.zsum):
            d -= 1
            zl, zh = z[lo], z[hi]
            if (x >> d) & 1:
                res += zs[hi] - zs[lo]
                lo, hi = z[-1] + lo - zl, z[-1] + hi - zh
            else:
                lo, hi = zl, zh
        return res
'''

# the persistent mex tree; {R} = the roots list's name, {n} = the array length's
PY_MEX_CORE = '''
    # persistent seg tree over the values 0..n+1: version p holds, per value, its last index before p (-1: none)
    def _buildMex(self):
        n = {n}
        self.ML, self.MR, self.MN = [0], [0], [-1]  # node 0 = the empty tree (every last index -1)
        self.{R} = root = [0] * (n + 1)
        for i, v in enumerate(self.arr):
            root[i + 1] = self._mexSet(root[i], v, i) if 0 <= v <= n + 1 else root[i]

    # O(logN) -- copy of node with value v's last index set to i
    def _mexSet(self, node, v, i):
        ML, MR, MN = self.ML, self.MR, self.MN
        path = []
        nl, nh = 0, {n} + 1
        while nl != nh:
            mid = (nl + nh) >> 1
            if v <= mid:
                path.append((node, True))
                node, nh = ML[node], mid
            else:
                path.append((node, False))
                node, nl = MR[node], mid + 1
        cur = len(MN)
        ML.append(0), MR.append(0), MN.append(i)
        for old, left in reversed(path):
            lc, rc = (cur, MR[old]) if left else (ML[old], cur)
            cur = len(MN)
            ML.append(lc), MR.append(rc), MN.append(min(MN[lc], MN[rc]))
        return cur

    # O(logN) -- smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    def _mexFrom(self, l, r, s):
        ML, MR, MN = self.ML, self.MR, self.MN
        stack = [(self.{R}[r + 1], 0, {n} + 1)]
        while stack:
            t, nl, nh = stack.pop()
            if nh < s or MN[t] >= l:  # nothing allowed here, or every value here is in a[l..r]
                continue
            if not t:  # no value here was ever seen
                return max(nl, s)
            if nl == nh:
                return nl
            mid = (nl + nh) >> 1
            stack.append((MR[t], mid + 1, nh))
            stack.append((ML[t], nl, mid))
        return {n} + 2  # (unreachable: the n + 2 values 0..n+1 can't all be in a[l..r])
'''


def py_dense(ops, sums, mex):
    slots = ["arr", "n", "srt", "m", "bits", "zeros"] + (["zsum"] if sums else []) + (["mexRoot", "ML", "MR", "MN"] if mex else [])
    init = '''    # O(N log N) -- arr: the initial array (a list), 0-indexed
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        self.srt = srt = sorted(set(arr))
        self.m = m = len(srt)
        self.bits = bits = max(1, (m - 1).bit_length())
        where = {v: k for k, v in enumerate(srt)}
        cur = [where[v] for v in arr]
        self.zeros = []
''' + ("        self.zsum = []\n" if sums else "") + '''        for d in range(bits - 1, -1, -1):
            self.zeros.append(list(accumulate((((v >> d) & 1) ^ 1 for v in cur), initial=0)))
''' + ("            self.zsum.append(list(accumulate((0 if (v >> d) & 1 else srt[v] for v in cur), initial=0)))\n" if sums else "") + \
        '''            cur = [v for v in cur if not (v >> d) & 1] + [v for v in cur if (v >> d) & 1]
''' + ("        self._buildMex()\n" if mex else "")
    body = "\n".join(PY_OPS[op] for op in ORDER if op in ops)
    return (PY_DOC + (PY_SUM_DOC if sums else "") + (PY_MEX_DOC if mex else "") +
            "from bisect import bisect_left, bisect_right\nfrom itertools import accumulate\n\n\nclass WaveletMatrix:\n"
            f"    __slots__ = ({', '.join(repr(s) for s in slots)})\n\n" + init + "\n" + body + PY_CORE +
            (PY_SUM_CORE if sums else "") + (PY_MEX_CORE.format(R="mexRoot", n="self.n") if mex else ""))


def py_mex_only():
    return ('''# Static array; rangeMex(l, r) = smallest integer >= 0 not in a[l..r] (0-indexed, inclusive), online.
''' + PY_MEX_DOC + '''

class PersistentMex:
    __slots__ = ("arr", "n", "root", "ML", "MR", "MN")

    # O(N log N) -- arr: the initial array (a list), 0-indexed
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        self._buildMex()

''' + PY_OPS["pointGet"] + "\n" + PY_OPS["rangeMex"] + PY_MEX_CORE.format(R="root", n="self.n"))


# order the methods are written in
ORDER = ["pointGet", "countOccurrences", "countInValRange", "countLtX", "countLteX", "countGtX", "countGteX", "kthSmallest",
         "kthLargest", "medianLow", "medianHigh", "rangeMin", "rangeMax", "smallestGteX", "smallestGtX", "largestLteX",
         "largestLtX", "rangeSum", "sumInValRange", "sumLtX", "sumLteX", "sumGtX", "sumGteX", "sumSmallestK", "sumLargestK",
         "sumKthSmallestRange", "sumKthLargestRange", "sumAbsDiffToX", "sumAbsDiffToMedian", "rangeMex"]


# ================================================================================================ C++, dense

CPP_DOC = '''// Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
// 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x,
// lowVal, ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the
// ranks with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0.
'''
CPP_SUM_DOC = '''// zsum[d][i] = sum of the values among the first i elements of level d's order whose bit is 0.
'''
CPP_MEX_DOC = '''// rangeMex: a persistent seg tree over the values 0..N+1; version p holds, per value, its last index before p (-1 if
// none). The mex of a[l..r] is the first value whose last index in version r + 1 is < l.
'''

E = "throw out_of_range"
CPP_OPS = {
    "pointGet": '''    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }
''',
    "countOccurrences": '''    // O(logN) -- # of i in [l, r] with a[i] == x
    int countOccurrences(int l, int r, T x) const { return countInValRange(l, r, x, x); }
''',
    "countInValRange": '''    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    int countInValRange(int l, int r, T lowVal, T highVal) const {
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }
''',
    "countLtX": '''    // O(logN) -- # of values < x in a[l..r]
    int countLtX(int l, int r, T x) const { return countBelow(l, r, lb(x)); }
''',
    "countLteX": '''    // O(logN) -- # of values <= x in a[l..r]
    int countLteX(int l, int r, T x) const { return countBelow(l, r, ub(x)); }
''',
    "countGtX": '''    // O(logN) -- # of values > x in a[l..r]
    int countGtX(int l, int r, T x) const { return r - l + 1 - countBelow(l, r, ub(x)); }
''',
    "countGteX": '''    // O(logN) -- # of values >= x in a[l..r]
    int countGteX(int l, int r, T x) const { return r - l + 1 - countBelow(l, r, lb(x)); }
''',
    "kthSmallest": f'''    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthSmallest(int l, int r, int k) const {{
        if (k < 1 || k > r - l + 1) {E}("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }}
''',
    "kthLargest": f'''    // O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthLargest(int l, int r, int k) const {{
        if (k < 1 || k > r - l + 1) {E}("kthLargest: needs 1 <= k <= r - l + 1");
        return kth(l, r, r - l + 2 - k);
    }}
''',
    "medianLow": '''    // O(logN) -- lower median of a[l..r]: its ceil(len / 2)-th smallest
    T medianLow(int l, int r) const { return kth(l, r, (r - l + 2) / 2); }
''',
    "medianHigh": '''    // O(logN) -- upper median of a[l..r]: its (floor(len / 2) + 1)-th smallest
    T medianHigh(int l, int r) const { return kth(l, r, (r - l + 1) / 2 + 1); }
''',
    "rangeMin": '''    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) const { return kth(l, r, 1); }
''',
    "rangeMax": '''    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) const { return kth(l, r, r - l + 1); }
''',
    "smallestGteX": '''    // O(logN) -- smallest value >= x in a[l..r], or nullopt
    optional<T> smallestGteX(int l, int r, T x) const {
        int c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }
''',
    "smallestGtX": '''    // O(logN) -- smallest value > x in a[l..r], or nullopt
    optional<T> smallestGtX(int l, int r, T x) const {
        int c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }
''',
    "largestLteX": '''    // O(logN) -- largest value <= x in a[l..r], or nullopt
    optional<T> largestLteX(int l, int r, T x) const {
        int c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }
''',
    "largestLtX": '''    // O(logN) -- largest value < x in a[l..r], or nullopt
    optional<T> largestLtX(int l, int r, T x) const {
        int c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }
''',
    "rangeSum": '''    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) const { return sumFirst(l, r, r - l + 1); }
''',
    "sumInValRange": '''    // O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    S sumInValRange(int l, int r, T lowVal, T highVal) const {
        if (highVal < lowVal) return 0;
        return sumBelow(l, r, ub(highVal)) - sumBelow(l, r, lb(lowVal));
    }
''',
    "sumLtX": '''    // O(logN) -- sum of the values < x in a[l..r]
    S sumLtX(int l, int r, T x) const { return sumBelow(l, r, lb(x)); }
''',
    "sumLteX": '''    // O(logN) -- sum of the values <= x in a[l..r]
    S sumLteX(int l, int r, T x) const { return sumBelow(l, r, ub(x)); }
''',
    "sumGtX": '''    // O(logN) -- sum of the values > x in a[l..r]
    S sumGtX(int l, int r, T x) const { return sumFirst(l, r, r - l + 1) - sumBelow(l, r, ub(x)); }
''',
    "sumGteX": '''    // O(logN) -- sum of the values >= x in a[l..r]
    S sumGteX(int l, int r, T x) const { return sumFirst(l, r, r - l + 1) - sumBelow(l, r, lb(x)); }
''',
    "sumSmallestK": f'''    // O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= k <= r - l + 1, else throws out_of_range
    S sumSmallestK(int l, int r, int k) const {{
        if (k < 0 || k > r - l + 1) {E}("sumSmallestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, k);
    }}
''',
    "sumLargestK": f'''    // O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else throws out_of_range
    S sumLargestK(int l, int r, int k) const {{
        int n = r - l + 1;
        if (k < 0 || k > n) {E}("sumLargestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, n) - sumFirst(l, r, n - k);
    }}
''',
    "sumKthSmallestRange": f'''    // O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 1 <= kFrom <= kTo <= r - l + 1,
    // else throws out_of_range
    S sumKthSmallestRange(int l, int r, int kFrom, int kTo) const {{
        if (kFrom < 1 || kFrom > kTo || kTo > r - l + 1) {E}("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, kTo) - sumFirst(l, r, kFrom - 1);
    }}
''',
    "sumKthLargestRange": f'''    // O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest); needs
    // 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    S sumKthLargestRange(int l, int r, int kFrom, int kTo) const {{
        int n = r - l + 1;
        if (kFrom < 1 || kFrom > kTo || kTo > n) {E}("sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, n - kFrom + 1) - sumFirst(l, r, n - kTo);
    }}
''',
    "sumAbsDiffToX": '''    // O(logN) -- sum of |a[i] - x| over i in [l, r]
    S sumAbsDiffToX(int l, int r, T x) const {
        int rk = lb(x), c = countBelow(l, r, rk);
        S s = sumBelow(l, r, rk);
        return S(x) * c - s + (sumFirst(l, r, r - l + 1) - s) - S(x) * (r - l + 1 - c);
    }
''',
    "sumAbsDiffToMedian": '''    // O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    S sumAbsDiffToMedian(int l, int r) const { return sumAbsDiffToX(l, r, kth(l, r, (r - l + 2) / 2)); }
''',
    "rangeMex": '''    // O(logN) -- smallest integer >= 0 that is not in a[l..r]
    int rangeMex(int l, int r) const { return mexFrom(l, r, 0); }
''',
}

CPP_CORE = '''
    // ---- internals ----

    int lb(const T& v) const { return int(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    int ub(const T& v) const { return int(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    const int* row(int lv) const { return &zeros[(size_t)lv * (n + 1)]; }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(int l, int r, int k) const {
        int lo = l, hi = r + 1, rank = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            int zl = z[lo], zh = z[hi];
            if (k <= zh - zl) lo = zl, hi = zh;  // enough 0s at this bit: the answer has it 0
            else k -= zh - zl, rank |= 1 << (bits - 1 - lv), lo = z[n] + lo - zl, hi = z[n] + hi - zh;
        }
        return srt[rank];
    }

    // # of i in [l, r] whose rank is < x
    int countBelow(int l, int r, int x) const {
        if (x <= 0) return 0;
        if (x >= m) return r - l + 1;
        int lo = l, hi = r + 1, res = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            int zl = z[lo], zh = z[hi];
            if ((x >> (bits - 1 - lv)) & 1) res += zh - zl, lo = z[n] + lo - zl, hi = z[n] + hi - zh;  // all 0s are below x
            else lo = zl, hi = zh;
        }
        return res;
    }
'''
CPP_SUM_CORE = '''
    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    S sumFirst(int l, int r, int k) const {
        if (k <= 0) return 0;
        int lo = l, hi = r + 1, rank = 0;
        S res = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            const S* zs = &zsum[(size_t)lv * (n + 1)];
            int zl = z[lo], zh = z[hi];
            if (k <= zh - zl) lo = zl, hi = zh;
            else k -= zh - zl, res += zs[hi] - zs[lo], rank |= 1 << (bits - 1 - lv), lo = z[n] + lo - zl, hi = z[n] + hi - zh;
        }
        return res + S(k) * srt[rank];  // the last k all equal the k-th smallest
    }

    // sum of the a[i], i in [l, r], whose rank is < x
    S sumBelow(int l, int r, int x) const {
        if (x <= 0) return 0;
        if (x >= m) return sumFirst(l, r, r - l + 1);
        int lo = l, hi = r + 1;
        S res = 0;
        for (int lv = 0; lv < bits; lv++) {
            const int* z = row(lv);
            const S* zs = &zsum[(size_t)lv * (n + 1)];
            int zl = z[lo], zh = z[hi];
            if ((x >> (bits - 1 - lv)) & 1) res += zs[hi] - zs[lo], lo = z[n] + lo - zl, hi = z[n] + hi - zh;
            else lo = zl, hi = zh;
        }
        return res;
    }
'''
CPP_MEX_CORE = '''
    // persistent seg tree over the values 0..n+1: version p holds, per value, its last index before p (-1: none)
    void buildMex() {
        ML.assign(1, 0), MR.assign(1, 0), MN.assign(1, -1);  // node 0 = the empty tree (every last index -1)
        {R}.assign(n + 1, 0);
        for (int i = 0; i < n; i++)
            {R}[i + 1] = T(0) <= arr[i] && arr[i] <= T(n + 1) ? mexSet({R}[i], 0, n + 1, int(arr[i]), i) : {R}[i];
    }

    // copy of node with value v's last index set to i
    int mexSet(int node, int nl, int nh, int v, int i) {
        int l = ML[node], r = MR[node], x;
        if (nl == nh) x = i;
        else {
            int mid = (nl + nh) >> 1;
            if (v <= mid) l = mexSet(l, nl, mid, v, i);
            else r = mexSet(r, mid + 1, nh, v, i);
            x = min(MN[l], MN[r]);
        }
        ML.push_back(nl == nh ? 0 : l), MR.push_back(nl == nh ? 0 : r), MN.push_back(x);
        return (int)MN.size() - 1;
    }

    // smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    int mexFrom(int l, int r, int s) const {
        auto go = [&](auto&& self, int t, int nl, int nh) -> int {
            if (nh < s || MN[t] >= l) return -1;  // nothing allowed here, or every value here is in a[l..r]
            if (!t) return max(nl, s);            // no value here was ever seen
            if (nl == nh) return nl;
            int mid = (nl + nh) >> 1, res = self(self, ML[t], nl, mid);
            return res >= 0 ? res : self(self, MR[t], mid + 1, nh);
        };
        return go(go, {R}[r + 1], 0, n + 1);
    }
'''


def cpp_dense(ops, sums, mex):
    fields = ["    int n, m, bits;", "    vector<T> arr, srt;  // srt: sorted distinct values",
              "    vector<int> zeros;   // level lv's row is zeros[lv * (n + 1) .. lv * (n + 1) + n]"]
    if sums:
        fields.append("    vector<S> zsum;      // same layout as zeros")
    if mex:
        fields.append("    vector<int> mexRoot, ML, MR, MN;  // the persistent mex tree")
    ctor = '''    // O(N log N) -- arr: the initial array, 0-indexed
    explicit WaveletMatrix(const vector<T>& a) : n((int)a.size()), arr(a), srt(a) {
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        bits = 1;
        while ((1 << bits) < m) bits++;
        zeros.assign((size_t)bits * (n + 1), 0);
''' + ("        zsum.assign((size_t)bits * (n + 1), S(0));\n" if sums else "") + '''        vector<int> cur(n), nxt(n);
        for (int i = 0; i < n; i++) cur[i] = lb(a[i]);
        for (int lv = 0; lv < bits; lv++) {
            int d = bits - 1 - lv, k = 0, *z = &zeros[(size_t)lv * (n + 1)];
''' + ("            S* zs = &zsum[(size_t)lv * (n + 1)];\n" if sums else "") + '''            for (int i = 0; i < n; i++) {
                bool one = (cur[i] >> d) & 1;
                z[i + 1] = z[i] + !one;
''' + ("                zs[i + 1] = zs[i] + (one ? S(0) : S(srt[cur[i]]));\n" if sums else "") + '''            }
            for (int v : cur) if (!((v >> d) & 1)) nxt[k++] = v;
            for (int v : cur) if ((v >> d) & 1) nxt[k++] = v;
            swap(cur, nxt);
        }
''' + ("        buildMex();\n" if mex else "") + "    }\n"
    body = "\n".join(CPP_OPS[op] for op in ORDER if op in ops)
    return (CPP_DOC + (CPP_SUM_DOC if sums else "") + (CPP_MEX_DOC if mex else "") +
            "// T: int, long long, ..." + ("; sums are kept in S (long long for small T)" if sums else "") +
            ".\ntemplate <typename T>\nstruct WaveletMatrix {\n" +
            ("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n" if sums else "") +
            "\n".join(fields) + "\n\n" + ctor + "\n" + body + CPP_CORE + (CPP_SUM_CORE if sums else "") +
            (CPP_MEX_CORE.replace("{R}", "mexRoot") if mex else "") + "};\n")


def cpp_mex_only():
    return ('''// Static array; rangeMex(l, r) = smallest integer >= 0 not in a[l..r] (0-indexed, inclusive), online.
''' + CPP_MEX_DOC + '''// T: int, long long, ...
template <typename T>
struct PersistentMex {
    int n;
    vector<T> arr;
    vector<int> root, ML, MR, MN;

    // O(N log N) -- arr: the initial array, 0-indexed
    explicit PersistentMex(const vector<T>& a) : n((int)a.size()), arr(a) { buildMex(); }

''' + CPP_OPS["pointGet"] + "\n" + CPP_OPS["rangeMex"] + CPP_MEX_CORE.replace("{R}", "root") + "};\n")


# ================================================================================================ sparse wrappers

SPARSE_DOC = ('''{c} ======================================================================================== sparse wrapper

{c} The same queries over any index range [lo, hi], built from given values (index, value pairs); every other index is 0.
{c} The structure above runs on the given values alone (in index order). [l, r] covers given values i0..i1 and
{c} zeros = (r - l + 1) - (i1 - i0 + 1) zeros, and in sorted order those zeros sit right after the given negatives, so the
{c} k-th smallest of [l, r] is the given k-th while k <= neg, 0 while k <= neg + zeros, then the given (k - zeros)-th.
''')

PY_SPARSE_HEAD = '''
from bisect import bisect_left, bisect_right


class {name}:
    __slots__ = ("lo", "hi", "idx", "vals", "inner")

    # O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    def __init__(self, lo, hi, values):
        self.lo, self.hi = lo, hi
        pts = sorted(values)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        self.inner = {inner}(self.vals or [0])  # (a dummy element when there are no given values; it is never queried)

    # (i0, i1, zeros): the given values inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    def _span(self, l, r):
        i0, i1 = bisect_left(self.idx, l), bisect_right(self.idx, r) - 1
        return i0, i1, (r - l + 1) - (i1 - i0 + 1)

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
'''


def _py_cnt(op, test, doc):
    return f'''    # O(logN) -- {doc}
    def {op}(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return (self.inner.{op}(i0, i1, x) if i0 <= i1 else 0) + (zeros if {test} else 0)
'''


def _py_pred(op, test, pick, doc):
    return f'''    # O(logN) -- {doc}, or None
    def {op}(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        a = self.inner.{op}(i0, i1, x) if i0 <= i1 else None
        if zeros and {test}:
            a = 0 if a is None else {pick}(a, 0)
        return a
'''


def _py_sum(op, args, doc):
    return f'''    # O(logN) -- {doc} (the zeros add nothing)
    def {op}(self, l, r, {args}):
        i0, i1, _ = self._span(l, r)
        return self.inner.{op}(i0, i1, {args}) if i0 <= i1 else 0
'''


PY_SPARSE_OPS = {
    "countOccurrences": _py_cnt("countOccurrences", "x == 0", "# of i in [l, r] with a[i] == x"),
    "countInValRange": '''    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    def countInValRange(self, l, r, lowVal, highVal):
        i0, i1, zeros = self._span(l, r)
        inside = self.inner.countInValRange(i0, i1, lowVal, highVal) if i0 <= i1 else 0
        return inside + (zeros if lowVal <= 0 <= highVal else 0)
''',
    "countLtX": _py_cnt("countLtX", "0 < x", "# of values < x in a[l..r]"),
    "countLteX": _py_cnt("countLteX", "0 <= x", "# of values <= x in a[l..r]"),
    "countGtX": _py_cnt("countGtX", "0 > x", "# of values > x in a[l..r]"),
    "countGteX": _py_cnt("countGteX", "0 >= x", "# of values >= x in a[l..r]"),
    "kthSmallest": '''    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else IndexError
    def kthSmallest(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)
''',
    "kthLargest": '''    # O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else IndexError
    def kthLargest(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthLargest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, r - l + 2 - k)
''',
    "medianLow": '''    # O(logN) -- lower median of a[l..r]: its ceil(len / 2)-th smallest
    def medianLow(self, l, r):
        return self._kth(l, r, (r - l + 2) // 2)
''',
    "medianHigh": '''    # O(logN) -- upper median of a[l..r]: its (floor(len / 2) + 1)-th smallest
    def medianHigh(self, l, r):
        return self._kth(l, r, (r - l + 1) // 2 + 1)
''',
    "rangeMin": '''    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        return self._kth(l, r, 1)
''',
    "rangeMax": '''    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        return self._kth(l, r, r - l + 1)
''',
    "smallestGteX": _py_pred("smallestGteX", "0 >= x", "min", "smallest value >= x in a[l..r]"),
    "smallestGtX": _py_pred("smallestGtX", "0 > x", "min", "smallest value > x in a[l..r]"),
    "largestLteX": _py_pred("largestLteX", "0 <= x", "max", "largest value <= x in a[l..r]"),
    "largestLtX": _py_pred("largestLtX", "0 < x", "max", "largest value < x in a[l..r]"),
    "rangeSum": '''    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        i0, i1, _ = self._span(l, r)
        return self.inner.rangeSum(i0, i1) if i0 <= i1 else 0
''',
    "sumInValRange": _py_sum("sumInValRange", "lowVal, highVal", "sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal"),
    "sumLtX": _py_sum("sumLtX", "x", "sum of the values < x in a[l..r]"),
    "sumLteX": _py_sum("sumLteX", "x", "sum of the values <= x in a[l..r]"),
    "sumGtX": _py_sum("sumGtX", "x", "sum of the values > x in a[l..r]"),
    "sumGteX": _py_sum("sumGteX", "x", "sum of the values >= x in a[l..r]"),
    "sumSmallestK": '''    # O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= k <= r - l + 1, else IndexError
    def sumSmallestK(self, l, r, k):
        if not 0 <= k <= r - l + 1:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, k)
''',
    "sumLargestK": '''    # O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else IndexError
    def sumLargestK(self, l, r, k):
        n = r - l + 1
        if not 0 <= k <= n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n) - self._sumFirst(l, r, n - k)
''',
    "sumKthSmallestRange": '''    # O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 1 <= kFrom <= kTo <= r - l + 1,
    # else IndexError
    def sumKthSmallestRange(self, l, r, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= r - l + 1:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, kTo) - self._sumFirst(l, r, kFrom - 1)
''',
    "sumKthLargestRange": '''    # O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest); needs
    # 1 <= kFrom <= kTo <= r - l + 1, else IndexError
    def sumKthLargestRange(self, l, r, kFrom, kTo):
        n = r - l + 1
        if not 1 <= kFrom <= kTo <= n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n - kFrom + 1) - self._sumFirst(l, r, n - kTo)
''',
    "sumAbsDiffToX": '''    # O(logN) -- sum of |a[i] - x| over i in [l, r]
    def sumAbsDiffToX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return (self.inner.sumAbsDiffToX(i0, i1, x) if i0 <= i1 else 0) + zeros * abs(x)
''',
    "sumAbsDiffToMedian": '''    # O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    def sumAbsDiffToMedian(self, l, r):
        return self.sumAbsDiffToX(l, r, self._kth(l, r, (r - l + 2) // 2))
''',
    "rangeMex": '''    # O(logN) -- smallest integer >= 0 that is not in a[l..r]
    def rangeMex(self, l, r):
        i0, i1, zeros = self._span(l, r)
        if i0 > i1:
            return 1  # all zeros
        return self.inner._mexFrom(i0, i1, 1) if zeros else self.inner.rangeMex(i0, i1)
''',
}

PY_SPARSE_KTH = '''
    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        i0, i1, zeros = self._span(l, r)
        neg = self.inner.countLtX(i0, i1, 0) if i0 <= i1 else 0
        if k <= neg:
            return self.inner.kthSmallest(i0, i1, k)
        if k <= neg + zeros:
            return 0
        return self.inner.kthSmallest(i0, i1, k - zeros)
'''
PY_SPARSE_SUM = '''
    # how many of the k smallest of [l, r] are given values (the rest are zeros), with i0, i1 from _span
    def _given(self, i0, i1, zeros, k):
        neg = self.inner.countLtX(i0, i1, 0) if i0 <= i1 else 0
        return k if k <= neg else max(neg, k - zeros)
    # sum of the k smallest of a[l..r], 0 <= k <= r - l + 1 (zeros add nothing)
    def _sumFirst(self, l, r, k):
        i0, i1, zeros = self._span(l, r)
        return self.inner.sumSmallestK(i0, i1, self._given(i0, i1, zeros, k)) if i0 <= i1 else 0
'''

E2 = "throw out_of_range"


def _cpp_cnt(op, test, doc):
    return f'''    // O(logN) -- {doc}
    long long {op}(long long l, long long r, T x) const {{
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.{op}(i0, i1, x) : 0) + ({test} ? zeros : 0);
    }}
'''


def _cpp_pred(op, test, pick, doc):
    return f'''    // O(logN) -- {doc}, or nullopt
    optional<T> {op}(long long l, long long r, T x) const {{
        auto [i0, i1, zeros] = span(l, r);
        optional<T> a = i0 <= i1 ? inner.{op}(i0, i1, x) : nullopt;
        if (zeros && {test}) a = a ? {pick}(*a, T(0)) : T(0);
        return a;
    }}
'''


def _cpp_sum(op, params, args, doc):
    return f'''    // O(logN) -- {doc} (the zeros add nothing)
    S {op}(long long l, long long r, {params}) const {{
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.{op}(i0, i1, {args})) : S(0);
    }}
'''


CPP_SPARSE_OPS = {
    "countOccurrences": _cpp_cnt("countOccurrences", "x == T(0)", "# of i in [l, r] with a[i] == x"),
    "countInValRange": '''    // O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    long long countInValRange(long long l, long long r, T lowVal, T highVal) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? inner.countInValRange(i0, i1, lowVal, highVal) : 0) + (lowVal <= T(0) && T(0) <= highVal ? zeros : 0);
    }
''',
    "countLtX": _cpp_cnt("countLtX", "T(0) < x", "# of values < x in a[l..r]"),
    "countLteX": _cpp_cnt("countLteX", "T(0) <= x", "# of values <= x in a[l..r]"),
    "countGtX": _cpp_cnt("countGtX", "x < T(0)", "# of values > x in a[l..r]"),
    "countGteX": _cpp_cnt("countGteX", "x <= T(0)", "# of values >= x in a[l..r]"),
    "kthSmallest": f'''    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthSmallest(long long l, long long r, long long k) const {{
        if (k < 1 || k > r - l + 1) {E2}("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }}
''',
    "kthLargest": f'''    // O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthLargest(long long l, long long r, long long k) const {{
        if (k < 1 || k > r - l + 1) {E2}("kthLargest: needs 1 <= k <= r - l + 1");
        return kth(l, r, r - l + 2 - k);
    }}
''',
    "medianLow": '''    // O(logN) -- lower median of a[l..r]: its ceil(len / 2)-th smallest
    T medianLow(long long l, long long r) const { return kth(l, r, (r - l + 2) / 2); }
''',
    "medianHigh": '''    // O(logN) -- upper median of a[l..r]: its (floor(len / 2) + 1)-th smallest
    T medianHigh(long long l, long long r) const { return kth(l, r, (r - l + 1) / 2 + 1); }
''',
    "rangeMin": '''    // O(logN) -- min of a[l..r]
    T rangeMin(long long l, long long r) const { return kth(l, r, 1); }
''',
    "rangeMax": '''    // O(logN) -- max of a[l..r]
    T rangeMax(long long l, long long r) const { return kth(l, r, r - l + 1); }
''',
    "smallestGteX": _cpp_pred("smallestGteX", "x <= T(0)", "min", "smallest value >= x in a[l..r]"),
    "smallestGtX": _cpp_pred("smallestGtX", "x < T(0)", "min", "smallest value > x in a[l..r]"),
    "largestLteX": _cpp_pred("largestLteX", "T(0) <= x", "max", "largest value <= x in a[l..r]"),
    "largestLtX": _cpp_pred("largestLtX", "T(0) < x", "max", "largest value < x in a[l..r]"),
    "rangeSum": '''    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.rangeSum(i0, i1)) : S(0);
    }
''',
    "sumInValRange": _cpp_sum("sumInValRange", "T lowVal, T highVal", "lowVal, highVal", "sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal"),
    "sumLtX": _cpp_sum("sumLtX", "T x", "x", "sum of the values < x in a[l..r]"),
    "sumLteX": _cpp_sum("sumLteX", "T x", "x", "sum of the values <= x in a[l..r]"),
    "sumGtX": _cpp_sum("sumGtX", "T x", "x", "sum of the values > x in a[l..r]"),
    "sumGteX": _cpp_sum("sumGteX", "T x", "x", "sum of the values >= x in a[l..r]"),
    "sumSmallestK": f'''    // O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= k <= r - l + 1, else throws out_of_range
    S sumSmallestK(long long l, long long r, long long k) const {{
        if (k < 0 || k > r - l + 1) {E2}("sumSmallestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, k);
    }}
''',
    "sumLargestK": f'''    // O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else throws out_of_range
    S sumLargestK(long long l, long long r, long long k) const {{
        long long n = r - l + 1;
        if (k < 0 || k > n) {E2}("sumLargestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, n) - sumFirst(l, r, n - k);
    }}
''',
    "sumKthSmallestRange": f'''    // O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 1 <= kFrom <= kTo <= r - l + 1,
    // else throws out_of_range
    S sumKthSmallestRange(long long l, long long r, long long kFrom, long long kTo) const {{
        if (kFrom < 1 || kFrom > kTo || kTo > r - l + 1) {E2}("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, kTo) - sumFirst(l, r, kFrom - 1);
    }}
''',
    "sumKthLargestRange": f'''    // O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest); needs
    // 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    S sumKthLargestRange(long long l, long long r, long long kFrom, long long kTo) const {{
        long long n = r - l + 1;
        if (kFrom < 1 || kFrom > kTo || kTo > n) {E2}("sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, n - kFrom + 1) - sumFirst(l, r, n - kTo);
    }}
''',
    "sumAbsDiffToX": '''    // O(logN) -- sum of |a[i] - x| over i in [l, r]
    S sumAbsDiffToX(long long l, long long r, T x) const {
        auto [i0, i1, zeros] = span(l, r);
        return (i0 <= i1 ? S(inner.sumAbsDiffToX(i0, i1, x)) : S(0)) + S(zeros) * S(x < T(0) ? -x : x);
    }
''',
    "sumAbsDiffToMedian": '''    // O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    S sumAbsDiffToMedian(long long l, long long r) const { return sumAbsDiffToX(l, r, kth(l, r, (r - l + 2) / 2)); }
''',
    "rangeMex": '''    // O(logN) -- smallest integer >= 0 that is not in a[l..r]
    long long rangeMex(long long l, long long r) const {
        auto [i0, i1, zeros] = span(l, r);
        if (i0 > i1) return 1;  // all zeros
        return zeros ? inner.mexFrom(i0, i1, 1) : inner.rangeMex(i0, i1);
    }
''',
}

CPP_SPARSE_HEAD = '''template <typename T>
struct {name} {{
{using}    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    {inner}<T> inner;

    // O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    {name}(long long lo, long long hi, vector<pair<long long, T>> values) : lo(lo), hi(hi), inner(split(values)) {{}}

    vector<T> split(vector<pair<long long, T>>& pts) {{
        sort(pts.begin(), pts.end());
        for (auto& [i, v] : pts) idx.push_back(i), vals.push_back(v);
        return vals.empty() ? vector<T>{{T(0)}} : vals;  // (a dummy element when there are no given values; never queried)
    }}

    // {{i0, i1, zeros}}: the given values inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    tuple<int, int, long long> span(long long l, long long r) const {{
        int i0 = int(lower_bound(idx.begin(), idx.end(), l) - idx.begin());
        int i1 = int(upper_bound(idx.begin(), idx.end(), r) - idx.begin()) - 1;
        return {{i0, i1, (r - l + 1) - (i1 - i0 + 1)}};
    }}

    // O(logN) -- a[i]
    T pointGet(long long i) const {{
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }}
'''
CPP_SPARSE_KTH = '''
    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(long long l, long long r, long long k) const {
        auto [i0, i1, zeros] = span(l, r);
        long long neg = i0 <= i1 ? inner.countLtX(i0, i1, T(0)) : 0;
        if (k <= neg) return inner.kthSmallest(i0, i1, int(k));
        if (k <= neg + zeros) return T(0);
        return inner.kthSmallest(i0, i1, int(k - zeros));
    }
'''
CPP_SPARSE_SUM = '''
    // how many of the k smallest of [l, r] are given values (the rest are zeros), with i0, i1 from span
    long long given(int i0, int i1, long long zeros, long long k) const {
        long long neg = i0 <= i1 ? inner.countLtX(i0, i1, T(0)) : 0;
        return k <= neg ? k : max(neg, k - zeros);
    }
    // sum of the k smallest of a[l..r], 0 <= k <= r - l + 1 (zeros add nothing)
    S sumFirst(long long l, long long r, long long k) const {
        auto [i0, i1, zeros] = span(l, r);
        return i0 <= i1 ? S(inner.sumSmallestK(i0, i1, int(given(i0, i1, zeros, k)))) : S(0);
    }
'''


def py_sparse(ops, sums, mex_only, names=None):
    name, inner = names or (("SparsePersistentMex", "PersistentMex") if mex_only else ("SparseWaveletMatrix", "WaveletMatrix"))
    body = "\n".join(PY_SPARSE_OPS[op] for op in ORDER if op in ops and op != "pointGet")
    return ("\n" + SPARSE_DOC.format(c="#") + PY_SPARSE_HEAD.format(name=name, inner=inner) + "\n" + body +
            ("" if mex_only else PY_SPARSE_KTH) + (PY_SPARSE_SUM if sums else ""))


def cpp_sparse(ops, sums, mex_only, names=None):
    name, inner = names or (("SparsePersistentMex", "PersistentMex") if mex_only else ("SparseWaveletMatrix", "WaveletMatrix"))
    using = "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n" if sums else ""
    body = "\n".join(CPP_SPARSE_OPS[op] for op in ORDER if op in ops and op != "pointGet")
    return ("\n" + SPARSE_DOC.format(c="//") + CPP_SPARSE_HEAD.format(name=name, inner=inner, using=using) + "\n" + body +
            ("" if mex_only else CPP_SPARSE_KTH) + (CPP_SPARSE_SUM if sums else "") + "};\n")


# ================================================================================================ write

def write(folder, ops, dtype, sums, mex, py, cpp, spy, scpp):
    path = os.path.join(DIR, folder)
    os.makedirs(path, exist_ok=True)
    for sparse, files in ((False, (py, cpp)), (True, (py + spy, cpp + scpp))):
        node, other = memory(sums, mex, sparse)
        nt = note(sums, mex, sparse)
        stem = "sparse" if sparse else "template"
        write_template(os.path.join(path, f"{stem}.py"), header("#", ops, dtype, sparse, node, other, nt) + "\n" + files[0])
        write_template(os.path.join(path, f"{stem}.cpp"), header("//", ops, dtype, sparse, node, other, nt) + "\n" + files[1])
    print("wrote", folder)


def main():
    for sums in (False, True):
        for mex in (False, True):
            ops = sorted(BASE + (SUMS if sums else []) + (MEX if mex else []))
            folder = "wavelet-order-stats" + ("-sums" if sums else "") + ("-mex" if mex else "")
            write(folder, ops, "wavelet", sums, mex, py_dense(ops, sums, mex), cpp_dense(ops, sums, mex),
                  py_sparse(ops, sums, False), cpp_sparse(ops, sums, False))
    ops = ["pointGet", "rangeMex"]
    write("pointGet-rangeMex", ops, "persistent", None, True, py_mex_only(), cpp_mex_only(), py_sparse(ops, False, True),
          cpp_sparse(ops, False, True))


if __name__ == "__main__":
    main()
