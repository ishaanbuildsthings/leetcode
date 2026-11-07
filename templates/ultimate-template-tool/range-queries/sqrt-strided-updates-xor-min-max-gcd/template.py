# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-updates-xor-min-max-gcd/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet stridedGcd stridedMax stridedMin stridedXorQuery
# @data-structure-type: sqrt
# @complexities:
#   getAll: N
#   pointAdd: 1*sqrt(N)+3*sqrt(NlogN)+sqrt(N/logN)*log(U) ?
#   pointAssign: 1*sqrt(N)+3*sqrt(NlogN)+sqrt(N/logN)*log(U) ?
#   pointChmax: 1*sqrt(N)+3*sqrt(NlogN)+sqrt(N/logN)*log(U) ?
#   pointChmin: 1*sqrt(N)+3*sqrt(NlogN)+sqrt(N/logN)*log(U) ?
#   pointGet: 1
#   stridedGcd: sqrt(NlogN)+log(U) ?
#   stridedMax: sqrt(NlogN)
#   stridedMin: sqrt(NlogN)
#   stridedXorQuery: sqrt(N)
#   build: 1*N*sqrt(N)+6*N*sqrt(N/logN)+N*sqrt(N/logN)*log(U) ?
# @memory:
#   layout: none
#   node: xorBlocks[1*N] minTree[2*N*sqrt(N/logN)] maxTree[2*N*sqrt(N/logN)] gcdTree[2*N*sqrt(N/logN)]
#   tags: none
#   other: A[1*N] offsets[1*N]
#   note: one list per stride, in which a strided query is a contiguous range. Kept strides are lower than the costs suggest (an eighth for block sums, a quarter for seg trees), since slices walk the big steps fast

# Strided queries with point updates: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
# (the last position used may be below r). Fix a stride and split the array by position mod stride: a strided query
# is a contiguous range of one list, so small strides are ordinary range queries, and a big stride visits few
# positions, so it walks them. All indices 0-based, ranges inclusive.
# T: int, long long, ...; sums are kept in S (long long for small T).
from functools import reduce
from math import gcd, log2, sqrt
from operator import xor


class StridedQueries:
    # O(build) -- arr: the initial array. cutoff: seg trees are kept for steps up to it (more memory and slower
    # updates, faster big-step queries); leave it out for a quarter of sqrt(n / log n)
    def __init__(self, arr, cutoff=None):
        self.A = A = list(arr)
        self.n = n = len(A)
        self.blockStrides = self.treeStrides = 0
        self.blockSize = blockSize = max(1, min(n, int(sqrt(n))))
        self.blockStrides = max(1, min(n, int(sqrt(n)) // 8))  # (slices walk big steps fast; every stride kept slows updates)
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
        self.xorBlocks = [None] + [[reduce(xor, lists[step][k:k + blockSize]) for k in range(0, n, blockSize)] + [0] for step in range(1, self.blockStrides + 1)]
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
        trees["gcd"] = [None] * (self.treeStrides + 1)
        for step in range(1, self.treeStrides + 1):
            tree = [0] * n + lists[step]
            high = n
            while high > 1:  # (level by level: map is much faster than a loop over the nodes)
                low = (high + 1) // 2
                tree[low:high] = list(map(gcd, tree[2 * low:2 * high:2], tree[2 * low + 1:2 * high:2]))
                high = low
            trees["gcd"][step] = tree
        self.minTree = trees["min"]
        self.maxTree = trees["max"]
        self.gcdTree = trees["gcd"]

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

    # a[l] ^ a[l + step] ^ ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedXorQuery(self, l, r, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedXorQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedXorQuery: needs step >= 1, got step = {step}")
        last = l + (r - l) // step * step
        if step > self.blockStrides:
            return reduce(xor, self.A[l:last + 1:step])
        blockSize, A = self.blockSize, self.A
        starts = self.offsets[step]
        first = starts[l % step] + l // step
        final = starts[last % step] + last // step
        firstBlock, lastBlock = first // blockSize, final // blockSize
        if firstBlock == lastBlock:
            return reduce(xor, self.A[l:last + 1:step])
        leftEnd = l + ((firstBlock + 1) * blockSize - first) * step
        rightStart = last - (final - lastBlock * blockSize) * step
        middle = self.xorBlocks[step][firstBlock + 1:lastBlock]
        return reduce(xor, A[l:leftEnd:step], 0) ^ reduce(xor, middle, 0) ^ reduce(xor, A[rightStart:last + 1:step], 0)

    # min of a[l], a[l + step], ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedMin(self, l, r, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedMin: needs step >= 1, got step = {step}")
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
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedMax: needs step >= 1, got step = {step}")
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

    # gcd of a[l], a[l + step], ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedGcd(self, l, r, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedGcd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedGcd: needs step >= 1, got step = {step}")
        last = l + (r - l) // step * step
        if step > self.treeStrides:
            return gcd(*self.A[l:last + 1:step])
        starts, tree = self.offsets[step], self.gcdTree[step]
        n = self.n
        low = n + starts[l % step] + l // step
        high = n + starts[last % step] + last // step + 1
        res = self.A[l]  # (every aggregate here keeps a value it has already seen)
        while low < high:
            if low & 1:
                v = tree[low]
                res = gcd(res, v)
                low += 1
            if high & 1:
                high -= 1
                v = tree[high]
                res = gcd(res, v)
            low >>= 1
            high >>= 1
        return res

    # ---- internals ----

    def _write(self, i, v):
        A, n, offsets = self.A, self.n, self.offsets
        xorDelta = A[i] ^ v
        A[i] = v
        blockSize = self.blockSize
        for step in range(1, self.blockStrides + 1):
            block = (offsets[step][i % step] + i // step) // blockSize
            self.xorBlocks[step][block] ^= xorDelta
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
            tree = self.gcdTree[step]
            tree[leaf] = v
            node = leaf >> 1
            while node:
                a, b = tree[2 * node], tree[2 * node + 1]
                merged = gcd(a, b)
                if merged == tree[node]:
                    break  # (nothing above can change either)
                tree[node] = merged
                node >>= 1
