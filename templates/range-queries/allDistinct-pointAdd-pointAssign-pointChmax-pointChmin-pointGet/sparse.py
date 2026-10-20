# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/allDistinct-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/sparse.py
# @operations: allDistinct pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: seg-tree
# @complexities:
#   allDistinct: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mn[3*log(U)] cnt[3*log(U)]
#   tags: none
#   other: children[6*log(U)] chains[1] vals[1]
#   note: per point write, at most 3 root paths (i, its old and new predecessor); each node keeps the min nxt and the number of nonzero positions below it; chains maps each nonzero value to its sorted positions (a bucketed SortedList defined at the top of the file). Dicts keyed by heap index

from bisect import bisect_left, bisect_right, insort


# SortedList: a self-contained sorted container (no sortedcontainers import needed), used by the class below.
class SortedList:
    """Sorted list of ints kept in buckets of LOAD..2*LOAD. An add / remove is a binary search over the bucket maxima,
    one inside a bucket, and a C-level shift of at most 2*LOAD elements; pred / succ are two binary searches. A Fenwick
    tree over bucket sizes answers countLess in O(log N); a bucket split or an emptied bucket marks it stale and the
    next countLess rebuilds it in O(#buckets) (at most once per LOAD adds)."""
    LOAD = 512
    __slots__ = ("lists", "maxes", "fen", "size")

    # values must already be sorted
    def __init__(self, values=()):
        vals = list(values)
        L = self.LOAD
        self.lists = [vals[i:i + L] for i in range(0, len(vals), L)]
        self.maxes = [b[-1] for b in self.lists]
        self.fen = None
        self.size = len(vals)

    def __len__(self):
        return self.size

    def _fenAdd(self, k, d):
        fen = self.fen
        if fen is not None:
            while k < len(fen):
                fen[k] += d
                k |= k + 1

    def add(self, x):
        self.size += 1
        lists, maxes = self.lists, self.maxes
        if not lists:
            lists.append([x])
            maxes.append(x)
            self.fen = None
            return
        k = bisect_left(maxes, x)
        if k == len(lists):
            k -= 1
        b = lists[k]
        insort(b, x)
        maxes[k] = b[-1]
        if len(b) > 2 * self.LOAD:
            L = self.LOAD
            lists[k:k + 1] = [b[:L], b[L:]]
            maxes[k:k + 1] = [b[L - 1], b[-1]]
            self.fen = None
        else:
            self._fenAdd(k, 1)

    # x must be present
    def remove(self, x):
        lists, maxes = self.lists, self.maxes
        k = bisect_left(maxes, x)
        b = lists[k]
        del b[bisect_left(b, x)]
        self.size -= 1
        if b:
            maxes[k] = b[-1]
            self._fenAdd(k, -1)
        else:
            del lists[k], maxes[k]
            self.fen = None

    # largest element < x, or None
    def pred(self, x):
        k = bisect_left(self.maxes, x)
        if k < len(self.lists):
            b = self.lists[k]
            i = bisect_left(b, x)
            if i:
                return b[i - 1]
        return self.maxes[k - 1] if k else None

    # smallest element > x, or None
    def succ(self, x):
        k = bisect_right(self.maxes, x)
        if k == len(self.lists):
            return None
        b = self.lists[k]
        return b[bisect_right(b, x)]

    # number of elements < x
    def countLess(self, x):
        k = bisect_left(self.maxes, x)
        if k == len(self.lists):
            return self.size
        fen = self.fen
        if fen is None:
            fen = self.fen = [len(b) for b in self.lists]
            for i in range(len(fen)):
                j = i | (i + 1)
                if j < len(fen):
                    fen[j] += fen[i]
        s, i = 0, k
        while i > 0:
            s += fen[i - 1]
            i &= i - 1
        return s + bisect_left(self.lists[k], x)

# "Are all values in a[l..r] distinct?" with point updates, over any index range [lo, hi] (huge or negative is fine);
# every position starts at 0. Two zeros repeat, so a range with >= 2 positions holding 0 is not distinct. Among the
# nonzero positions, nxt[i] = the next position with the same value (none: INF), and they are distinct iff
# min(nxt[l..r]) > r. Sparse: dicts keyed by heap index over a power-of-two cover of [lo, hi] keep, per node, the
# min nxt (missing: INF) and the number of nonzero positions (missing: 0).

INF = float("inf")


class SparseDistinctTree:
    __slots__ = ("lo", "hi", "size", "mn", "cnt", "vals", "chains")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of i is size + (i - lo)
        self.mn = {}
        self.cnt = {}
        self.vals = {}  # i -> a[i], nonzero values only
        self.chains = {}  # nonzero value -> SortedList of its positions

    # O(logU) -- position i now has nxt[i] = v and is nonzero (c = 1) or zero (c = 0, v = INF)
    def _set(self, i, v, c):
        mn, cnt = self.mn, self.cnt
        p = self.size + i - self.lo
        mn[p], cnt[p] = v, c
        p >>= 1
        while p:
            a, b = mn.get(2 * p, INF), mn.get(2 * p + 1, INF)
            mn[p] = a if a < b else b
            cnt[p] = cnt.get(2 * p, 0) + cnt.get(2 * p + 1, 0)
            p >>= 1

    # O(logU) -- True iff no value repeats inside a[l..r]
    def allDistinct(self, l, r):
        mn, cnt = self.mn, self.cnt
        lo_, hi_ = l + self.size - self.lo, r + self.size - self.lo + 1
        best, c = INF, 0
        while lo_ < hi_:
            if lo_ & 1:
                best = min(best, mn.get(lo_, INF))
                c += cnt.get(lo_, 0)
                lo_ += 1
            if hi_ & 1:
                hi_ -= 1
                best = min(best, mn.get(hi_, INF))
                c += cnt.get(hi_, 0)
            lo_ >>= 1
            hi_ >>= 1
        return (r - l + 1) - c < 2 and best > r

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        old = self.vals.get(i, 0)
        if old == val:
            return
        if old:
            s = self.chains[old]
            p, nx = s.pred(i), s.succ(i)
            if p is not None:
                self._set(p, INF if nx is None else nx, 1)
            s.remove(i)
            if not len(s):
                del self.chains[old]
        if val:
            s = self.chains.get(val)
            if s is None:
                s = self.chains[val] = SortedList()
            s.add(i)
            p, nx = s.pred(i), s.succ(i)
            self._set(i, INF if nx is None else nx, 1)
            if p is not None:
                self._set(p, i, 1)
            self.vals[i] = val
        else:
            self._set(i, INF, 0)
            del self.vals[i]

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.vals.get(i, 0)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
