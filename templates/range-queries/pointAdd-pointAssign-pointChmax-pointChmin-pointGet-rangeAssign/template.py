# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
# @data-structure-type: seg-tree
# @letters: same
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: 1
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAssign: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: stamp[1*N] val[1*N]
#   tags: stamp[1*N] val[1*N]
#   other: none
#   note: every node remembers the last assignment that covered it and when; a point takes the newest one on its path; leaves count as node data, internal nodes as tags

# Range assign + point ops, no pushing anywhere. All indices 0-based, ranges inclusive [l, r].
# Assignments are stamped with an increasing counter; pointGet returns the value with the largest stamp
# among the leaf and its ancestors. A point write is just a newer stamp on the leaf, so it is O(1).
class RangeAssignTree:
    __slots__ = ("n", "stamp", "val", "clock")

    # O(N) -- leaves start with stamp 0, internal nodes with -1 (never assigned)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.stamp = [-1] * n + [0] * n
        self.val = [0] * n + list(arr)
        self.clock = 0

    # O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        stamp, val = self.stamp, self.val
        self.clock += 1
        c = self.clock
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                stamp[l] = c
                val[l] = v
                l += 1
            if r & 1:
                r -= 1
                stamp[r] = c
                val[r] = v
            l >>= 1
            r >>= 1

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        stamp, val = self.stamp, self.val
        p = i + self.n
        best = stamp[p]
        res = val[p]
        p >>= 1
        while p:
            s = stamp[p]
            if s > best:
                best = s
                res = val[p]
            p >>= 1
        return res

    # O(N) -- the whole array: hand each node's assign to its children when it is newer than theirs (a parent's
    # index is below its children's, so in index order each node already holds the newest assign on its path)
    def getAll(self):
        stamp, val = self.stamp, self.val
        for x in range(2, 2 * self.n):
            p = x >> 1
            if stamp[p] > stamp[x]:
                stamp[x] = stamp[p]
                val[x] = val[p]
        return val[self.n:]

    # O(1) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.clock += 1
        p = i + self.n
        self.stamp[p] = self.clock
        self.val[p] = v

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if v > self.pointGet(i):
            self.pointAssign(i, v)

    # O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if v < self.pointGet(i):
            self.pointAssign(i, v)
