# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostIndexOf-leftmostIndexOfInRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rightmostIndexOf-rightmostIndexOfInRange/template.py
# @operations: getAll leftmostIndexOf leftmostIndexOfInRange pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rightmostIndexOf rightmostIndexOfInRange
# @data-structure-type: interval-map
# @complexities:
#   getAll: N
#   leftmostIndexOf: log(N)
#   leftmostIndexOfInRange: log(N)
#   pointAdd: log(N) amortized
#   pointAssign: log(N) amortized
#   pointChmax: log(N) amortized
#   pointChmin: log(N) amortized
#   pointGet: log(N)
#   rangeAssign: log(N) amortized
#   rightmostIndexOf: log(N)
#   rightmostIndexOfInRange: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: runs[1*N] byVal[1*N]
#   tags: none
#   other: none
#   note: one entry per run of equal values (at most N, usually far fewer), in the run map and in its value's set

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

# "Where is x's first / last copy, in the whole array or inside a[l..r]?" with RANGE ASSIGN and point updates. All
# indices 0-based, ranges inclusive; -1 when there is no such index. The array is kept as runs of one value: an
# ordered map start -> value, and per value the ordered set of its runs' starts. An assign splits the runs at l and
# r + 1, deletes the runs inside and adds one, so it adds at most 3 runs and pays for every run it later deletes
# (O(log N) amortized). x's first index in [l, r] is l if the run holding l has x, else the start of x's next run.


class IntervalMap:
    __slots__ = ("n", "starts", "val", "byVal")

    # O(N) -- arr: the initial array (equal neighbours become one run)
    def __init__(self, arr):
        n = self.n = len(arr)
        starts, val, by = [], {}, {}
        for i, v in enumerate(arr):
            if i == 0 or v != arr[i - 1]:
                starts.append(i)
                val[i] = v
                by.setdefault(v, []).append(i)
        self.starts = SortedList(starts)  # every run's start, in order
        self.val = val  # run start -> its value
        self.byVal = {v: SortedList(s) for v, s in by.items()}  # value -> the starts of its runs

    # O(logN) amortized -- a[i] = x for i in [l, r]
    def rangeAssign(self, l, r, x):
        if l > r:
            return
        self._split(l)
        self._split(r + 1)
        starts, val, by = self.starts, self.val, self.byVal
        s = l
        while s is not None and s <= r:  # (the runs inside [l, r], each deleted once)
            nxt = starts.succ(s)
            starts.remove(s)
            v = val.pop(s)
            p = by[v]
            p.remove(s)
            if not len(p):
                del by[v]
            s = nxt
        starts.add(l)
        val[l] = x
        p = by.get(x)
        if p is None:
            p = by[x] = SortedList()
        p.add(l)

    # O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        p = self.byVal.get(x)
        return p.lists[0][0] if p is not None else -1

    # O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        p = self.byVal.get(x)
        return self._end(p.lists[-1][-1]) if p is not None else -1

    # O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
    def leftmostIndexOfInRange(self, l, r, x):
        p = self.byVal.get(x)
        if p is None or l > r:
            return -1
        s = p.pred(l + 1)  # x's last run starting at or before l: does it reach l?
        if s is not None and self._end(s) >= l:
            return l
        s = p.succ(l)
        return s if s is not None and s <= r else -1

    # O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none
    def rightmostIndexOfInRange(self, l, r, x):
        p = self.byVal.get(x)
        if p is None or l > r:
            return -1
        s = p.pred(r + 1)  # x's last run starting at or before r
        if s is None:
            return -1
        e = min(self._end(s), r)
        return e if e >= l else -1

    # O(logN) -- a[i]
    def pointGet(self, i):
        val = self.val
        return val[i] if i in val else val[self.starts.pred(i)]

    # O(N) -- the whole array
    def getAll(self):
        out, val = [], self.val
        prev = None
        for b in self.starts.lists:
            for s in b:
                if prev is not None:
                    out += [val[prev]] * (s - prev)
                prev = s
        if prev is not None:
            out += [val[prev]] * (self.n - prev)
        return out

    # O(logN) amortized -- a[i] = v
    def pointAssign(self, i, v):
        self.rangeAssign(i, i, v)

    # O(logN) amortized -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAssign(i, i, self.pointGet(i) + delta)

    # O(logN) amortized -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        if v > self.pointGet(i):
            self.rangeAssign(i, i, v)

    # O(logN) amortized -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        if v < self.pointGet(i):
            self.rangeAssign(i, i, v)

    # ---- internals ----

    def _end(self, s):  # the last index of the run starting at s
        t = self.starts.succ(s)
        return (self.n if t is None else t) - 1

    def _split(self, i):  # make a run start at i (nothing if one does, or i == n)
        val = self.val
        if i >= self.n or i in val:
            return
        v = val[self.starts.pred(i)]
        self.starts.add(i)
        val[i] = v
        self.byVal[v].add(i)
