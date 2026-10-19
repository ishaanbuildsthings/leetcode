# @operations: countDistinct pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: BIT
# @complexities:
#   countDistinct: log^2(N)
#   pointAdd: log^2(N)
#   pointAssign: log^2(N)
#   pointChmax: log^2(N)
#   pointChmin: log^2(N)
#   pointGet: 1
#   build: N*log^2(N)
# @memory:
#   layout: none
#   node: sets[1*N*log(N)] last[1*N]
#   tags: none
#   other: a[1*N] nxt[1*N] chains[1*N]
#   note: Fenwick node j keeps an ordered set of the nxt values in its lowbit(j) positions, about N*log(N)/2 keys in all; those are balanced-tree / bucket entries, several times heavier than a plain int (measured ~100 MB peak in C++ at N = 2e5)

from bisect import bisect_left, bisect_right, insort

# Range count distinct with point updates in O(log^2 N), online. All indices 0-based, ranges inclusive [l, r].
# nxt[i] = next j > i with a[j] == a[i], else n. a[l..r] has one distinct value per position whose next occurrence
# is past r, so countDistinct(l, r) = #{i in [l, r] : nxt[i] > r}, a 2D count; an assign changes at most 3 nxt values.
# Positions with nxt[i] == n (last occurrences) always count, so a plain Fenwick tree tracks them. Every other nxt
# value is a distinct position < n, kept in a Fenwick tree of sorted sets: node j holds the nxt values of the
# lowbit(j) positions it covers, so a prefix count of "nxt > r" visits log N nodes with one rank query each.
# chains[v] = the sorted positions holding value v, for the predecessor / successor an assign has to rewire.


class DynamicDistinctBIT:
    __slots__ = ("n", "a", "nxt", "last", "sets", "chains")

    # O(N log^2 N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.a = list(arr)
        nxt = self.nxt = [n] * n
        positions = {}
        for i, v in enumerate(arr):
            if v in positions:
                nxt[positions[v][-1]] = i
                positions[v].append(i)
            else:
                positions[v] = [i]
        self.chains = {v: SortedList(p) for v, p in positions.items()}
        last = self.last = [0] * (n + 1)
        for i in range(n):
            if nxt[i] == n:
                last[i + 1] += 1
            j = (i + 1) + ((i + 1) & -(i + 1))
            if j <= n:
                last[j] += last[i + 1]
        self.sets = [None] + [SortedList(sorted(x for x in nxt[j - (j & -j):j] if x < n)) for j in range(1, n + 1)]

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

    # O(log^2 N) -- nxt[i] = v
    def _setNxt(self, i, v):
        old = self.nxt[i]
        if old == v:
            return
        n, sets = self.n, self.sets
        if old == n:
            self._lastAdd(i, -1)
        else:
            j = i + 1
            while j <= n:
                sets[j].remove(old)
                j += j & -j
        if v == n:
            self._lastAdd(i, 1)
        else:
            j = i + 1
            while j <= n:
                sets[j].add(v)
                j += j & -j
        self.nxt[i] = v

    # O(log^2 N) -- # of distinct values in a[l..r]
    def countDistinct(self, l, r):
        if l > r:
            return 0
        return self._countPast(r, r) - self._countPast(l - 1, r)

    # O(log^2 N) -- a[i] = val; rewires i's old predecessor, i's new predecessor, and i. The order matters: no two
    # positions may share an nxt value < n at any moment (the C++ version keeps them in sets, not multisets)
    def pointAssign(self, i, val):
        old = self.a[i]
        if old == val:
            return
        n, chains = self.n, self.chains
        chain = chains[old]
        p, s = chain.pred(i), chain.succ(i)
        self._setNxt(i, n)  # unlink i first, so its successor is free for p
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
        if p is not None:
            self._setNxt(p, i)  # move p off s first, then hand s to i
        self._setNxt(i, n if s is None else s)
        self.a[i] = val

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.a[i]

    # O(log^2 N) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.a[i] + delta)

    # O(log^2 N) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.a[i]:
            self.pointAssign(i, val)

    # O(log^2 N) -- a[i] = min(a[i], val)
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
