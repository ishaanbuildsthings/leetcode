# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-add/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet stridedAdd
# @data-structure-type: sqrt
# @complexities:
#   getAll: N*sqrt(NlogN)
#   pointAdd: 1
#   pointAssign: sqrt(NlogN)
#   pointChmax: sqrt(NlogN)
#   pointChmin: sqrt(NlogN)
#   pointGet: sqrt(NlogN)
#   stridedAdd: sqrt(NlogN)
#   build: N*sqrt(N/logN)
# @memory:
#   layout: none
#   node: diffs[1*N*sqrt(N/logN)]
#   tags: none
#   other: A[1*N] offsets[1*N]
#   note: a small step is a range add on that step's Fenwick tree of differences, a big step walks its positions, and a point read adds up every small step

# Strided add with point reads and writes: stridedAdd(l, r, step, v) adds v to a[l], a[l + step], ... up to at most r
# (the last position used may be below r). A strided sum on top of this has no good bound: two different steps
# overlap in a pattern that depends on both. All indices 0-based, ranges inclusive.
from math import log2, sqrt


class StridedQueries:
    # O(build) -- arr: the initial array. cutoff: a Fenwick tree is kept for steps up to it (more memory and slower
    # reads, faster big-step adds); leave it out for a quarter of sqrt(n / log n)
    def __init__(self, arr, cutoff=None):
        self.A = list(arr)
        self.n = n = len(self.A)
        self.strides = cutoff if cutoff is not None else max(1, min(n, int(sqrt(n / max(1.0, log2(n + 1)))) // 4))
        if not 0 <= self.strides <= n:
            raise IndexError(f"StridedQueries: needs 0 <= cutoff <= n, got cutoff={cutoff}, n={n}")
        # offsets[step][residue]: where that residue class starts in that stride's list
        self.offsets = [None] * (self.strides + 1)
        for step in range(1, self.strides + 1):
            used, starts = 0, [0] * step
            for residue in range(step):
                starts[residue] = used
                if residue < n:
                    used += (n - residue + step - 1) // step
            self.offsets[step] = starts
        self.diffs = [None] + [[0] * (n + 2) for _ in range(self.strides)]  # one Fenwick tree of differences per kept step

    # a[l] += v, a[l + step] += v, ... up to at most r; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedAdd(self, l, r, step, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedAdd: needs step >= 1, got step = {step}")
        last = l + (r - l) // step * step
        if step > self.strides:
            A = self.A
            for i in range(l, last + 1, step):
                A[i] += v
            return
        starts = self.offsets[step]
        self._addDiff(step, starts[l % step] + l // step, v)
        self._addDiff(step, starts[last % step] + last // step + 1, -v)

    # the current a[i]; needs 0 <= i < n, else raises IndexError
    def pointGet(self, i):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i={i}, n={self.n}")
        res = self.A[i]
        offsets, diffs = self.offsets, self.diffs
        for step in range(1, self.strides + 1):
            tree = diffs[step]
            node = offsets[step][i % step] + i // step + 1
            while node:
                res += tree[node]
                node &= node - 1
        return res

    # a[i] += v; needs 0 <= i < n, else raises IndexError
    def pointAdd(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i={i}, n={self.n}")
        self.A[i] += v

    # a[i] = v (overwrite); needs 0 <= i < n, else raises IndexError
    def pointAssign(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i={i}, n={self.n}")
        self.A[i] += v - self.pointGet(i)

    # a[i] = max(a[i], v); needs 0 <= i < n, else raises IndexError
    def pointChmax(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i={i}, n={self.n}")
        current = self.pointGet(i)
        if v > current:
            self.A[i] += v - current

    # a[i] = min(a[i], v); needs 0 <= i < n, else raises IndexError
    def pointChmin(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i={i}, n={self.n}")
        current = self.pointGet(i)
        if v < current:
            self.A[i] += v - current

    # the whole array
    def getAll(self):
        return [self.pointGet(i) for i in range(self.n)]

    # ---- internals ----

    def _addDiff(self, step, index, v):
        tree = self.diffs[step]
        node = index + 1
        limit = self.n + 1
        while node <= limit:
            tree[node] += v
            node += node & -node
