# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/merge-sort-tree-updates-sortedlist/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX getAll largestLtX largestLteX pointAdd pointAssign pointChmax pointChmin pointGet smallestGtX smallestGteX
# @data-structure-type: merge-sort-tree
# @fractional-cascading: no
# @complexities:
#   countGtX: log^2(N)
#   countGteX: log^2(N)
#   countInValRange: log^2(N)
#   countLtX: log^2(N)
#   countLteX: log^2(N)
#   getAll: N
#   largestLtX: log^2(N)
#   largestLteX: log^2(N)
#   pointAdd: log^2(N) amortized
#   pointAssign: log^2(N) amortized
#   pointChmax: log^2(N) amortized
#   pointChmin: log^2(N) amortized
#   pointGet: 1
#   smallestGtX: log^2(N)
#   smallestGteX: log^2(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: vals[1*N*log(N)]
#   tags: none
#   other: A[1*N]
#   note: no value range and nothing up front; buckets hold 256 to 512 values, so an update also moves up to 512 values in each of its log N nodes

# Merge sort tree with point updates: a segment tree over positions (bottom-up: node p >= n is a[p - n]), each
# inner node keeping its positions' values in a searchable structure (sorted buckets of 256 to 512 values, with a
# Fenwick tree over the bucket sizes). a[l..r] is O(log n) nodes, and a
# point update changes one value in each of the O(log n) nodes above it. All indices 0-based, ranges inclusive.
# Counts and nearest values only: sums and xors need the treap or offline versions.
# T: int, long long, ...; sums are kept in S (long long for small T).

from bisect import bisect_left, bisect_right, insort


class MergeSortTreeUpdates:
    LOAD = 256  # buckets hold LOAD to 2 * LOAD values

    # O(build) -- arr: the initial array
    def __init__(self, arr):
        self.A = A = list(arr)
        self.n = n = len(A)
        self.nodeSize = nodeSize = [1] * (2 * n)
        for p in range(n - 1, 0, -1):
            nodeSize[p] = nodeSize[2 * p] + nodeSize[2 * p + 1]
        self.buckets, self.maxes, self.sizes = [None] * n, [None] * n, [None] * n
        sortedVals = [None] * n + [[v] for v in A]  # node p's values, sorted (dropped once its parent has them)
        for p in range(n - 1, 0, -1):
            vals = sortedVals[2 * p] + sortedVals[2 * p + 1]
            vals.sort()  # (two sorted runs: timsort merges them in linear time)
            sortedVals[2 * p] = sortedVals[2 * p + 1] = None
            sortedVals[p] = vals
            self.buckets[p] = [vals[k:k + self.LOAD] for k in range(0, len(vals), self.LOAD)]
            self._reindex(p)

    # O(n) -- the whole array
    def getAll(self):
        return list(self.A)

    # O(1) -- a[i]; needs 0 <= i < n, else raises IndexError
    def pointGet(self, i):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i={i}, n={self.n}")
        return self.A[i]

    # O(log^2(N) amortized) -- a[i] = v (overwrite); needs 0 <= i < n, else raises IndexError
    def pointAssign(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, v)

    # O(log^2(N) amortized) -- a[i] += v; needs 0 <= i < n, else raises IndexError
    def pointAdd(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, self.A[i] + v)

    # O(log^2(N) amortized) -- a[i] = max(a[i], v); needs 0 <= i < n, else raises IndexError
    def pointChmax(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, max(self.A[i], v))

    # O(log^2(N) amortized) -- a[i] = min(a[i], v); needs 0 <= i < n, else raises IndexError
    def pointChmin(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, min(self.A[i], v))

    # O(log^2(N)) -- # of i in [l, r] with a[i] < x; needs 0 <= l <= r < n, else raises IndexError
    def countLtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"countLtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._countLess(l, r, x, True)

    # O(log^2(N)) -- # of i in [l, r] with a[i] <= x; needs 0 <= l <= r < n, else raises IndexError
    def countLteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"countLteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._countLess(l, r, x, False)

    # O(log^2(N)) -- # of i in [l, r] with a[i] > x; needs 0 <= l <= r < n, else raises IndexError
    def countGtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"countGtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return (r - l + 1) - self._countLess(l, r, x, False)

    # O(log^2(N)) -- # of i in [l, r] with a[i] >= x; needs 0 <= l <= r < n, else raises IndexError
    def countGteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"countGteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return (r - l + 1) - self._countLess(l, r, x, True)

    # O(log^2(N)) -- # of i in [l, r] with lowVal <= a[i] <= highVal (0 if lowVal > highVal); needs 0 <= l <= r < n,
    # else raises IndexError
    def countInValRange(self, l, r, lowVal, highVal):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"countInValRange: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        if lowVal > highVal:
            return 0
        return self._countLess(l, r, highVal, False) - self._countLess(l, r, lowVal, True)

    # O(log^2(N)) -- smallest a[i] >= x in [l, r]; None if there is none; needs 0 <= l <= r < n, else raises IndexError
    def smallestGteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"smallestGteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._firstAtLeast(l, r, x, False)

    # O(log^2(N)) -- smallest a[i] > x in [l, r]; None if there is none; needs 0 <= l <= r < n, else raises IndexError
    def smallestGtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"smallestGtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._firstAtLeast(l, r, x, True)

    # O(log^2(N)) -- largest a[i] <= x in [l, r]; None if there is none; needs 0 <= l <= r < n, else raises IndexError
    def largestLteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"largestLteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._lastBelow(l, r, x, False)

    # O(log^2(N)) -- largest a[i] < x in [l, r]; None if there is none; needs 0 <= l <= r < n, else raises IndexError
    def largestLtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"largestLtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._lastBelow(l, r, x, True)

    # ---- internals ----

    def _nodes(self, l, r):  # the O(log n) nodes that cover a[l..r]
        n = self.n
        l += n
        r += n + 1
        out = []
        while l < r:
            if l & 1:
                out.append(l)
                l += 1
            if r & 1:
                r -= 1
                out.append(r)
            l >>= 1
            r >>= 1
        return out

    def _countLess(self, l, r, x, strict):  # number of values < x (strict) or <= x in a[l..r]
        n, A, res = self.n, self.A, 0
        for p in self._nodes(l, r):
            if p >= n:
                v = A[p - n]
                res += (v < x) if strict else (v <= x)
            else:
                res += self._countBelow(p, x, strict)
        return res

    def _firstAtLeast(self, l, r, x, strict):  # smallest value > x (strict) or >= x
        n, A, best = self.n, self.A, None
        for p in self._nodes(l, r):
            if p >= n:
                v = A[p - n]
                got = v if ((v > x) if strict else (v >= x)) else None
            else:
                got = self._firstIn(p, x, strict)
            if got is not None and (best is None or got < best):
                best = got
        return best

    def _lastBelow(self, l, r, x, strict):  # largest value < x (strict) or <= x
        n, A, best = self.n, self.A, None
        for p in self._nodes(l, r):
            if p >= n:
                v = A[p - n]
                got = v if ((v < x) if strict else (v <= x)) else None
            else:
                got = self._lastIn(p, x, strict)
            if got is not None and (best is None or got > best):
                best = got
        return best

    def _write(self, i, v):
        old = self.A[i]
        if old == v:
            return
        p = (i + self.n) >> 1
        while p:
            self._erase(p, old)
            self._insert(p, v)
            p >>= 1
        self.A[i] = v

    def _reindex(self, p):  # maxes and the size Fenwick tree of node p, from its buckets
        bs = self.buckets[p]
        self.maxes[p] = [b[-1] for b in bs]
        count = len(bs)
        f = [0] * (count + 1)
        for j in range(1, count + 1):
            f[j] += len(bs[j - 1])
            up = j + (j & -j)
            if up <= count:
                f[up] += f[j]
        self.sizes[p] = f

    def _before(self, p, b):  # number of node p's values in its buckets 0 .. b - 1
        f, res = self.sizes[p], 0
        while b:
            res += f[b]
            b &= b - 1
        return res

    def _countBelow(self, p, x, strict):
        m = self.maxes[p]
        b = bisect_left(m, x) if strict else bisect_right(m, x)
        if b == len(m):
            return self.nodeSize[p]
        bucket = self.buckets[p][b]
        return self._before(p, b) + (bisect_left(bucket, x) if strict else bisect_right(bucket, x))

    def _firstIn(self, p, x, strict):  # smallest value > x (strict) or >= x in node p
        m = self.maxes[p]
        b = bisect_right(m, x) if strict else bisect_left(m, x)
        if b == len(m):
            return None
        bucket = self.buckets[p][b]
        return bucket[bisect_right(bucket, x) if strict else bisect_left(bucket, x)]

    def _lastIn(self, p, x, strict):  # largest value < x (strict) or <= x in node p
        m = self.maxes[p]
        b = bisect_left(m, x) if strict else bisect_right(m, x)
        if b < len(m):
            bucket = self.buckets[p][b]
            k = bisect_left(bucket, x) if strict else bisect_right(bucket, x)
            if k:
                return bucket[k - 1]
        return self.buckets[p][b - 1][-1] if b else None

    def _insert(self, p, v):
        bs, m = self.buckets[p], self.maxes[p]
        b = bisect_left(m, v)
        if b == len(bs):
            b -= 1
        bucket = bs[b]
        insort(bucket, v)
        if len(bucket) > 2 * self.LOAD:  # split it in two
            bs[b:b + 1] = [bucket[:self.LOAD], bucket[self.LOAD:]]
            self._reindex(p)
        else:
            m[b] = bucket[-1]
            f, j, count = self.sizes[p], b + 1, len(bs)
            while j <= count:
                f[j] += 1
                j += j & -j

    def _erase(self, p, v):  # v is in node p
        bs, m = self.buckets[p], self.maxes[p]
        b = bisect_left(m, v)
        bucket = bs[b]
        del bucket[bisect_left(bucket, v)]
        if not bucket:
            del bs[b]
            self._reindex(p)
        else:
            m[b] = bucket[-1]
            f, j, count = self.sizes[p], b + 1, len(bs)
            while j <= count:
                f[j] -= 1
                j += j & -j
