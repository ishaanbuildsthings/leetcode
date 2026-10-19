# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeMod
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeMod: log(U)*log(U) amortized
#   build: 1
# @memory:
#   layout: sparse
#   node: mx[1*log(U)]
#   tags: none
#   other: links[2*log(U)]
#   note: per point write, one node per level of its path (rangeMod creates nothing); rangeMod's second log is of the largest value. C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; Python: a dict keyed by heap index, a missing key is a block of zeros

# Range mod + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# Requires a[i] >= 0, mod >= 1. Mods don't compose into one tag, so rangeMod descends into every covering node
# whose max is still >= mod; each value that changes at least halves, so the work is amortized. Sparse: a dict
# keyed by heap index over a power-of-two cover of [lo, hi]; a missing node is all zeros, so rangeMod never
# enters one.


class SparseRangeModTree:
    __slots__ = ("lo", "size", "mx")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of i is size + (i - lo)
        self.mx = {}  # heap index -> max of the subtree (missing: 0)

    # O(logU) -- recompute the maxes on leaf p's root path
    def _pull(self, p):
        mx = self.mx
        p >>= 1
        while p:
            a = mx.get(2 * p, 0)
            b = mx.get(2 * p + 1, 0)
            mx[p] = a if a > b else b
            p >>= 1

    def _descend(self, top, mod):
        mx, size = self.mx, self.size
        stack, inner = [top], []
        while stack:
            y = stack.pop()
            if mx.get(y, 0) < mod:
                continue
            if y >= size:
                mx[y] %= mod
            else:
                inner.append(y)
                stack.append(2 * y)
                stack.append(2 * y + 1)
        for y in reversed(inner):  # pre-order reversed puts every child before its parent
            a = mx.get(2 * y, 0)
            b = mx.get(2 * y + 1, 0)
            mx[y] = a if a > b else b

    # amortized O(logU logV) -- a[i] %= mod for i in [l, r]
    def rangeMod(self, l, r, mod):
        if l > r:
            return
        l += self.size - self.lo
        r += self.size - self.lo
        lo, hi = l, r + 1
        while lo < hi:
            if lo & 1:
                self._descend(lo, mod)
                lo += 1
            if hi & 1:
                hi -= 1
                self._descend(hi, mod)
            lo >>= 1
            hi >>= 1
        self._pull(l)
        self._pull(r)

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.mx.get(self.size + i - self.lo, 0)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        p = self.size + i - self.lo
        self.mx[p] = val
        self._pull(p)

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
