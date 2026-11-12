# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countDistinct-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/template.py
# @operations: countDistinct getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
# @data-structure-type: BIT
# @letters: same
# @complexities:
#   countDistinct: log^2(N)
#   getAll: N
#   pointAdd: log^2(N) amortized
#   pointAssign: log^2(N) amortized
#   pointChmax: log^2(N) amortized
#   pointChmin: log^2(N) amortized
#   pointGet: log(N)
#   rangeAssign: log^2(N) amortized
#   build: N*log^2(N)
# @memory:
#   layout: none
#   node: sets[1*N*log(N)] last[1*N]
#   tags: none
#   other: nxt[1*N] end[1*N] val[1*N] starts[1*N] chains[1*N]
#   note: the array is kept as runs of equal values; Fenwick node j keeps an ordered set of the nxt values in its lowbit(j) positions, at most N*log(N)/2 keys in all (fewer once assigns merge runs); those are balanced-tree / bucket entries, several times heavier than a plain int

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

# Range count distinct with range assign, online. All indices 0-based, ranges inclusive [l, r].
# The array is kept as runs: run s covers s..end[s], all holding val[s] (at first every element is its own run; an
# assign makes l..r one run). starts holds every run start, chains[v] the starts of the runs holding v.
# Only a run's last position e has a point: nxt[e] = the start of the next run holding the same value, else n (every
# other position has nxt = -1: its next equal value is right after it). A value is counted once in a[l..r] at its last
# occurrence there, so countDistinct(l, r) = [the run holding r continues past r] + #{run ends e in [l, r] : nxt[e] >
# r}.
# Points with nxt == n always count, so a plain Fenwick tree tracks them; every other nxt is a distinct run start < n,
# kept in a Fenwick tree of sorted sets: node j holds the nxt values of the lowbit(j) positions it covers, so a prefix
# count of "nxt > r" visits log N nodes with one rank query each.
# An assign removes the runs it covers (each one was made by an earlier op, so that is O(1) amortized of them) and
# changes O(1) points per run added or removed. No two positions may share an nxt value < n at any moment (the C++
# version keeps them in sets, not multisets), so a point is always cleared before its value is handed on.


class DynamicDistinctAssign:
    __slots__ = ("n", "nxt", "last", "sets", "end", "val", "starts", "chains", "salt")

    # O(N log^2 N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.end = list(range(n))
        self.val = list(arr)
        nxt = self.nxt = [n] * n
        positions = {}
        # int values are salted as dict keys, so no fixed input can make them collide
        salt = self.salt = getrandbits(62)
        for i, v in enumerate(arr):
            if type(v) is int:
                v ^= salt
            if v in positions:
                nxt[positions[v][-1]] = i
                positions[v].append(i)
            else:
                positions[v] = [i]
        self.chains = {v: SortedList(p) for v, p in positions.items()}
        self.starts = SortedList(range(n))
        last = self.last = [0] * (n + 1)
        for i in range(n):
            if nxt[i] == n:
                last[i + 1] += 1
            j = (i + 1) + ((i + 1) & -(i + 1))
            if j <= n:
                last[j] += last[i + 1]
        self.sets = [None] + [SortedList(sorted(x for x in nxt[j - (j & -j):j] if x < n)) for j in range(1, n + 1)]

    # O(1) -- chains key of a value: ints are salted, so no fixed input can make the keys collide (str hashing is
    # already random per run)
    def _key(self, v):
        return v ^ self.salt if type(v) is int else v

    def _lastAdd(self, i, d):
        last, n = self.last, self.n
        i += 1
        while i <= n:
            last[i] += d
            i += i & -i

    # how many i in [0, x] have nxt[i] > r (x = -1 gives 0)
    def _countPast(self, x, r):
        last, sets = self.last, self.sets
        res = 0
        j = x + 1
        while j > 0:
            s = sets[j]
            res += last[j] + len(s) - s.countLess(r + 1)
            j &= j - 1
        return res

    # O(log^2 N) -- nxt[i] = v (-1: no point)
    def _setNxt(self, i, v):
        old = self.nxt[i]
        if old == v:
            return
        n, sets = self.n, self.sets
        if old == n:
            self._lastAdd(i, -1)
        elif old >= 0:
            j = i + 1
            while j <= n:
                sets[j].remove(old)
                j += j & -j
        if v == n:
            self._lastAdd(i, 1)
        elif v >= 0:
            j = i + 1
            while j <= n:
                sets[j].add(v)
                j += j & -j
        self.nxt[i] = v

    # O(log^2 N) -- make a run start at x (0 < x < n): the left part's new last position x - 1 points at x
    def _split(self, x):
        p = self.starts.pred(x + 1)
        if p == x:
            return
        e, v = self.end[p], self.val[p]
        self.end[p], self.end[x], self.val[x] = x - 1, e, v
        self.starts.add(x)
        self.chains[self._key(v)].add(x)
        self._setNxt(x - 1, x)

    # O(log^2 N) -- # of distinct values in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countDistinct(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countDistinct: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        tail = 1 if self.end[self.starts.pred(r + 1)] > r else 0  # a[r]'s run goes on past r: count it here
        return tail + self._countPast(r, r) - self._countPast(l - 1, r)

    # O(log^2 N) amortized -- a[i] = val for every i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, val):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, starts, chains, end, vals = self.n, self.starts, self.chains, self.end, self.val
        self._split(l)
        if r + 1 < n:
            self._split(r + 1)
        s = l
        while s is not None and s <= r:  # drop every run inside l..r
            nx = starts.succ(s)
            key = self._key(vals[s])
            chain = chains[key]
            q, after = chain.pred(s), chain.succ(s)
            self._setNxt(end[s], -1)  # clear s's point first, so the value it held is free for q
            chain.remove(s)
            if not len(chain):
                del chains[key]
            if q is not None:
                self._setNxt(end[q], n if after is None else after)
            if s != l:
                starts.remove(s)
            s = nx
        end[l], vals[l] = r, val
        key = self._key(val)
        chain = chains.get(key)
        if chain is None:
            chain = chains[key] = SortedList()
        chain.add(l)
        q, after = chain.pred(l), chain.succ(l)
        if q is not None:
            self._setNxt(end[q], l)  # move q off `after` first, then hand `after` to the new run
        self._setNxt(r, n if after is None else after)

    # O(log^2 N) amortized -- a[i] = val; needs 0 <= i < n, else IndexError
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

    # O(log^2 N) amortized -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAssign(i, i, self.pointGet(i) + delta)

    # O(log^2 N) amortized -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.pointGet(i):
            self.rangeAssign(i, i, val)

    # O(log^2 N) amortized -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.pointGet(i):
            self.rangeAssign(i, i, val)
