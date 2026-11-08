# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/allDistinct-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/template.py
# @operations: allDistinct getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
# @data-structure-type: seg-tree
# @letters: same
# @complexities:
#   allDistinct: log(N)
#   getAll: N
#   pointAdd: log(N) amortized
#   pointAssign: log(N) amortized
#   pointChmax: log(N) amortized
#   pointChmin: log(N) amortized
#   pointGet: log(N)
#   rangeAssign: log(N) amortized
#   build: N*log(N)
# @memory:
#   layout: 2n-iterative
#   node: tree[2*N]
#   tags: none
#   other: end[1*N] val[1*N] starts[1*N] chains[1*N]
#   note: the array is kept as runs of equal values; tree is a min tree with one leaf per run start; starts and chains are bucketed SortedLists (defined at the top of the file, so each change is a few binary searches plus a C-level shift of at most 1024 elements); the build is O(N): a dict groups the positions, already in order

from bisect import bisect_left, bisect_right, insort
from random import getrandbits


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


# "Are all values in a[l..r] distinct?" with range assign. All indices 0-based, ranges inclusive [l, r].
# The array is kept as runs: run s covers s..end[s], all holding val[s] (at first every element is its own run; an
# assign makes l..r one run). starts holds every run start, chains[v] the starts of the runs holding v.
# tree is a min tree over positions with one leaf per run start s: s + 1 if the run is longer than 1 (a repeat right
# there), else the start of the next run holding the same value (n if none); every other leaf is n.
# a[l..r] has a repeat iff the run holding l repeats inside l..r, or some run starting in l+1..r has its leaf <= r.
# An assign removes the runs it covers (each one was made by an earlier op, so that is O(1) amortized of them) and
# changes O(1) leaves per run added or removed.


class DistinctTree:
    __slots__ = ("n", "tree", "end", "val", "starts", "chains", "salt")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.end = list(range(n))
        self.val = list(arr)
        tree = self.tree = [n] * (2 * n)
        positions = {}
        salt = self.salt = getrandbits(62)  # int values are salted as dict keys, so no fixed input can make them collide
        for i, v in enumerate(arr):
            if type(v) is int:
                v ^= salt
            if v in positions:
                positions[v].append(i)
            else:
                positions[v] = [i]
        for p in positions.values():
            for k in range(len(p) - 1):
                tree[n + p[k]] = p[k + 1]
        self.chains = {v: SortedList(p) for v, p in positions.items()}
        self.starts = SortedList(range(n))
        for x in range(n - 1, 0, -1):
            tree[x] = tree[2 * x] if tree[2 * x] < tree[2 * x + 1] else tree[2 * x + 1]

    # O(1) -- chains key of a value: ints are salted, so no fixed input can make the keys collide (str hashing is
    # already random per run)
    def _key(self, v):
        return v ^ self.salt if type(v) is int else v

    # O(logN) -- leaf of position i = v
    def _setLeaf(self, i, v):
        tree = self.tree
        p = i + self.n
        tree[p] = v
        p >>= 1
        while p:
            a, b = tree[2 * p], tree[2 * p + 1]
            tree[p] = a if a < b else b
            p >>= 1

    # O(logN) -- the leaf run s should have: s + 1 if it is longer than 1, else its value's next run start (or n)
    def _refresh(self, s):
        if self.end[s] > s:
            self._setLeaf(s, s + 1)
        else:
            nx = self.chains[self._key(self.val[s])].succ(s)
            self._setLeaf(s, self.n if nx is None else nx)

    # O(logN) -- make a run start at x (0 < x < n)
    def _split(self, x):
        p = self.starts.pred(x + 1)
        if p == x:
            return
        e, v = self.end[p], self.val[p]
        self.end[p], self.end[x], self.val[x] = x - 1, e, v
        self.starts.add(x)
        self.chains[self._key(v)].add(x)
        self._refresh(p)
        self._refresh(x)

    # O(logN) -- true iff no value repeats inside a[l..r]; needs 0 <= l <= r < n, else IndexError
    def allDistinct(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"allDistinct: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        p = self.starts.pred(l + 1)  # the run holding l
        e = self.end[p]
        if e > l:
            if l < r:
                return False
        else:
            nx = self.chains[self._key(self.val[p])].succ(p)
            if nx is not None and nx <= r:
                return False
        tree = self.tree
        lo, hi = l + 1 + self.n, r + self.n + 1
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

    # O(logN) amortized -- a[i] = val for every i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, val):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, starts, chains, end, vals = self.n, self.starts, self.chains, self.end, self.val
        self._split(l)
        if r + 1 < n:
            self._split(r + 1)
        s = l
        while s is not None and s <= r:  # drop every run inside l..r
            nxt = starts.succ(s)
            key = self._key(vals[s])
            chain = chains[key]
            q = chain.pred(s)
            chain.remove(s)
            if not len(chain):
                del chains[key]
            elif q is not None and end[q] == q:
                self._refresh(q)
            if s != l:
                starts.remove(s)
                self._setLeaf(s, n)
            s = nxt
        end[l], vals[l] = r, val
        key = self._key(val)
        chain = chains.get(key)
        if chain is None:
            chain = chains[key] = SortedList()
        chain.add(l)
        q = chain.pred(l)
        if q is not None and end[q] == q:
            self._refresh(q)
        self._refresh(l)

    # O(logN) amortized -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAssign(i, i, val)

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.val[self.starts.pred(i + 1)]

    # O(N) -- the whole array (a copy)
    def getAll(self):
        out, end, vals = [], self.end, self.val
        for b in self.starts.lists:
            for s in b:
                out.extend([vals[s]] * (end[s] - s + 1))
        return out

    # O(logN) amortized -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAssign(i, i, self.pointGet(i) + delta)

    # O(logN) amortized -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.pointGet(i):
            self.rangeAssign(i, i, val)

    # O(logN) amortized -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.pointGet(i):
            self.rangeAssign(i, i, val)
