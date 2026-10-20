# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/sparse.py
# @operations: countOccurrences pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: positions
# @complexities:
#   countOccurrences: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: 1
#   build: 1
# @memory:
#   layout: sparse
#   node: pos[2]
#   tags: none
#   other: vals[1]
#   note: per point write, one index in its value's sorted list and one in the list of nonzero positions (bucketed SortedLists defined at the top of the file); zeros are counted as the range length minus the nonzero positions in it. No shared pool: every tree owns its memory

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

# "How many times does x appear in a[l..r]?" with point updates, over any index range [lo, hi] (huge or negative is
# fine); every position starts at 0. Each nonzero value keeps its sorted indices, and so does "any nonzero value";
# x != 0 is two rank queries in x's list, and x == 0 is the range length minus the nonzero positions in it.


class SparseOccurrenceLists:
    __slots__ = ("lo", "hi", "vals", "pos", "nz")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.vals = {}  # i -> a[i], nonzero values only
        self.pos = {}  # value -> SortedList of its indices (nonzero values only)
        self.nz = SortedList()  # indices holding a nonzero value

    # O(logU) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        if l > r:
            return 0
        if x == 0:
            nz = self.nz
            return (r - l + 1) - (nz.countLess(r + 1) - nz.countLess(l))
        s = self.pos.get(x)
        return 0 if s is None else s.countLess(r + 1) - s.countLess(l)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        old = self.vals.get(i, 0)
        if old == val:
            return
        if old:
            s = self.pos[old]
            s.remove(i)
            if not len(s):
                del self.pos[old]
        else:
            self.nz.add(i)
        if val:
            s = self.pos.get(val)
            if s is None:
                s = self.pos[val] = SortedList()
            s.add(i)
            self.vals[i] = val
        else:
            self.nz.remove(i)
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
