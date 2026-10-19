# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorSqrt
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(N)+log(log(U))
#   pointAssign: log(N)+log(log(U))
#   pointChmax: log(N)+log(log(U))
#   pointChmin: log(N)+log(log(U))
#   pointGet: log(N)+log(log(U))
#   rangeFloorSqrt: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: none
#   tags: tree[2*N]
#   other: none
#   note: tree[n:] holds the values, tree[1:n] holds how many floor-sqrts are pending at each node (capped at 6)

from math import isqrt

# Range floor-sqrt + point ops. All indices 0-based, ranges inclusive [l, r].
# Pending sqrts on a node are just a count. Six isqrts take any value below 2^64 down to 0 or 1, which are
# fixed points, so counts are capped at MAX_SQRTS. Requires 0 <= a[i] < 2^64 at all times.
MAX_SQRTS = 6


class RangeFloorSqrtTree:
    __slots__ = ("n", "tree")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.tree = [0] * n + list(arr)

    # O(logN) -- a[i] = floor(sqrt(a[i])) for i in [l, r]
    def rangeFloorSqrt(self, l, r):
        tree, n = self.tree, self.n
        l += n
        r += n + 1
        while l < r:
            if l & 1:
                if l >= n:
                    tree[l] = isqrt(tree[l])
                elif tree[l] < MAX_SQRTS:
                    tree[l] += 1
                l += 1
            if r & 1:
                r -= 1
                if r >= n:
                    tree[r] = isqrt(tree[r])
                elif tree[r] < MAX_SQRTS:
                    tree[r] += 1
            l >>= 1
            r >>= 1

    # O(logN + loglogU) -- apply the pending sqrts on i's path, so nothing above i is pending
    def _push(self, p):
        tree, n = self.tree, self.n
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            k = tree[x]
            if k:
                y = x << 1
                for c in (y, y | 1):
                    if c >= n:
                        v = tree[c]
                        for _ in range(k):
                            if v < 2:
                                break
                            v = isqrt(v)
                        tree[c] = v
                    else:
                        u = tree[c] + k
                        tree[c] = u if u < MAX_SQRTS else MAX_SQRTS
                tree[x] = 0

    # O(logN + loglogU) -- a[i]
    def pointGet(self, i):
        tree = self.tree
        p = i + self.n
        v = tree[p]
        k = 0
        p >>= 1
        while p:
            k += tree[p]
            p >>= 1
        for _ in range(k if k < MAX_SQRTS else MAX_SQRTS):
            if v < 2:
                break
            v = isqrt(v)
        return v

    # O(logN + loglogU) -- a[i] = val
    def pointAssign(self, i, val):
        p = i + self.n
        self._push(p)
        self.tree[p] = val

    # O(logN + loglogU) -- a[i] += delta
    def pointAdd(self, i, delta):
        p = i + self.n
        self._push(p)
        self.tree[p] += delta

    # O(logN + loglogU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        p = i + self.n
        self._push(p)
        if val > self.tree[p]:
            self.tree[p] = val

    # O(logN + loglogU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        p = i + self.n
        self._push(p)
        if val < self.tree[p]:
            self.tree[p] = val
