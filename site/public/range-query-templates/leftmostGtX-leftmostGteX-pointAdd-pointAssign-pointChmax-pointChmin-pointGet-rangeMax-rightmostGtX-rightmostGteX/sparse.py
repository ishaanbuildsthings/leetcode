# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeMax-rightmostGtX-rightmostGteX/sparse.py
# @operations: leftmostGtX leftmostGteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rightmostGtX rightmostGteX
# @data-structure-type: seg-tree
# @complexities:
#   leftmostGtX: log(U)
#   leftmostGteX: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeMax: log(U)
#   rightmostGtX: log(U)
#   rightmostGteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mx[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per update, one node per level of the touched path;  a dict keyed by heap index, a missing key is a block of zeros

NEG = float("-inf")
INF = float("inf")

# Range max and leftmost / rightmost index with a[i] >= / > x, with point updates, over
# any index range [lo, hi] (huge or negative is fine); every position starts at 0. Searches return lo - 1 when nothing
# qualifies (-1 when lo = 0). Sparse: dicts keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of
# zeros. The searches are the dense tree's iterative walks: climb from the boundary until a node holds a match,
# then descend into it.


class SparseMaxSearchTree:
    __slots__ = ("lo", "size", "mx")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; leaf of i is size + (i - lo)
        self.mx = {}

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        p = self.size + i - self.lo
        self.mx[p] = val
        p >>= 1
        while p:
            u, w = self.mx.get(2 * p, 0), self.mx.get(2 * p + 1, 0)
            self.mx[p] = u if u > w else w
            p >>= 1

    # O(logU) -- max of a[l..r]
    def rangeMax(self, l, r):
        t, res = self.mx, NEG
        l += self.size - self.lo
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                v = t.get(l, 0)
                if v > res:
                    res = v
                l += 1
            if r & 1:
                r -= 1
                v = t.get(r, 0)
                if v > res:
                    res = v
            l >>= 1
            r >>= 1
        return res

    # O(logU) -- first i in [l, r] with a[i] >= x, or lo - 1
    def leftmostGteX(self, l, r, x):
        t, size = self.mx, self.size
        p = l - self.lo + size
        while True:
            while not p & 1:  # climb while p is a left child: its parent starts at the same index
                p >>= 1
            if t.get(p, 0) >= x:  # the answer is inside p: descend, preferring the left child
                while p < size:
                    p <<= 1
                    if not t.get(p, 0) >= x:
                        p += 1
                i = p - size + self.lo
                return i if i <= r else self.lo - 1
            p += 1
            if not p & (p - 1):  # walked off the right edge
                return self.lo - 1

    # O(logU) -- last i in [l, r] with a[i] >= x, or lo - 1
    def rightmostGteX(self, l, r, x):
        t, size = self.mx, self.size
        p = r - self.lo + size + 1
        while True:
            p -= 1
            while p > 1 and p & 1:  # climb while p is a right child: its parent ends at the same index
                p >>= 1
            if t.get(p, 0) >= x:  # the answer is inside p: descend, preferring the right child
                while p < size:
                    p = 2 * p + 1
                    if not t.get(p, 0) >= x:
                        p -= 1
                i = p - size + self.lo
                return i if i >= l else self.lo - 1
            if not p & (p - 1):  # walked off the left edge
                return self.lo - 1

    # O(logU) -- first i in [l, r] with a[i] > x, or lo - 1
    def leftmostGtX(self, l, r, x):
        t, size = self.mx, self.size
        p = l - self.lo + size
        while True:
            while not p & 1:  # climb while p is a left child: its parent starts at the same index
                p >>= 1
            if t.get(p, 0) > x:  # the answer is inside p: descend, preferring the left child
                while p < size:
                    p <<= 1
                    if not t.get(p, 0) > x:
                        p += 1
                i = p - size + self.lo
                return i if i <= r else self.lo - 1
            p += 1
            if not p & (p - 1):  # walked off the right edge
                return self.lo - 1

    # O(logU) -- last i in [l, r] with a[i] > x, or lo - 1
    def rightmostGtX(self, l, r, x):
        t, size = self.mx, self.size
        p = r - self.lo + size + 1
        while True:
            p -= 1
            while p > 1 and p & 1:  # climb while p is a right child: its parent ends at the same index
                p >>= 1
            if t.get(p, 0) > x:  # the answer is inside p: descend, preferring the right child
                while p < size:
                    p = 2 * p + 1
                    if not t.get(p, 0) > x:
                        p -= 1
                i = p - size + self.lo
                return i if i >= l else self.lo - 1
            if not p & (p - 1):  # walked off the left edge
                return self.lo - 1

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self.mx.get(self.size + i - self.lo, 0)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
