# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/merge-sort-tree-updates-treap-sums/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX getAll largestLtX largestLteX pointAdd pointAssign pointChmax pointChmin pointGet smallestGtX smallestGteX sumAbsDiffToX sumGtX sumGteX sumInValRange sumLtX sumLteX
# @data-structure-type: merge-sort-tree
# @fractional-cascading: no
# @complexities:
#   countGtX: log^2(N) expected
#   countGteX: log^2(N) expected
#   countInValRange: log^2(N) expected
#   countLtX: log^2(N) expected
#   countLteX: log^2(N) expected
#   getAll: N
#   largestLtX: log^2(N) expected
#   largestLteX: log^2(N) expected
#   pointAdd: log^2(N) expected
#   pointAssign: log^2(N) expected
#   pointChmax: log^2(N) expected
#   pointChmin: log^2(N) expected
#   pointGet: 1
#   smallestGtX: log^2(N) expected
#   smallestGteX: log^2(N) expected
#   sumAbsDiffToX: log^2(N) expected
#   sumGtX: log^2(N) expected
#   sumGteX: log^2(N) expected
#   sumInValRange: log^2(N) expected
#   sumLtX: log^2(N) expected
#   sumLteX: log^2(N) expected
#   build: N*log(N)
# @memory:
#   layout: none
#   node: key[1*N*log(N)] copies[1*N*log(N)] under[1*N*log(N)] leftChild[1*N*log(N)] rightChild[1*N*log(N)] priority[1*N*log(N)] subSum[1*N*log(N)]
#   tags: none
#   other: A[1*N] total[2*N] root[1*N]
#   note: no value range and nothing up front; each update makes at most log N new treap nodes and none are reused, so N counts updates too

# Merge sort tree with point updates: a segment tree over positions (bottom-up: node p >= n is a[p - n]), each inner
# node keeping its positions' values in a searchable structure (a treap keyed by value, copies counted, with subtree
# sizes / sums / xors). a[l..r] is O(log n) nodes, and a point update changes one value in each of the O(log n) nodes
# above it. All indices 0-based, ranges inclusive.
# T: int, long long, ...; sums are kept in S (long long for small T).

from bisect import bisect_left, bisect_right
from random import random


class MergeSortTreeUpdates:
    # O(build) -- arr: the initial array
    def __init__(self, arr):
        self.A = A = list(arr)
        self.n = n = len(A)
        self.nodeSize = nodeSize = [1] * (2 * n)
        for p in range(n - 1, 0, -1):
            nodeSize[p] = nodeSize[2 * p] + nodeSize[2 * p + 1]
        self.key, self.copies, self.under, self.leftChild, self.rightChild, self.priority = [0], [0], [0], [0], [0], [0]
        self.subSum = [0]
        self.root = [0] * max(n, 1)
        sortedVals = [None] * n + [[v] for v in A]  # node p's values, sorted (dropped once its parent has them)
        for p in range(n - 1, 0, -1):
            vals = sortedVals[2 * p] + sortedVals[2 * p + 1]
            vals.sort()  # (two sorted runs: timsort merges them in linear time)
            sortedVals[2 * p] = sortedVals[2 * p + 1] = None
            sortedVals[p] = vals
            self.root[p] = self._buildTreap(vals)
        self.total = total = [0] * n + list(A)
        for p in range(n - 1, 0, -1):
            total[p] = total[2 * p] + total[2 * p + 1]

    # O(n) -- the whole array
    def getAll(self):
        return list(self.A)

    # O(1) -- a[i]; needs 0 <= i < n, else raises IndexError
    def pointGet(self, i):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i={i}, n={self.n}")
        return self.A[i]

    # O(log^2(N) expected) -- a[i] = v (overwrite); needs 0 <= i < n, else raises IndexError
    def pointAssign(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, v)

    # O(log^2(N) expected) -- a[i] += v; needs 0 <= i < n, else raises IndexError
    def pointAdd(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, self.A[i] + v)

    # O(log^2(N) expected) -- a[i] = max(a[i], v); needs 0 <= i < n, else raises IndexError
    def pointChmax(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, max(self.A[i], v))

    # O(log^2(N) expected) -- a[i] = min(a[i], v); needs 0 <= i < n, else raises IndexError
    def pointChmin(self, i, v):
        if i < 0 or i >= self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i={i}, n={self.n}")
        self._write(i, min(self.A[i], v))

    # O(log^2(N) expected) -- # of i in [l, r] with a[i] < x; needs 0 <= l <= r < n, else raises IndexError
    def countLtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"countLtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._countLess(l, r, x, True)

    # O(log^2(N) expected) -- # of i in [l, r] with a[i] <= x; needs 0 <= l <= r < n, else raises IndexError
    def countLteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"countLteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._countLess(l, r, x, False)

    # O(log^2(N) expected) -- # of i in [l, r] with a[i] > x; needs 0 <= l <= r < n, else raises IndexError
    def countGtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"countGtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return (r - l + 1) - self._countLess(l, r, x, False)

    # O(log^2(N) expected) -- # of i in [l, r] with a[i] >= x; needs 0 <= l <= r < n, else raises IndexError
    def countGteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"countGteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return (r - l + 1) - self._countLess(l, r, x, True)

    # O(log^2(N) expected) -- # of i in [l, r] with lowVal <= a[i] <= highVal (0 if lowVal > highVal); needs 0 <= l <= r
    # < n, else raises IndexError
    def countInValRange(self, l, r, lowVal, highVal):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"countInValRange: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        if lowVal > highVal:
            return 0
        return self._countLess(l, r, highVal, False) - self._countLess(l, r, lowVal, True)

    # O(log^2(N) expected) -- smallest a[i] >= x in [l, r]; None if there is none; needs 0 <= l <= r < n, else raises
    # IndexError
    def smallestGteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"smallestGteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._firstAtLeast(l, r, x, False)

    # O(log^2(N) expected) -- smallest a[i] > x in [l, r]; None if there is none; needs 0 <= l <= r < n, else raises
    # IndexError
    def smallestGtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"smallestGtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._firstAtLeast(l, r, x, True)

    # O(log^2(N) expected) -- largest a[i] <= x in [l, r]; None if there is none; needs 0 <= l <= r < n, else raises
    # IndexError
    def largestLteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"largestLteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._lastBelow(l, r, x, False)

    # O(log^2(N) expected) -- largest a[i] < x in [l, r]; None if there is none; needs 0 <= l <= r < n, else raises
    # IndexError
    def largestLtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"largestLtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._lastBelow(l, r, x, True)

    # O(log^2(N) expected) -- sum of a[i] < x in [l, r]; needs 0 <= l <= r < n, else raises IndexError
    def sumLtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"sumLtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._sumLess(l, r, x, True)

    # O(log^2(N) expected) -- sum of a[i] <= x in [l, r]; needs 0 <= l <= r < n, else raises IndexError
    def sumLteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"sumLteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._sumLess(l, r, x, False)

    # O(log^2(N) expected) -- sum of a[i] > x in [l, r]; needs 0 <= l <= r < n, else raises IndexError
    def sumGtX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"sumGtX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._sumAll(l, r) - self._sumLess(l, r, x, False)

    # O(log^2(N) expected) -- sum of a[i] >= x in [l, r]; needs 0 <= l <= r < n, else raises IndexError
    def sumGteX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"sumGteX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        return self._sumAll(l, r) - self._sumLess(l, r, x, True)

    # O(log^2(N) expected) -- sum of a[i] with lowVal <= a[i] <= highVal in [l, r] (0 if lowVal > highVal); needs 0 <= l
    # <= r < n, else raises IndexError
    def sumInValRange(self, l, r, lowVal, highVal):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"sumInValRange: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        if lowVal > highVal:
            return 0
        return self._sumLess(l, r, highVal, False) - self._sumLess(l, r, lowVal, True)

    # O(log^2(N) expected) -- sum of |a[i] - x| over [l, r]; needs 0 <= l <= r < n, else raises IndexError
    def sumAbsDiffToX(self, l, r, x):
        if l < 0 or l > r or r >= self.n:
            raise IndexError(f"sumAbsDiffToX: needs 0 <= l <= r < n, got l={l}, r={r}, n={self.n}")
        below = self._countLess(l, r, x, True)
        belowSum, total = self._sumLess(l, r, x, True), self._sumAll(l, r)
        return x * below - belowSum + (total - belowSum) - x * ((r - l + 1) - below)

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

    def _sumLess(self, l, r, x, strict):
        n, A, res = self.n, self.A, 0
        for p in self._nodes(l, r):
            if p >= n:
                v = A[p - n]
                if (v < x) if strict else (v <= x):
                    res += v
            else:
                res += self._sumBelow(p, x, strict)
        return res

    def _sumAll(self, l, r):
        n, A, total = self.n, self.A, self.total
        return sum(A[p - n] if p >= n else total[p] for p in self._nodes(l, r))

    def _write(self, i, v):
        old = self.A[i]
        if old == v:
            return
        p = (i + self.n) >> 1
        while p:
            self._erase(p, old)
            self._insert(p, v)
            self.total[p] += v - old
            p >>= 1
        self.A[i] = v

    def _newNode(self, v, count):
        self.key.append(v)
        self.copies.append(count)
        self.under.append(0)
        self.leftChild.append(0)
        self.rightChild.append(0)
        self.priority.append(random())
        self.subSum.append(0)
        t = len(self.key) - 1
        self._pull(t)
        return t

    def _pull(self, t):
        L, R = self.leftChild[t], self.rightChild[t]
        self.under[t] = self.under[L] + self.under[R] + self.copies[t]
        self.subSum[t] = self.subSum[L] + self.subSum[R] + self.key[t] * self.copies[t]

    def _buildTreap(self, vals):  # a treap of vals (sorted) in O(len): a Cartesian tree by priority
        stack, k, size = [], 0, len(vals)
        leftChild, rightChild, priority = self.leftChild, self.rightChild, self.priority
        while k < size:
            nxt = k
            while nxt < size and vals[nxt] == vals[k]:
                nxt += 1
            t, last = self._newNode(vals[k], nxt - k), 0
            k = nxt
            while stack and priority[stack[-1]] < priority[t]:
                last = stack.pop()
            leftChild[t] = last
            if stack:
                rightChild[stack[-1]] = t
            stack.append(t)
        order, todo = [], [stack[0]] if stack else []
        while todo:  # (pull children before parents)
            t = todo.pop()
            order.append(t)
            for c in (leftChild[t], rightChild[t]):
                if c:
                    todo.append(c)
        for t in reversed(order):
            self._pull(t)
        return stack[0] if stack else 0

    def _split(self, t, v, orEqual):  # (keys < v, or <= v if orEqual; the rest)
        if not t:
            return 0, 0
        k = self.key[t]
        if (k <= v) if orEqual else (k < v):
            low, high = self._split(self.rightChild[t], v, orEqual)
            self.rightChild[t] = low
            self._pull(t)
            return t, high
        low, high = self._split(self.leftChild[t], v, orEqual)
        self.leftChild[t] = high
        self._pull(t)
        return low, t

    def _join(self, a, b):  # every key of a is below every key of b
        if not a or not b:
            return a or b
        if self.priority[a] > self.priority[b]:
            self.rightChild[a] = self._join(self.rightChild[a], b)
            self._pull(a)
            return a
        self.leftChild[b] = self._join(a, self.leftChild[b])
        self._pull(b)
        return b

    def _insert(self, p, v):
        low, rest = self._split(self.root[p], v, False)
        same, high = self._split(rest, v, True)
        if same:
            self.copies[same] += 1
            self._pull(same)
        else:
            same = self._newNode(v, 1)
        self.root[p] = self._join(self._join(low, same), high)

    def _erase(self, p, v):  # v is in node p
        low, rest = self._split(self.root[p], v, False)
        same, high = self._split(rest, v, True)
        self.copies[same] -= 1
        if self.copies[same]:
            self._pull(same)
        else:
            same = 0
        self.root[p] = self._join(self._join(low, same), high)

    def _countBelow(self, p, x, strict):
        key, leftChild, rightChild, under, copies = self.key, self.leftChild, self.rightChild, self.under, self.copies
        res, t = 0, self.root[p]
        while t:
            k = key[t]
            if (k < x) if strict else (k <= x):
                res += under[leftChild[t]] + copies[t]
                t = rightChild[t]
            else:
                t = leftChild[t]
        return res

    def _sumBelow(self, p, x, strict):
        key, leftChild, rightChild, subSum, copies = self.key, self.leftChild, self.rightChild, self.subSum, self.copies
        res, t = 0, self.root[p]
        while t:
            k = key[t]
            if (k < x) if strict else (k <= x):
                res += subSum[leftChild[t]] + k * copies[t]
                t = rightChild[t]
            else:
                t = leftChild[t]
        return res

    def _firstIn(self, p, x, strict):  # smallest value > x (strict) or >= x in node p
        key, leftChild, rightChild = self.key, self.leftChild, self.rightChild
        best, t = None, self.root[p]
        while t:
            k = key[t]
            if (k > x) if strict else (k >= x):
                best = k
                t = leftChild[t]
            else:
                t = rightChild[t]
        return best

    def _lastIn(self, p, x, strict):  # largest value < x (strict) or <= x in node p
        key, leftChild, rightChild = self.key, self.leftChild, self.rightChild
        best, t = None, self.root[p]
        while t:
            k = key[t]
            if (k < x) if strict else (k <= x):
                best = k
                t = rightChild[t]
            else:
                t = leftChild[t]
        return best
