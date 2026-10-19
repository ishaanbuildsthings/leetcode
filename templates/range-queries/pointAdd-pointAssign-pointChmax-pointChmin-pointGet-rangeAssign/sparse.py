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
#   other: links[8*log(U)]
#   note: per update, the nodes a range update visits (at most 4 per level), each remembering the newest assignment covering it; Python stores only the covering nodes (point assign is O(1) there). C++: one shared node pool, call resetPool() between test cases; Python: a dict keyed by heap index

# Range assign + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# No pushing anywhere: assignments are stamped with an increasing counter, every node remembers the newest one
# covering it, and pointGet returns the newest on the leaf's root path. A point write is a newer stamp on the leaf,
# so it is O(1). Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi] -> (stamp, value).


class SparseRangeAssignTree:
    __slots__ = ("lo", "size", "t", "clock")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of i is size + (i - lo)
        self.t = {}
        self.clock = 0

    # O(logU) -- a[i] = val for i in [l, r]
    def rangeAssign(self, l, r, val):
        self.clock += 1
        e = (self.clock, val)
        t = self.t
        l += self.size - self.lo
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                t[l] = e
                l += 1
            if r & 1:
                r -= 1
                t[r] = e
            l >>= 1
            r >>= 1

    # O(logU) -- a[i]
    def pointGet(self, i):
        t = self.t
        p = self.size + i - self.lo
        best, res = t.get(p, (0, 0))
        p >>= 1
        while p:
            e = t.get(p)
            if e is not None and e[0] > best:
                best, res = e
            p >>= 1
        return res

    # O(1) -- a[i] = val
    def pointAssign(self, i, val):
        self.clock += 1
        self.t[self.size + i - self.lo] = (self.clock, val)

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
