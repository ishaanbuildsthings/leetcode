# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/template.py
# @operations: countOccurrences pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: positions
# @complexities:
#   countOccurrences: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: pos[1*N]
#   tags: none
#   other: a[1*N]
#   note: pos maps each value to its sorted indices (a bucketed SortedList, defined at the top of the file, so each change is a few binary searches plus a C-level shift of at most 1024 elements)

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

# "How many times does x appear in a[l..r]?" with point updates. All indices 0-based, ranges inclusive.
# Each value keeps the sorted list of its indices; a query is two binary searches in x's list, and an assign moves
# one index from the old value's list to the new one's.


class DynamicOccurrenceLists:
    __slots__ = ("a", "pos")

    # O(N)
    def __init__(self, arr):
        self.a = list(arr)
        pos = {}
        for i, v in enumerate(arr):
            if v in pos:
                pos[v].append(i)
            else:
                pos[v] = [i]
        self.pos = {v: SortedList(p) for v, p in pos.items()}

    # O(logN) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        p = self.pos.get(x)
        return p.countLess(r + 1) - p.countLess(l) if p is not None and l <= r else 0

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        old = self.a[i]
        if old == val:
            return
        pos = self.pos
        p = pos[old]
        p.remove(i)
        if not len(p):
            del pos[old]
        p = pos.get(val)
        if p is None:
            p = pos[val] = SortedList()
        p.add(i)
        self.a[i] = val

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.a[i]

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.a[i] + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.a[i]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.a[i]:
            self.pointAssign(i, val)
