# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeMin-rightmostLtX-rightmostLteX/template.py
# @operations: leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMin rightmostLtX rightmostLteX
# @data-structure-type: seg-tree
# @complexities:
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   rangeMin: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   build: N
# @memory:
#   layout: pow2-iterative
#   node: tree[4*N]
#   tags: none
#   other: none
#   note: tree holds each node's min; tree is 2*size where size is the next power of two >= n, so between 2N and 4N slots; arr is a reference
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/MinSeg.py

# ⚠️ Not fully benchmarked but should be pretty fast, 2n iterative tree
# Mirror of MaxSegTree with min operations
class MinSegTree:
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)

        size = 1
        while size < self.n:
            size <<= 1
        self.size = size

        tree = [float("inf")] * (2 * size)
        base = size
        for i, v in enumerate(arr):
            tree[base + i] = v
        for idx in range(size - 1, 0, -1):
            left = tree[idx << 1]
            right = tree[(idx << 1) | 1]
            tree[idx] = left if left <= right else right
        self.tree = tree

    def _queryHalfOpen(self, l, r):
        tree = self.tree
        l += self.size
        r += self.size
        ans = float("inf")
        while l < r:
            if l & 1:
                v = tree[l]
                ans = v if v <= ans else ans
                l += 1
            if r & 1:
                r -= 1
                v = tree[r]
                ans = v if v <= ans else ans
            l >>= 1
            r >>= 1
        return ans

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        return self._queryHalfOpen(l, r + 1)

    # Point overwrite: a[index] = newVal. Only updates the tree; the array you passed in is untouched.
    def pointAssign(self, index, newVal):
        tree = self.tree
        pos = self.size + index
        tree[pos] = newVal
        pos >>= 1
        while pos:
            left = tree[pos << 1]
            right = tree[(pos << 1) | 1]
            tree[pos] = left if left <= right else right
            pos >>= 1

    # Same as pointAssign, but also writes newVal into the array you passed in.
    def pointAssignAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        self.pointAssign(index, newVal)

    # O(logN) -- first i in [l, r] with a[i] <= x, or -1
    def leftmostLteX(self, l, r, x):
        t, size = self.tree, self.size
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
        t, size = self.tree, self.size
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

    # O(logN) -- last i in [l, r] with a[i] <= x, or -1
    def rightmostLteX(self, l, r, x):
        t, size = self.tree, self.size
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
        t, size = self.tree, self.size
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

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.tree[self.size + i]

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.tree[self.size + i]:
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.tree[self.size + i]:
            self.pointAssign(i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.tree[self.size + i] + delta)