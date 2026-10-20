# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-pointGet/sparse.py
# @operations: countOccurrences pointGet
# @data-structure-type: positions
# @complexities:
#   countOccurrences: log(N)
#   pointGet: log(N)
#   build: N*log(N)
# @memory:
#   layout: sparse
#   node: pos[1*N]
#   tags: none
#   other: idx[1*N] vals[1*N]
#   note: built from N (index, value) points over any index range [lo, hi], every other index 0; pos maps each value to its sorted indices; 0 also counts the zeros of [l, r] (its length minus the points inside)
from bisect import bisect_left, bisect_right

# "How many times does x appear in a[l..r]?" over any index range [lo, hi], built from (index, value) points; every
# other index is 0. Each value keeps its sorted indices; x == 0 also counts the zeros of [l, r] (its length minus the
# points inside).


class SparseStaticOccurrences:
    __slots__ = ("lo", "hi", "idx", "vals", "pos")

    # O(N log N) -- [lo, hi] all 0 except the given (index, value) points (distinct indices)
    def __init__(self, lo, hi, points):
        self.lo, self.hi = lo, hi
        pts = sorted(points)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        pos = self.pos = {}
        for i, v in pts:
            if v in pos:
                pos[v].append(i)
            else:
                pos[v] = [i]

    # O(logN) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        if l > r:
            return 0
        p = self.pos.get(x)
        res = bisect_right(p, r) - bisect_left(p, l) if p else 0
        if x == 0:
            res += (r - l + 1) - (bisect_right(self.idx, r) - bisect_left(self.idx, l))
        return res

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
