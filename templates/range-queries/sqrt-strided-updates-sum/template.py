# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-strided-updates-sum/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet stridedSum
# @data-structure-type: sqrt
# @complexities:
#   getAll: N
#   pointAdd: 1*sqrt(N)
#   pointAssign: 1*sqrt(N)
#   pointChmax: 1*sqrt(N)
#   pointChmin: 1*sqrt(N)
#   pointGet: 1
#   stridedSum: sqrt(N)
#   build: 1*N*sqrt(N)
# @memory:
#   layout: none
#   node: sumBlocks[1*N]
#   tags: none
#   other: A[1*N] offsets[1*N]
#   note: one list per stride, in which a strided query is a contiguous range. Kept strides are lower than the costs suggest (an eighth for block sums, a quarter for seg trees), since slices walk the big steps fast

# Strided queries with point updates: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
# (the last position used may be below r). Fix a stride and split the array by position mod stride: a strided query
# is a contiguous range of one list, so small strides are ordinary range queries, and a big stride visits few
# positions, so it walks them. All indices 0-based, ranges inclusive.
# T: int, long long, ...; sums are kept in S (long long for small T).
from math import sqrt


class StridedQueries:
    # O(build) -- arr: the initial array
    def __init__(self, arr):
        self.A = A = list(arr)
        self.n = n = len(A)
        self.blockStrides = self.treeStrides = 0
        self.blockSize = blockSize = max(1, min(n, int(sqrt(n))))
        self.blockStrides = max(1, min(n, int(sqrt(n)) // 8))  # (slices walk big steps fast; every stride kept slows updates)
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
        self.sumBlocks = [None] + [[sum(lists[step][k:k + blockSize]) for k in range(0, n, blockSize)] + [0] for step in range(1, self.blockStrides + 1)]

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

    # a[l] + a[l + step] + ..., up to at most r; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedSum(self, l, r, step):
        if l < 0 or l > r or r >= self.n or step < 1:
            raise IndexError(f"stridedSum: needs 0 <= l <= r < n and step >= 1, got l={l}, r={r}, step={step}, n={self.n}")
        last = l + (r - l) // step * step
        if step > self.blockStrides:
            return sum(self.A[l:last + 1:step])
        blockSize, A = self.blockSize, self.A
        starts = self.offsets[step]
        first = starts[l % step] + l // step
        final = starts[last % step] + last // step
        firstBlock, lastBlock = first // blockSize, final // blockSize
        if firstBlock == lastBlock:
            return sum(self.A[l:last + 1:step])
        leftEnd = l + ((firstBlock + 1) * blockSize - first) * step
        rightStart = last - (final - lastBlock * blockSize) * step
        middle = self.sumBlocks[step][firstBlock + 1:lastBlock]
        return sum(A[l:leftEnd:step]) + sum(middle) + sum(A[rightStart:last + 1:step])

    # ---- internals ----

    def _write(self, i, v):
        A, n, offsets = self.A, self.n, self.offsets
        sumDelta = v - A[i]
        A[i] = v
        blockSize = self.blockSize
        for step in range(1, self.blockStrides + 1):
            block = (offsets[step][i % step] + i // step) // blockSize
            self.sumBlocks[step][block] += sumDelta
