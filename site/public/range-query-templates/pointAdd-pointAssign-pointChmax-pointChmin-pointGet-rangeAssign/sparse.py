# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/sparse.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeAssign: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: none
#   tags: stamp[4*log(U)] val[4*log(U)]
#   other: children[8*log(U)]
#   note: per update, the nodes a range update visits (at most 4 per level), each remembering the newest assignment covering it. A dict keyed by heap index, storing only the covering nodes (so point assign is O(1))

# Range assign + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# No pushing anywhere: assignments are stamped with an increasing counter, every node remembers the newest one
# covering it, and pointGet returns the newest on the leaf's root path. A point write is a newer stamp on the leaf,
# so it is O(1). Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi] -> (stamp, value).


from random import getrandbits

SALT = getrandbits(62)  # dict keys are salted positions, so no fixed input can make the dict collide


class SparseRangeAssignTree:
    __slots__ = ("lo", "hi", "size", "t", "clock")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of i is size + (i - lo)
        self.t = {}
        self.clock = 0

    # O(logU) -- a[i] = val for i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def rangeAssign(self, l, r, val):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeAssign: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        self.clock += 1
        e = (self.clock, val)
        t = self.t
        l += self.size - self.lo
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                t[l ^ SALT] = e
                l += 1
            if r & 1:
                r -= 1
                t[r ^ SALT] = e
            l >>= 1
            r >>= 1

    # O(logU) -- a[i]; needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointGet: needs lo <= i <= hi, got i = {i}")
        t = self.t
        p = self.size + i - self.lo
        best, res = t.get(p ^ SALT, (0, 0))
        p >>= 1
        while p:
            e = t.get(p ^ SALT)
            if e is not None and e[0] > best:
                best, res = e
            p >>= 1
        return res

    # O(logU) -- a[i] = val; needs lo <= i <= hi, else IndexError
    def pointAssign(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAssign: needs lo <= i <= hi, got i = {i}")
        self.clock += 1
        self.t[(self.size + i - self.lo) ^ SALT] = (self.clock, val)

    # O(logU) -- a[i] += delta; needs lo <= i <= hi, else IndexError
    def pointAdd(self, i, delta):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAdd: needs lo <= i <= hi, got i = {i}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val); needs lo <= i <= hi, else IndexError
    def pointChmax(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmax: needs lo <= i <= hi, got i = {i}")
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logU) -- a[i] = min(a[i], val); needs lo <= i <= hi, else IndexError
    def pointChmin(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmin: needs lo <= i <= hi, got i = {i}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)
