# @operations: countDistinct pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: BIT
# @complexities:
#   countDistinct: log(U)*log(U)
#   pointAdd: log(U)*log(U)
#   pointAssign: log(U)*log(U)
#   pointChmax: log(U)*log(U)
#   pointChmin: log(U)*log(U)
#   pointGet: 1
#   build: 1
# @memory:
#   layout: sparse
#   node: sets[3*log(U)] last[3*log(U)]
#   tags: none
#   other: nxt[1] chains[1] vals[1]
#   note: per point write, at most 3 nxt changes, each touching the O(logU) Fenwick nodes above its position; node j keeps an ordered set of the nxt values below it (C++: pb_ds trees in a hash map; Python: bucketed SortedLists, below, in a dict). No shared pool: every tree owns its memory

from bisect import bisect_left, bisect_right, insort

# Range count distinct with point updates in O(log^2 U), online, over any index range [lo, hi] (huge or negative is
# fine); every position starts at 0. Only nonzero positions are tracked: nxt[i] = the next position with the same
# value (none: NONE = hi + 1), and the distinct nonzero values in [l, r] are #{i in [l, r] : nxt[i] > r}, a 2D count
# on a Fenwick tree (in a dict, over offsets) whose node j keeps an ordered set of the nxt values < NONE below it,
# plus a plain count of the NONE ones. 0 is one more distinct value when the range has fewer nonzero positions than
# its length. An assign changes at most 3 nxt values, in an order that never lets two positions share an nxt value.


class SparseDistinctBIT:
    __slots__ = ("lo", "hi", "n", "none", "vals", "nxt", "last", "sets", "chains")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.none = hi + 1
        self.vals = {}  # i -> a[i], nonzero values only
        self.nxt = {}  # nonzero position -> nxt
        self.last = {}  # Fenwick tree counting positions with nxt == NONE
        self.sets = {}  # Fenwick tree of SortedLists of nxt values < NONE
        self.chains = {}  # nonzero value -> SortedList of its positions

    def _lastAdd(self, i, d):
        last, n = self.last, self.n
        j = i - self.lo + 1
        while j <= n:
            last[j] = last.get(j, 0) + d
            j += j & -j

    # how many tracked positions p <= x have nxt[p] > r (0 for x < lo)
    def _countPast(self, x, r):
        last, sets = self.last, self.sets
        res = 0
        j = x - self.lo + 1
        while j > 0:
            res += last.get(j, 0)
            s = sets.get(j)
            if s is not None:
                res += len(s) - s.countLess(r + 1)
            j &= j - 1
        return res

    # O(log^2 U) -- nxt[i] = v (None: i is not tracked, it holds 0)
    def _setNxt(self, i, v):
        old = self.nxt.get(i)
        if old == v:
            return
        n, sets = self.n, self.sets
        if old == self.none:
            self._lastAdd(i, -1)
        elif old is not None:
            j = i - self.lo + 1
            while j <= n:
                s = sets[j]
                s.remove(old)
                if not len(s):
                    del sets[j]
                j += j & -j
        if v == self.none:
            self._lastAdd(i, 1)
        elif v is not None:
            j = i - self.lo + 1
            while j <= n:
                s = sets.get(j)
                if s is None:
                    s = sets[j] = SortedList()
                s.add(v)
                j += j & -j
        if v is None:
            del self.nxt[i]
        else:
            self.nxt[i] = v

    # O(log^2 U) -- # of distinct values in a[l..r]
    def countDistinct(self, l, r):
        if l > r:
            return 0
        lo1 = self.lo - 1  # every nxt is > lo - 1, so this counts the tracked positions
        nonzero = self._countPast(r, lo1) - self._countPast(l - 1, lo1)
        return self._countPast(r, r) - self._countPast(l - 1, r) + (nonzero < r - l + 1)

    # O(log^2 U) -- a[i] = val; rewires i's old predecessor, i's new predecessor, and i
    def pointAssign(self, i, val):
        old = self.vals.get(i, 0)
        if old == val:
            return
        if old:
            s = self.chains[old]
            self._setNxt(i, None)  # unlink i first, so its successor is free for its predecessor
            p, nx = s.pred(i), s.succ(i)
            if p is not None:
                self._setNxt(p, self.none if nx is None else nx)
            s.remove(i)
            if not len(s):
                del self.chains[old]
        if val:
            s = self.chains.get(val)
            if s is None:
                s = self.chains[val] = SortedList()
            s.add(i)
            p, nx = s.pred(i), s.succ(i)
            if p is not None:
                self._setNxt(p, i)  # move the predecessor off the successor first, then hand it to i
            self._setNxt(i, self.none if nx is None else nx)
            self.vals[i] = val
        else:
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
