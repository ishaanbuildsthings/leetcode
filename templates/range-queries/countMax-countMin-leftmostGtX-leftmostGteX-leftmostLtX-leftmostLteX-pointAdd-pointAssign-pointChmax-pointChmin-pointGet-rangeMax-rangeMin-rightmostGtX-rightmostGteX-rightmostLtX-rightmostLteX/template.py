# @operations: countMax countMin leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rightmostGtX rightmostGteX rightmostLtX rightmostLteX
# @data-structure-type: seg-tree
# @complexities:
#   countMax: log(N)
#   countMin: log(N)
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
#   node: mx[4*N] cntMx[4*N] mn[4*N] cntMn[4*N]
#   tags: none
#   other: none
#   note: four flat arrays of 2*size slots (size = next power of two >= n); padding leaves are -inf/+inf with count 0
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/MaxAndMinAndCountsAndGteLteIndexSegmentTree.py

# Range max / min, how many times each appears, and leftmost / rightmost index with a[i] >= x or <= x, with
# point updates. All indices 0-based, ranges inclusive [l, r]. Searches return -1 when nothing qualifies.
# Iterative over a power-of-two layout so the searches can descend; every field is its own flat list.
INF = float("inf")


class MaxMinCountTree:
    __slots__ = ("n", "size", "mx", "cntMx", "mn", "cntMn")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        size = 1
        while size < n:
            size <<= 1
        self.size = size
        mx = self.mx = [-INF] * (2 * size)
        mn = self.mn = [INF] * (2 * size)
        cntMx = self.cntMx = [0] * (2 * size)
        cntMn = self.cntMn = [0] * (2 * size)
        for i, v in enumerate(arr):
            mx[size + i] = mn[size + i] = v
            cntMx[size + i] = cntMn[size + i] = 1
        for x in range(size - 1, 0, -1):
            self._pull(x)

    def _pull(self, x):
        mx, mn, cntMx, cntMn = self.mx, self.mn, self.cntMx, self.cntMn
        a, b = 2 * x, 2 * x + 1
        if mx[a] > mx[b]:
            mx[x], cntMx[x] = mx[a], cntMx[a]
        elif mx[a] < mx[b]:
            mx[x], cntMx[x] = mx[b], cntMx[b]
        else:
            mx[x], cntMx[x] = mx[a], cntMx[a] + cntMx[b]
        if mn[a] < mn[b]:
            mn[x], cntMn[x] = mn[a], cntMn[a]
        elif mn[a] > mn[b]:
            mn[x], cntMn[x] = mn[b], cntMn[b]
        else:
            mn[x], cntMn[x] = mn[a], cntMn[a] + cntMn[b]

    # O(logN) -- (max of a[l..r], how many times it appears)
    def _maxCount(self, l, r):
        mx, cntMx = self.mx, self.cntMx
        best, cnt = -INF, 0
        l += self.size
        r += self.size + 1
        while l < r:
            if l & 1:
                if mx[l] > best:
                    best, cnt = mx[l], cntMx[l]
                elif mx[l] == best:
                    cnt += cntMx[l]
                l += 1
            if r & 1:
                r -= 1
                if mx[r] > best:
                    best, cnt = mx[r], cntMx[r]
                elif mx[r] == best:
                    cnt += cntMx[r]
            l >>= 1
            r >>= 1
        return best, cnt

    # O(logN) -- (min of a[l..r], how many times it appears)
    def _minCount(self, l, r):
        mn, cntMn = self.mn, self.cntMn
        best, cnt = INF, 0
        l += self.size
        r += self.size + 1
        while l < r:
            if l & 1:
                if mn[l] < best:
                    best, cnt = mn[l], cntMn[l]
                elif mn[l] == best:
                    cnt += cntMn[l]
                l += 1
            if r & 1:
                r -= 1
                if mn[r] < best:
                    best, cnt = mn[r], cntMn[r]
                elif mn[r] == best:
                    cnt += cntMn[r]
            l >>= 1
            r >>= 1
        return best, cnt

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        return self._maxCount(l, r)[0]

    # O(logN) -- how many i in [l, r] have a[i] == max of a[l..r]
    def countMax(self, l, r):
        return self._maxCount(l, r)[1]

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        return self._minCount(l, r)[0]

    # O(logN) -- how many i in [l, r] have a[i] == min of a[l..r]
    def countMin(self, l, r):
        return self._minCount(l, r)[1]

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
