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
#   note: tree is a min tree over nxt[i]; chains maps each value to its sorted positions (Python: plain lists, so an insert is a memmove over that value's occurrences)

from bisect import bisect_left

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
        chains = self.chains = {}
        for i, v in enumerate(arr):
            if v in chains:
                chains[v].append(i)
            else:
                chains[v] = [i]
        for chain in chains.values():
            for k in range(len(chain) - 1):
                tree[n + chain[k]] = chain[k + 1]
            tree[n + chain[-1]] = n
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
        k = bisect_left(chain, i)
        if k:
            self._setNxt(chain[k - 1], chain[k + 1] if k + 1 < len(chain) else n)
        chain.pop(k)
        if not chain:
            del chains[old]
        if val in chains:
            chain = chains[val]
        else:
            chain = chains[val] = []
        k = bisect_left(chain, i)
        chain.insert(k, i)
        self._setNxt(i, chain[k + 1] if k + 1 < len(chain) else n)
        if k:
            self._setNxt(chain[k - 1], i)
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
