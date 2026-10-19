# @operations: allDistinct pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: seg-tree
# @complexities:
#   allDistinct: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: tree[2*N]
#   tags: none
#   other: a[1*N] chains[1*N]
#   note: tree is a min tree over nxt[i]; chains maps each value to its sorted positions (C++: std::set; Python: a bucketed SortedList (below), so each change is a few binary searches plus a C-level shift of at most 1024 elements)

from bisect import bisect_left, bisect_right, insort

# "Are all values in a[l..r] distinct?" with point updates. All indices 0-based, ranges inclusive [l, r].
# nxt[i] = next j > i with a[j] == a[i], else n. a[l..r] has a repeat iff some i in [l, r] has nxt[i] <= r,
# so it is all distinct iff min(nxt[l..r]) > r: one min query on an iterative 2N tree.
# An assign changes at most 3 nxt values: i's old predecessor, i's new predecessor, and i itself.


class DistinctTree:
    __slots__ = ("n", "a", "tree", "chains")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.a = list(arr)
        tree = self.tree = [0] * (2 * n)
        positions = {}
        for i, v in enumerate(arr):
            if v in positions:
                positions[v].append(i)
            else:
                positions[v] = [i]
        for p in positions.values():
            for k in range(len(p) - 1):
                tree[n + p[k]] = p[k + 1]
            tree[n + p[-1]] = n
        self.chains = {v: SortedList(p) for v, p in positions.items()}
        for x in range(n - 1, 0, -1):
            tree[x] = tree[2 * x] if tree[2 * x] < tree[2 * x + 1] else tree[2 * x + 1]

    # O(logN) -- nxt[i] = v
    def _setNxt(self, i, v):
        tree = self.tree
        p = i + self.n
        tree[p] = v
        p >>= 1
        while p:
            a, b = tree[2 * p], tree[2 * p + 1]
            tree[p] = a if a < b else b
            p >>= 1

    # O(logN) -- true iff no value repeats inside a[l..r]
    def allDistinct(self, l, r):
        tree = self.tree
        lo, hi = l + self.n, r + self.n + 1
        while lo < hi:
            if lo & 1:
                if tree[lo] <= r:
                    return False
                lo += 1
            if hi & 1:
                hi -= 1
                if tree[hi] <= r:
                    return False
            lo >>= 1
            hi >>= 1
        return True

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        old = self.a[i]
        if old == val:
            return
        n, chains = self.n, self.chains
        chain = chains[old]
        p, s = chain.pred(i), chain.succ(i)
        if p is not None:
            self._setNxt(p, n if s is None else s)
        chain.remove(i)
        if not len(chain):
            del chains[old]
        chain = chains.get(val)
        if chain is None:
            chain = chains[val] = SortedList()
        chain.add(i)
        p, s = chain.pred(i), chain.succ(i)
        self._setNxt(i, n if s is None else s)
        if p is not None:
            self._setNxt(p, i)
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
