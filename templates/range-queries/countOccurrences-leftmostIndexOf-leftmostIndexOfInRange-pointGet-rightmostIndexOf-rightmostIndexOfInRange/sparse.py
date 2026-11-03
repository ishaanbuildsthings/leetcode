# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointGet-rightmostIndexOf-rightmostIndexOfInRange/sparse.py
# @operations: countOccurrences leftmostIndexOf leftmostIndexOfInRange pointGet rightmostIndexOf rightmostIndexOfInRange
# @data-structure-type: positions
# @complexities:
#   countOccurrences: log(N)
#   leftmostIndexOf: log(N)
#   leftmostIndexOfInRange: log(N)
#   pointGet: log(N)
#   rightmostIndexOf: log(N)
#   rightmostIndexOfInRange: log(N)
#   build: N*log(N)
# @memory:
#   layout: sparse
#   node: pos[1*N]
#   tags: none
#   other: idx[1*N] vals[1*N]
#   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; pos maps each value to its sorted indices; 0 also counts the zeros of [l, r] (its length minus the given values inside)
from bisect import bisect_left, bisect_right

# "How many times does x appear in a[l..r]?" and "where is x's first / last copy (in a[l..r])?" over any index range
# [lo, hi], built from given values (index, value pairs); every other index is 0. Each value keeps its sorted indices;
# x == 0 also counts the zeros of [l, r] (its length minus the given values inside), and its first / last copy may be
# an index nobody gave: the end of a run of consecutive given indices, found by a binary search on idx[k] - k.


class SparseStaticOccurrences:
    __slots__ = ("lo", "hi", "idx", "vals", "pos")

    # O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    def __init__(self, lo, hi, values):
        self.lo, self.hi = lo, hi
        pts = sorted(values)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        pos = self.pos = {}
        for i, v in pts:
            if v in pos:
                pos[v].append(i)
            else:
                pos[v] = [i]

    # O(logN) -- # of i in [l, r] with a[i] == x; needs lo <= l <= r <= hi, else IndexError
    def countOccurrences(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countOccurrences: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if l > r:
            return 0
        p = self.pos.get(x)
        res = bisect_right(p, r) - bisect_left(p, l) if p else 0
        if x == 0:
            res += (r - l + 1) - (bisect_right(self.idx, r) - bisect_left(self.idx, l))
        return res

    # O(logN) -- the smallest i in [lo, hi] with a[i] == x, or lo - 1 if there is none
    def leftmostIndexOf(self, x):
        return self.leftmostIndexOfInRange(self.lo, self.hi, x)

    # O(logN) -- the largest i in [lo, hi] with a[i] == x, or lo - 1 if there is none
    def rightmostIndexOf(self, x):
        return self.rightmostIndexOfInRange(self.lo, self.hi, x)

    # O(logN) -- the smallest i in [l, r] with a[i] == x, or lo - 1 if there is none; needs lo <= l <= r <= hi, else
    # IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"leftmostIndexOfInRange: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        best = r + 1
        p = self.pos.get(x)
        if p:
            k = bisect_left(p, l)
            if k < len(p):
                best = p[k]
        if x == 0:
            best = min(best, self._firstGap(l))
        return best if best <= r else self.lo - 1

    # O(logN) -- the largest i in [l, r] with a[i] == x, or lo - 1 if there is none; needs lo <= l <= r <= hi, else
    # IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rightmostIndexOfInRange: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        best = l - 1
        p = self.pos.get(x)
        if p:
            k = bisect_right(p, r) - 1
            if k >= 0:
                best = p[k]
        if x == 0:
            best = max(best, self._lastGap(r))
        return best if best >= l else self.lo - 1

    def _firstGap(self, i):  # the smallest index >= i that wasn't given (it holds 0)
        idx = self.idx
        k = bisect_left(idx, i)
        if k == len(idx) or idx[k] != i:
            return i
        a, b = k, len(idx) - 1  # idx[k..a] = i, i + 1, ...: the largest such a (idx[j] - j stays i - k along it)
        while a < b:
            m = (a + b + 1) // 2
            if idx[m] - m == i - k:
                a = m
            else:
                b = m - 1
        return i + (a - k) + 1

    def _lastGap(self, i):  # the largest index <= i that wasn't given (it holds 0)
        idx = self.idx
        k = bisect_right(idx, i) - 1
        if k < 0 or idx[k] != i:
            return i
        a, b = 0, k  # idx[a..k] = ..., i - 1, i: the smallest such a
        while a < b:
            m = (a + b) // 2
            if idx[m] - m == i - k:
                b = m
            else:
                a = m + 1
        return i - (k - a) - 1

    # O(logN) -- a[i]; needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointGet: needs lo <= i <= hi, got i = {i}")
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
