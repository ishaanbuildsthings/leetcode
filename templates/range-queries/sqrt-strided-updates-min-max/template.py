# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-strided-updates-min-max/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet stridedMax stridedMin
# @data-structure-type: sqrt
# @complexities:
#   getAll: N
#   pointAdd: 2*sqrt(NlogN)
#   pointAssign: 2*sqrt(NlogN)
#   pointChmax: 2*sqrt(NlogN)
#   pointChmin: 2*sqrt(NlogN)
#   pointGet: 1
#   stridedMax: sqrt(NlogN)
#   stridedMin: sqrt(NlogN)
#   build: 4*N*sqrt(N/logN)
# @memory:
#   layout: none
#   node: minTree[2*N*sqrt(N/logN)] maxTree[2*N*sqrt(N/logN)]
#   tags: none
#   other: A[1*N] offsets[1*N]
#   note: one list per stride, in which a strided query is a contiguous range. Kept strides are lower than the costs suggest (an eighth for block sums, a quarter for seg trees), since slices walk the big steps fast

# Strided queries with point updates: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
# (the last position used may be below r). Fix a stride and split the array by position mod stride: a strided query
# is a contiguous range of one list, so small strides are ordinary range queries, and a big stride visits few
# positions, so it walks them. All indices 0-based, ranges inclusive.
# T: int, long long, ...; sums are kept in S (long long for small T).
from math import log2, sqrt


class StridedQueries:
    # O(build) -- arr: the initial array. cutoff: seg trees are kept for steps up to it (more memory and slower
    # updates, faster big-step queries); leave it out for a quarter of sqrt(n / log n)
    def __init__(self, arr, cutoff=None):
        self.A = A = list(arr)
        self.n = n = len(A)
        self.blockStrides = self.treeStrides = 0
        self.treeStrides = cutoff if cutoff is not None else max(1, min(n, int(sqrt(n / max(1.0, log2(n + 1)))) // 4))
        if not 0 <= self.treeStrides <= n:
            raise IndexError(f"StridedQueries: needs 0 <= cutoff <= n, got cutoff={cutoff}, n={n}")
        strides = max(self.blockStrides, self.treeStrides)
        # offsets[step][residue]: where that residue class starts in that stride's list
        self.offsets = [None] * (strides + 1)
        lists = [None] * (strides + 1)
        for step in range(1, strides + 1):
            used, starts, parts = 0, [0] * step, []
            for residue in range(step):
                starts[residue] = used
                parts.extend(A[residue::step])
                if residue < n:
                    used += (n - residue + step - 1) // step
            self.offsets[step] = starts
            lists[step] = parts
        self.trees = trees = {}
        trees["min"] = [None] * (self.treeStrides + 1)
        for step in range(1, self.treeStrides + 1):
            tree = [0] * n + lists[step]
            high = n
            while high > 1:  # (level by level: map is much faster than a loop over the nodes)
                low = (high + 1) // 2
                tree[low:high] = list(map(min, tree[2 * low:2 * high:2], tree[2 * low + 1:2 * high:2]))
                high = low
            trees["min"][step] = tree
        trees["max"] = [None] * (self.treeStrides + 1)
        for step in range(1, self.treeStrides + 1):
            tree = [0] * n + lists[step]
            high = n
            while high > 1:  # (level by level: map is much faster than a loop over the nodes)
                low = (high + 1) // 2
                tree[low:high] = list(map(max, tree[2 * low:2 * high:2], tree[2 * low + 1:2 * high:2]))
                high = low
            trees["max"][step] = tree
        self.minTree = trees["min"]
        self.maxTree = trees["max"]

    # O(n) -- the whole array
    def getAll(self):
        return list(self.A)

    # O(1) -- a[i]; needs 0 <= i < n, else raises IndexError
    def pointGet(self, i):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i={i}, n={self.n}")
        return self.A[i]

    # a[i] = v (overwrite); needs 0 <= i < n, else raises IndexError
    def pointAssign(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, v)

    # a[i] += v; needs 0 <= i < n, else raises IndexError
    def pointAdd(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, self.A[i] + v)

    # a[i] = max(a[i], v); needs 0 <= i < n, else raises IndexError
    def pointChmax(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, max(self.A[i], v))

    # a[i] = min(a[i], v); needs 0 <= i < n, else raises IndexError
    def pointChmin(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, min(self.A[i], v))

    # min of a[l], a[l + step], ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedMin(self, l, r, step):
        if l < 0 or l > r or r >= self.n or step < 1:
            raise IndexError(f"stridedMin: needs 0 <= l <= r < n and step >= 1, got l={l}, r={r}, step={step}, n={self.n}")
        last = l + (r - l) // step * step
        if step > self.treeStrides:
            return min(self.A[l:last + 1:step])
        starts, tree = self.offsets[step], self.minTree[step]
        n = self.n
        low = n + starts[l % step] + l // step
        high = n + starts[last % step] + last // step + 1
        res = self.A[l]  # (every aggregate here keeps a value it has already seen)
        while low < high:
            if low & 1:
                v = tree[low]
                res = res if res < v else v
                low += 1
            if high & 1:
                high -= 1
                v = tree[high]
                res = res if res < v else v
            low >>= 1
            high >>= 1
        return res

    # max of a[l], a[l + step], ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedMax(self, l, r, step):
        if l < 0 or l > r or r >= self.n or step < 1:
            raise IndexError(f"stridedMax: needs 0 <= l <= r < n and step >= 1, got l={l}, r={r}, step={step}, n={self.n}")
        last = l + (r - l) // step * step
        if step > self.treeStrides:
            return max(self.A[l:last + 1:step])
        starts, tree = self.offsets[step], self.maxTree[step]
        n = self.n
        low = n + starts[l % step] + l // step
        high = n + starts[last % step] + last // step + 1
        res = self.A[l]  # (every aggregate here keeps a value it has already seen)
        while low < high:
            if low & 1:
                v = tree[low]
                res = res if res > v else v
                low += 1
            if high & 1:
                high -= 1
                v = tree[high]
                res = res if res > v else v
            low >>= 1
            high >>= 1
        return res

    # ---- internals ----

    def _write(self, i, v):
        A, n, offsets = self.A, self.n, self.offsets
        A[i] = v
        for step in range(1, self.treeStrides + 1):
            leaf = n + offsets[step][i % step] + i // step
            tree = self.minTree[step]
            tree[leaf] = v
            node = leaf >> 1
            while node:
                a, b = tree[2 * node], tree[2 * node + 1]
                merged = a if a < b else b
                if merged == tree[node]:
                    break  # (nothing above can change either)
                tree[node] = merged
                node >>= 1
            tree = self.maxTree[step]
            tree[leaf] = v
            node = leaf >> 1
            while node:
                a, b = tree[2 * node], tree[2 * node + 1]
                merged = a if a > b else b
                if merged == tree[node]:
                    break  # (nothing above can change either)
                tree[node] = merged
                node >>= 1
