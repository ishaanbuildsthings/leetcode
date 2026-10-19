# @operations: leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rightmostGtX rightmostGteX rightmostLtX rightmostLteX
# @data-structure-type: seg-tree
# @complexities:
#   leftmostGtX: log(N)
#   leftmostGteX: log(N)
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   rangeMax: log(N)
#   rangeMin: log(N)
#   rightmostGtX: log(N)
#   rightmostGteX: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   build: N
# @memory:
#   layout: pow2-iterative
#   node: mx[4*N] mn[4*N]
#   tags: none
#   other: none
#   note: two flat arrays of 2*size slots (size = next power of two >= n); padding leaves are -inf / +inf

# Range max / min and leftmost / rightmost index with a[i] >= x, > x, <= x or < x, with
# point updates. All indices 0-based, ranges inclusive [l, r]. Searches return -1 when nothing qualifies.
# Iterative over a power-of-two layout so the searches can descend; every field is its own flat list.
INF = float("inf")


class MaxMinTree:
    __slots__ = ("n", "size", "mx", "mn")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        size = 1
        while size < n:
            size <<= 1
        self.size = size
        mx = self.mx = [-INF] * (2 * size)
        mn = self.mn = [INF] * (2 * size)
        for i, v in enumerate(arr):
            mx[size + i] = mn[size + i] = v
        for x in range(size - 1, 0, -1):
            self._pull(x)

    def _pull(self, x):
        mx, mn = self.mx, self.mn
        a, b = mx[2 * x], mx[2 * x + 1]
        mx[x] = a if a > b else b
        a, b = mn[2 * x], mn[2 * x + 1]
        mn[x] = a if a < b else b

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        mx, res = self.mx, -INF
        l += self.size
        r += self.size + 1
        while l < r:
            if l & 1:
                if mx[l] > res:
                    res = mx[l]
                l += 1
            if r & 1:
                r -= 1
                if mx[r] > res:
                    res = mx[r]
            l >>= 1
            r >>= 1
        return res

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        mn, res = self.mn, INF
        l += self.size
        r += self.size + 1
        while l < r:
            if l & 1:
                if mn[l] < res:
                    res = mn[l]
                l += 1
            if r & 1:
                r -= 1
                if mn[r] < res:
                    res = mn[r]
            l >>= 1
            r >>= 1
        return res

    # O(logN) -- first i in [l, r] with a[i] >= x, or -1
    def leftmostGteX(self, l, r, x):
        t, size = self.mx, self.size
        p = l + size
        while True:
            while not p & 1:  # climb while p is a left child: its parent starts at the same index
                p >>= 1
            if t[p] >= x:  # the answer is inside p: descend, preferring the left child
                while p < size:
                    p <<= 1
                    if not t[p] >= x:
                        p += 1
                p -= size
                return p if p <= r else -1
            p += 1
            if not p & (p - 1):  # walked off the right edge of the tree
                return -1

    # O(logN) -- first i in [l, r] with a[i] > x, or -1
    def leftmostGtX(self, l, r, x):
        t, size = self.mx, self.size
        p = l + size
        while True:
            while not p & 1:  # climb while p is a left child: its parent starts at the same index
                p >>= 1
            if t[p] > x:  # the answer is inside p: descend, preferring the left child
                while p < size:
                    p <<= 1
                    if not t[p] > x:
                        p += 1
                p -= size
                return p if p <= r else -1
            p += 1
            if not p & (p - 1):  # walked off the right edge of the tree
                return -1

    # O(logN) -- first i in [l, r] with a[i] <= x, or -1
    def leftmostLteX(self, l, r, x):
        t, size = self.mn, self.size
        p = l + size
        while True:
            while not p & 1:  # climb while p is a left child: its parent starts at the same index
                p >>= 1
            if t[p] <= x:  # the answer is inside p: descend, preferring the left child
                while p < size:
                    p <<= 1
                    if not t[p] <= x:
                        p += 1
                p -= size
                return p if p <= r else -1
            p += 1
            if not p & (p - 1):  # walked off the right edge of the tree
                return -1

    # O(logN) -- first i in [l, r] with a[i] < x, or -1
    def leftmostLtX(self, l, r, x):
        t, size = self.mn, self.size
        p = l + size
        while True:
            while not p & 1:  # climb while p is a left child: its parent starts at the same index
                p >>= 1
            if t[p] < x:  # the answer is inside p: descend, preferring the left child
                while p < size:
                    p <<= 1
                    if not t[p] < x:
                        p += 1
                p -= size
                return p if p <= r else -1
            p += 1
            if not p & (p - 1):  # walked off the right edge of the tree
                return -1

    # O(logN) -- last i in [l, r] with a[i] >= x, or -1
    def rightmostGteX(self, l, r, x):
        t, size = self.mx, self.size
        p = r + size + 1
        while True:
            p -= 1
            while p > 1 and p & 1:  # climb while p is a right child: its parent ends at the same index
                p >>= 1
            if t[p] >= x:  # the answer is inside p: descend, preferring the right child
                while p < size:
                    p = 2 * p + 1
                    if not t[p] >= x:
                        p -= 1
                p -= size
                return p if p >= l else -1
            if not p & (p - 1):  # walked off the left edge of the tree
                return -1

    # O(logN) -- last i in [l, r] with a[i] > x, or -1
    def rightmostGtX(self, l, r, x):
        t, size = self.mx, self.size
        p = r + size + 1
        while True:
            p -= 1
            while p > 1 and p & 1:  # climb while p is a right child: its parent ends at the same index
                p >>= 1
            if t[p] > x:  # the answer is inside p: descend, preferring the right child
                while p < size:
                    p = 2 * p + 1
                    if not t[p] > x:
                        p -= 1
                p -= size
                return p if p >= l else -1
            if not p & (p - 1):  # walked off the left edge of the tree
                return -1

    # O(logN) -- last i in [l, r] with a[i] <= x, or -1
    def rightmostLteX(self, l, r, x):
        t, size = self.mn, self.size
        p = r + size + 1
        while True:
            p -= 1
            while p > 1 and p & 1:  # climb while p is a right child: its parent ends at the same index
                p >>= 1
            if t[p] <= x:  # the answer is inside p: descend, preferring the right child
                while p < size:
                    p = 2 * p + 1
                    if not t[p] <= x:
                        p -= 1
                p -= size
                return p if p >= l else -1
            if not p & (p - 1):  # walked off the left edge of the tree
                return -1

    # O(logN) -- last i in [l, r] with a[i] < x, or -1
    def rightmostLtX(self, l, r, x):
        t, size = self.mn, self.size
        p = r + size + 1
        while True:
            p -= 1
            while p > 1 and p & 1:  # climb while p is a right child: its parent ends at the same index
                p >>= 1
            if t[p] < x:  # the answer is inside p: descend, preferring the right child
                while p < size:
                    p = 2 * p + 1
                    if not t[p] < x:
                        p -= 1
                p -= size
                return p if p >= l else -1
            if not p & (p - 1):  # walked off the left edge of the tree
                return -1

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        p = self.size + i
        self.mx[p] = self.mn[p] = val
        p >>= 1
        while p:
            self._pull(p)
            p >>= 1

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.mx[self.size + i]

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.mx[self.size + i]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.mx[self.size + i]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.mx[self.size + i] + delta)
