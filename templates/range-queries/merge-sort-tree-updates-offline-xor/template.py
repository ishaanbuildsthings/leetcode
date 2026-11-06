# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/merge-sort-tree-updates-offline-xor/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX getAll largestLtX largestLteX pointAssign pointGet smallestGtX smallestGteX xorGtX xorGteX xorInValRange xorLtX xorLteX
# @data-structure-type: merge-sort-tree
# @fractional-cascading: no
# @values: offline
# @complexities:
#   countGtX: log^2(N)
#   countGteX: log^2(N)
#   countInValRange: log^2(N)
#   countLtX: log^2(N)
#   countLteX: log^2(N)
#   getAll: N
#   largestLtX: log^2(N)
#   largestLteX: log^2(N)
#   pointAssign: log^2(N)
#   pointGet: 1
#   smallestGtX: log^2(N)
#   smallestGteX: log^2(N)
#   xorGtX: log^2(N)
#   xorGteX: log^2(N)
#   xorInValRange: log^2(N)
#   xorLtX: log^2(N)
#   xorLteX: log^2(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: vals[1*N*log(N)] counts[1*N*log(N)] xors[1*N*log(N)]
#   tags: none
#   other: A[1*N] xorTotal[2*N] start[1*N] nodeSize[2*N]
#   note: the constructor takes every (i, v) a pointAssign will ever use, so N is the array length plus that list's length; worst-case bounds and flat arrays, the fastest of these

# Merge sort tree with point updates: a segment tree over positions (bottom-up: node p >= n is a[p - n]), each
# inner node keeping its positions' values in a searchable structure (the sorted values its positions can ever hold, with Fenwick trees over them). a[l..r] is O(log n) nodes, and a
# point update changes one value in each of the O(log n) nodes above it. All indices 0-based, ranges inclusive.
# Offline: the constructor takes every (i, v) that a pointAssign will ever use (read every query first). For adds
# or chmax / chmin, work out the new value yourself and list that.
# T: int, long long, ...; sums are kept in S (long long for small T).

from bisect import bisect_left, bisect_right


class MergeSortTreeOffline:
    # O(build) -- arr: the initial array. updates: every (i, v) that pointAssign will ever be called with (any order,
    # repeats fine); a pointAssign with a pair not listed raises ValueError
    def __init__(self, arr, updates):
        self.A = A = list(arr)
        self.n = n = len(A)
        possible = [None] * n + [[v] for v in A]  # node p's possible values, sorted, distinct
        for i, v in updates:
            if i < 0 or i >= n:
                raise IndexError(f"MergeSortTreeOffline: every listed update needs 0 <= i < n, got i={i}, n={n}")
            possible[n + i].append(v)
        copiesNow = [None] * (2 * n)  # and how many positions under p hold each right now
        for i in range(n):
            here = sorted(set(possible[n + i]))
            possible[n + i] = here
            row = [0] * len(here)
            row[bisect_left(here, A[i])] = 1
            copiesNow[n + i] = row
        self.nodeSize = nodeSize = [1] * (2 * n)
        self.vals, self.counts = [None] * n, [None] * n
        self.xors = [None] * n
        for p in range(n - 1, 0, -1):
            nodeSize[p] = nodeSize[2 * p] + nodeSize[2 * p + 1]
            merged = {}
            for side in (2 * p, 2 * p + 1):
                for v, c in zip(possible[side], copiesNow[side]):
                    merged[v] = merged.get(v, 0) + c
            vals = sorted(merged)
            row = [merged[v] for v in vals]
            possible[p], copiesNow[p] = vals, row
            if 2 * p >= n:
                possible[2 * p] = copiesNow[2 * p] = None
            if 2 * p + 1 >= n:
                possible[2 * p + 1] = copiesNow[2 * p + 1] = None
            size = len(vals)
            self.vals[p] = vals
            self.counts[p] = self._fenwick([0] + row, size, False)
            self.xors[p] = self._fenwick([0] + [v if c & 1 else 0 for v, c in zip(vals, row)], size, True)
        for p in range(1, n):
            if 2 * p < n:
                possible[2 * p] = copiesNow[2 * p] = None
        self.xorTotal = xorTotal = [0] * n + list(A)
        for p in range(n - 1, 0, -1):
            xorTotal[p] = xorTotal[2 * p] ^ xorTotal[2 * p + 1]

    # O(n) -- the whole array
    def getAll(self):
        return list(self.A)

    # O(1) -- a[i]; needs 0 <= i < n, else raises IndexError
    def pointGet(self, i):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i={i}, n={self.n}")
        return self.A[i]

    # O(log^2(N)) -- a[i] = v (overwrite); needs 0 <= i < n, else raises IndexError, and (i, v) listed in the
    # constructor's updates (or v == a[i]), else raises ValueError
    def pointAssign(self, i, v):
        n = self.n
        if i < 0 or i >= n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i={i}, n={n}")
        old = self.A[i]
        if old == v:
            return
        if n > 1 and not self._listed((i + n) >> 1, v):
            raise ValueError(f"pointAssign: ({i}, {v}) was not in the constructor's updates")
        p = (i + n) >> 1
        while p:
            self._add(p, old, -1)
            self._add(p, v, 1)
            self.xorTotal[p] ^= old ^ v
            p >>= 1
        self.A[i] = v

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

    # O(log^2(N)) -- # of i in [l, r] with lowVal <= a[i] <= highVal (0 if lowVal > highVal); needs 0 <= l <= r < n, else raises IndexError
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

    # O(log^2(N)) -- xor of a[i] < x in [l, r]; needs 0 <= l <= r < n, else raises IndexError
    def xorLtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"xorLtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._xorLess(l, r, x, True)

    # O(log^2(N)) -- xor of a[i] <= x in [l, r]; needs 0 <= l <= r < n, else raises IndexError
    def xorLteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"xorLteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._xorLess(l, r, x, False)

    # O(log^2(N)) -- xor of a[i] > x in [l, r]; needs 0 <= l <= r < n, else raises IndexError
    def xorGtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"xorGtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._xorAll(l, r) ^ self._xorLess(l, r, x, False)

    # O(log^2(N)) -- xor of a[i] >= x in [l, r]; needs 0 <= l <= r < n, else raises IndexError
    def xorGteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"xorGteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._xorAll(l, r) ^ self._xorLess(l, r, x, True)

    # O(log^2(N)) -- xor of a[i] with lowVal <= a[i] <= highVal in [l, r] (0 if lowVal > highVal); needs 0 <= l <= r < n, else raises IndexError
    def xorInValRange(self, l, r, lowVal, highVal):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"xorInValRange: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        if lowVal > highVal:
            return 0
        return self._xorLess(l, r, highVal, False) ^ self._xorLess(l, r, lowVal, True)

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

    def _xorLess(self, l, r, x, strict):
        n, A, res = self.n, self.A, 0
        for p in self._nodes(l, r):
            if p >= n:
                v = A[p - n]
                if (v < x) if strict else (v <= x):
                    res ^= v
            else:
                res ^= self._xorBelow(p, x, strict)
        return res

    def _xorAll(self, l, r):
        n, A, res, xorTotal = self.n, self.A, 0, self.xorTotal
        for p in self._nodes(l, r):
            res ^= A[p - n] if p >= n else xorTotal[p]
        return res

    @staticmethod
    def _fenwick(f, size, isXor):  # f[1..size] raw values -> a Fenwick tree in O(size)
        for j in range(1, size + 1):
            up = j + (j & -j)
            if up <= size:
                if isXor:
                    f[up] ^= f[j]
                else:
                    f[up] += f[j]
        return f

    def _listed(self, p, v):
        vals = self.vals[p]
        k = bisect_left(vals, v)
        return k < len(vals) and vals[k] == v

    def _add(self, p, v, delta):
        counts = self.counts[p]
        xors = self.xors[p]
        size = len(self.vals[p])
        j = bisect_left(self.vals[p], v) + 1
        while j <= size:
            counts[j] += delta
            xors[j] ^= v
            j += j & -j

    def _countBelow(self, p, x, strict):  # over node p's values < x (strict) or <= x
        f, res = self.counts[p], 0
        j = bisect_left(self.vals[p], x) if strict else bisect_right(self.vals[p], x)
        while j:
            res += f[j]
            j &= j - 1
        return res

    def _xorBelow(self, p, x, strict):  # over node p's values < x (strict) or <= x
        f, res = self.xors[p], 0
        j = bisect_left(self.vals[p], x) if strict else bisect_right(self.vals[p], x)
        while j:
            res ^= f[j]
            j &= j - 1
        return res

    def _kth(self, p, k):  # node p's k-th smallest value (1-indexed; 1 <= k <= nodeSize[p])
        f, size, pos = self.counts[p], len(self.vals[p]), 0
        step = 1 << (size.bit_length() - 1) if size else 0
        while step:
            if pos + step <= size and f[pos + step] < k:
                pos += step
                k -= f[pos]
            step >>= 1
        return self.vals[p][pos]

    def _firstIn(self, p, x, strict):  # smallest value > x (strict) or >= x in node p
        below = self._countBelow(p, x, not strict)
        return None if below >= self.nodeSize[p] else self._kth(p, below + 1)

    def _lastIn(self, p, x, strict):  # largest value < x (strict) or <= x in node p
        below = self._countBelow(p, x, strict)
        return self._kth(p, below) if below else None
