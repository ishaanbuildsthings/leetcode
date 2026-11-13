# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/node-merge-sort-tree-updates-treap-sums/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/merge-sort-tree-updates-treap-sums/template.py
# @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathCountGtX nodePathCountGteX nodePathCountInValRange nodePathCountLtX nodePathCountLteX nodePathLargestLtX nodePathLargestLteX nodePathSmallestGtX nodePathSmallestGteX nodePathSumAbsDiffToX nodePathSumGtX nodePathSumGteX nodePathSumInValRange nodePathSumLtX nodePathSumLteX nodeSubtreeCountGtX nodeSubtreeCountGteX nodeSubtreeCountInValRange nodeSubtreeCountLtX nodeSubtreeCountLteX nodeSubtreeLargestLtX nodeSubtreeLargestLteX nodeSubtreeSmallestGtX nodeSubtreeSmallestGteX nodeSubtreeSumAbsDiffToX nodeSubtreeSumGtX nodeSubtreeSumGteX nodeSubtreeSumInValRange nodeSubtreeSumLtX nodeSubtreeSumLteX parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: merge-sort-tree
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
#   nodeAdd: log^2(N) expected
#   nodeAssign: log^2(N) expected
#   nodeChmax: log^2(N) expected
#   nodeChmin: log^2(N) expected
#   nodeGet: 1
#   nodePathCountGtX: log^3(N) expected
#   nodePathCountGteX: log^3(N) expected
#   nodePathCountInValRange: log^3(N) expected
#   nodePathCountLtX: log^3(N) expected
#   nodePathCountLteX: log^3(N) expected
#   nodePathLargestLtX: log^3(N) expected
#   nodePathLargestLteX: log^3(N) expected
#   nodePathSmallestGtX: log^3(N) expected
#   nodePathSmallestGteX: log^3(N) expected
#   nodePathSumAbsDiffToX: log^3(N) expected
#   nodePathSumGtX: log^3(N) expected
#   nodePathSumGteX: log^3(N) expected
#   nodePathSumInValRange: log^3(N) expected
#   nodePathSumLtX: log^3(N) expected
#   nodePathSumLteX: log^3(N) expected
#   nodeSubtreeCountGtX: log^2(N) expected
#   nodeSubtreeCountGteX: log^2(N) expected
#   nodeSubtreeCountInValRange: log^2(N) expected
#   nodeSubtreeCountLtX: log^2(N) expected
#   nodeSubtreeCountLteX: log^2(N) expected
#   nodeSubtreeLargestLtX: log^2(N) expected
#   nodeSubtreeLargestLteX: log^2(N) expected
#   nodeSubtreeSmallestGtX: log^2(N) expected
#   nodeSubtreeSmallestGteX: log^2(N) expected
#   nodeSubtreeSumAbsDiffToX: log^2(N) expected
#   nodeSubtreeSumGtX: log^2(N) expected
#   nodeSubtreeSumGteX: log^2(N) expected
#   nodeSubtreeSumInValRange: log^2(N) expected
#   nodeSubtreeSumLtX: log^2(N) expected
#   nodeSubtreeSumLteX: log^2(N) expected
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: log(N)
#   pathNodes: K+log(N)
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: log(N)
#   unweightedDistBetweenPaths: log(N)
#   unweightedDistToPath: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: key[1*N*log(N)] copies[1*N*log(N)] under[1*N*log(N)] leftChild[1*N*log(N)] rightChild[1*N*log(N)] priority[1*N*log(N)] subSum[1*N*log(N)]
#   tags: none
#   other: A[1*N] total[2*N] root[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
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


from bisect import bisect_left


# tree = Tree(edges, root, vals)
#
# edges: the tree's n - 1 edges. Whether nodes are 0..n-1 or 1..n is detected automatically from the edge list
#        (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b), ...]        e.g. [(0, 1), (1, 2)]
#   [(a, b, w), ...]     also accepted: the weights are ignored here
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
#
#   Tree([(0, 1), (1, 2)], 0, [10, 20, 30])       # nodes 0..2, rooted at 0
#   Tree([(1, 2), (2, 3)], 1, [0, 10, 20, 30])    # nodes 1..3, rooted at 1
#
# Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree raises
# IndexError. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). The values sit in the range structure above
# (MergeSortTreeUpdates) in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per
# chain it crosses.
class Tree:
    # O(n * log n) -- builds the layout and the range structure; raises ValueError when the edges are not one tree on
    # nodes 0..n-1 or 1..n, or vals has the wrong length
    def __init__(self, edges, root, vals):
        n = len(edges) + 1
        lo = float("inf")
        for e in edges:
            if len(e) != 2 and len(e) != 3:
                raise ValueError(f"Tree: every edge needs 2 or 3 numbers, (a, b) or (a, b, w), got {e}")
            if e[0] < lo:
                lo = e[0]
            if e[1] < lo:
                lo = e[1]
        if not edges:
            lo = root
        if lo != 0 and lo != 1:
            raise ValueError(f"Tree: nodes must be labeled 0..n-1 or 1..n, but the smallest label is {lo}")
        hi = lo + n - 1
        if not lo <= root <= hi:
            raise ValueError(f"Tree: root must be one of the nodes {lo}..{hi}, got {root}")
        adj = [[] for _ in range(hi + 1)]
        for e in edges:
            a, b = e[0], e[1]
            if a > hi or b > hi:
                raise ValueError(f"Tree: {n - 1} edges means the nodes are {lo}..{hi}, got the edge ({a}, {b})")
            adj[a].append(b)
            adj[b].append(a)

        # parents and depths, top down (par is -2 until a node is reached)
        par = [-2] * (hi + 1)
        dep = [0] * (hi + 1)
        par[root] = -1
        bfs = [root]
        for v in bfs:
            d = dep[v] + 1
            for u in adj[v]:
                if par[u] == -2:
                    par[u] = v
                    dep[u] = d
                    bfs.append(u)
        if len(bfs) != n:
            raise ValueError("Tree: the edges do not form one tree (some node cannot be reached from root)")

        # subtree sizes bottom up, then each node's heavy child (the one with the biggest subtree)
        sz = [1] * (hi + 1)
        for i in range(n - 1, 0, -1):
            v = bfs[i]
            sz[par[v]] += sz[v]
        heavy = [-1] * (hi + 1)
        for i in range(1, n):
            v = bfs[i]
            p = par[v]
            if heavy[p] == -1 or sz[v] > sz[heavy[p]]:
                heavy[p] = v

        # positions: a preorder that always steps into the heavy child first, so a heavy chain is one stretch
        head = [0] * (hi + 1)  # the top node of each node's chain
        pos = [0] * (hi + 1)
        order = [0] * n  # order[pos[v]] = v
        head[root] = root
        stack = [root]
        t = 0
        while stack:
            v = stack.pop()
            pos[v] = t
            order[t] = v
            t += 1
            h = heavy[v]
            p = par[v]
            for u in adj[v]:
                if u != p and u != h:
                    head[u] = u
                    stack.append(u)
            if h != -1:  # pushed last, so it is popped next
                head[h] = head[v]
                stack.append(h)

        # depthPos[depthStart[d] : depthStart[d + 1]] = the positions of the nodes at depth d, increasing
        maxDep = dep[bfs[-1]]
        depthStart = [0] * (maxDep + 2)
        for v in bfs:
            depthStart[dep[v] + 1] += 1
        for d in range(maxDep + 1):
            depthStart[d + 1] += depthStart[d]
        at = depthStart[:]
        depthPos = [0] * n
        for i in range(n):
            d = dep[order[i]]
            depthPos[at[d]] = i
            at[d] += 1

        self.n, self.lo, self.hi, self.root = n, lo, hi, root
        self.par, self.dep, self.sz, self.head, self.pos, self.order = par, dep, sz, head, pos, order
        self.depthStart, self.depthPos = depthStart, depthPos
        if len(vals) != hi + 1:
            raise ValueError(f"Tree: vals[node] is node's value, so nodes {lo}..{hi} need len(vals) = {hi + 1}"
                             f"{' (vals[0] is ignored)' if lo else ''}, got {len(vals)}")
        self.seg = MergeSortTreeUpdates([vals[v] for v in order])  # the values, in position order

    # O(1) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.seg.pointGet(self.pos[node])

    # O(log^2 n) -- val(node) = x
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        self.seg.pointAssign(self.pos[node], x)

    # O(log^2 n) -- val(node) += x
    def nodeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAdd", node)
        self.seg.pointAdd(self.pos[node], x)

    # O(log^2 n) -- val(node) = max(val, x)
    def nodeChmax(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmax", node)
        self.seg.pointChmax(self.pos[node], x)

    # O(log^2 n) -- val(node) = min(val, x)
    def nodeChmin(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmin", node)
        self.seg.pointChmin(self.pos[node], x)

    # O(log^3 n) -- how many node values on the path a..b are < x
    def nodePathCountLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countLtX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^3 n) -- how many node values on the path a..b are <= x
    def nodePathCountLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countLteX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^3 n) -- how many node values on the path a..b are > x
    def nodePathCountGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countGtX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^3 n) -- how many node values on the path a..b are >= x
    def nodePathCountGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countGteX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^3 n) -- how many node values on the path a..b are in [low, high]
    def nodePathCountInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountInValRange", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countInValRange
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], low, high)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, low, high)
        return res

    # O(log^3 n) -- sum of the node values on the path a..b that are < x
    def nodePathSumLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.sumLtX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^3 n) -- sum of the node values on the path a..b that are <= x
    def nodePathSumLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.sumLteX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^3 n) -- sum of the node values on the path a..b that are > x
    def nodePathSumGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.sumGtX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^3 n) -- sum of the node values on the path a..b that are >= x
    def nodePathSumGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.sumGteX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^3 n) -- sum of the node values on the path a..b in [low, high]
    def nodePathSumInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumInValRange", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.sumInValRange
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], low, high)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, low, high)
        return res

    # O(log^3 n) -- sum of |val - x| over the node values on the path a..b
    def nodePathSumAbsDiffToX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumAbsDiffToX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.sumAbsDiffToX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(log^3 n) -- smallest of the node values on the path a..b that is >= x (None if none)
    def nodePathSmallestGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSmallestGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.smallestGteX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v < res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r, x)
        if v is not None and (res is None or v < res):
            res = v
        return res

    # O(log^3 n) -- smallest of the node values on the path a..b that is > x (None if none)
    def nodePathSmallestGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSmallestGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.smallestGtX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v < res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r, x)
        if v is not None and (res is None or v < res):
            res = v
        return res

    # O(log^3 n) -- largest of the node values on the path a..b that is <= x (None if none)
    def nodePathLargestLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLargestLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.largestLteX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v > res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r, x)
        if v is not None and (res is None or v > res):
            res = v
        return res

    # O(log^3 n) -- largest of the node values on the path a..b that is < x (None if none)
    def nodePathLargestLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLargestLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.largestLtX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v > res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r, x)
        if v is not None and (res is None or v > res):
            res = v
        return res

    # O(log^2 n) -- how many node values in node's subtree are < x
    def nodeSubtreeCountLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountLtX", node)
        l = self.pos[node]
        return self.seg.countLtX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- how many node values in node's subtree are <= x
    def nodeSubtreeCountLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountLteX", node)
        l = self.pos[node]
        return self.seg.countLteX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- how many node values in node's subtree are > x
    def nodeSubtreeCountGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountGtX", node)
        l = self.pos[node]
        return self.seg.countGtX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- how many node values in node's subtree are >= x
    def nodeSubtreeCountGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountGteX", node)
        l = self.pos[node]
        return self.seg.countGteX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- how many node values in node's subtree are in [low, high]
    def nodeSubtreeCountInValRange(self, node, low, high):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountInValRange", node)
        l = self.pos[node]
        return self.seg.countInValRange(l, l + self.sz[node] - 1, low, high)

    # O(log^2 n) -- sum of the node values in node's subtree that are < x
    def nodeSubtreeSumLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSumLtX", node)
        l = self.pos[node]
        return self.seg.sumLtX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- sum of the node values in node's subtree that are <= x
    def nodeSubtreeSumLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSumLteX", node)
        l = self.pos[node]
        return self.seg.sumLteX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- sum of the node values in node's subtree that are > x
    def nodeSubtreeSumGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSumGtX", node)
        l = self.pos[node]
        return self.seg.sumGtX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- sum of the node values in node's subtree that are >= x
    def nodeSubtreeSumGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSumGteX", node)
        l = self.pos[node]
        return self.seg.sumGteX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- sum of the node values in node's subtree in [low, high]
    def nodeSubtreeSumInValRange(self, node, low, high):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSumInValRange", node)
        l = self.pos[node]
        return self.seg.sumInValRange(l, l + self.sz[node] - 1, low, high)

    # O(log^2 n) -- sum of |val - x| over the node values in node's subtree
    def nodeSubtreeSumAbsDiffToX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSumAbsDiffToX", node)
        l = self.pos[node]
        return self.seg.sumAbsDiffToX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- smallest of the node values in node's subtree that is >= x (None if none)
    def nodeSubtreeSmallestGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSmallestGteX", node)
        l = self.pos[node]
        return self.seg.smallestGteX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- smallest of the node values in node's subtree that is > x (None if none)
    def nodeSubtreeSmallestGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSmallestGtX", node)
        l = self.pos[node]
        return self.seg.smallestGtX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- largest of the node values in node's subtree that is <= x (None if none)
    def nodeSubtreeLargestLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeLargestLteX", node)
        l = self.pos[node]
        return self.seg.largestLteX(l, l + self.sz[node] - 1, x)

    # O(log^2 n) -- largest of the node values in node's subtree that is < x (None if none)
    def nodeSubtreeLargestLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeLargestLtX", node)
        l = self.pos[node]
        return self.seg.largestLtX(l, l + self.sz[node] - 1, x)

    def _bad(self, name, *nodes):
        raise IndexError(f"{name}: needs {self.lo} <= node <= {self.hi}, got {', '.join(map(str, nodes))}")

    def _lca(self, a, b):
        head, par, dep = self.head, self.par, self.dep
        while head[a] != head[b]:
            if dep[head[a]] > dep[head[b]]:
                a = par[head[a]]
            else:
                b = par[head[b]]
        return a if dep[a] < dep[b] else b

    # the node k steps above node (k <= its depth): a whole chain at a time
    def _kth(self, node, k):
        head, pos, par = self.head, self.pos, self.par
        while True:
            h = head[node]
            d = pos[node] - pos[h]
            if k <= d:
                return self.order[pos[node] - k]
            k -= d + 1
            node = par[h]

    def _dist(self, a, b):
        dep = self.dep
        return dep[a] + dep[b] - 2 * dep[self._lca(a, b)]

    # of the three pairwise lcas two are equal and the third, the deeper one, is the median
    def _median(self, a, b, c):
        dep = self.dep
        x, y, z = self._lca(a, b), self._lca(a, c), self._lca(b, c)
        if dep[y] > dep[x]:
            x = y
        return z if dep[z] > dep[x] else x

    def _isAncestor(self, a, b):
        return self.pos[a] <= self.pos[b] < self.pos[a] + self.sz[a]

    def _onPath(self, a, b, node):
        return self._isAncestor(self._lca(a, b), node) and (self._isAncestor(node, a) or self._isAncestor(node, b))

    # the neighbor of a on the way to b (a != b): the child holding b when b is below a, else a's parent
    def _next(self, a, b):
        if self._isAncestor(a, b):
            return self._kth(b, self.dep[b] - self.dep[a] - 1)
        return self.par[a]

    # O(log n) -- lowest common ancestor of a and b
    def lca(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lca", a, b)
        return self._lca(a, b)

    # O(log n) -- number of edges on the path a..b
    def unweightedDist(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("unweightedDist", a, b)
        return self.dep[a] + self.dep[b] - 2 * self.dep[self._lca(a, b)]

    # O(1) -- edges from the root to node (the root is depth 0)
    def depth(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("depth", node)
        return self.dep[node]

    # O(1) -- node's parent (-1 for the root)
    def parent(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("parent", node)
        return self.par[node]

    # O(log n) -- the node k steps above node (k = 0 is node itself; -1 if that is past the root); needs k >= 0
    def kthAncestor(self, node, k):
        if not self.lo <= node <= self.hi:
            self._bad("kthAncestor", node)
        if k < 0:
            raise IndexError(f"kthAncestor: needs k >= 0, got {k}")
        return self._kth(node, k) if k <= self.dep[node] else -1

    # O(1) -- is a an ancestor of b? (True when a == b)
    def isAncestor(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("isAncestor", a, b)
        return self.pos[a] <= self.pos[b] < self.pos[a] + self.sz[a]

    # O(1) -- number of nodes in node's subtree (node included)
    def subtreeSize(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("subtreeSize", node)
        return self.sz[node]

    # O(log n) -- number of nodes in node's subtree at depth d (the root is depth 0); 0 when there are none
    def countAtDepthInSubtree(self, node, d):
        if not self.lo <= node <= self.hi:
            self._bad("countAtDepthInSubtree", node)
        if d < 0 or d + 1 >= len(self.depthStart):
            return 0
        s, e = self.depthStart[d], self.depthStart[d + 1]
        l = self.pos[node]
        return bisect_left(self.depthPos, l + self.sz[node], s, e) - bisect_left(self.depthPos, l, s, e)

    # O(log n) -- lca of a and b if the tree were rooted at r instead
    def lcaRootedAt(self, r, a, b):
        if not (self.lo <= r <= self.hi and self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lcaRootedAt", r, a, b)
        return self._median(a, b, r)

    # O(log n) -- node's parent if the tree were rooted at r (-1 when node == r)
    def parentRootedAt(self, r, node):
        if not (self.lo <= r <= self.hi and self.lo <= node <= self.hi):
            self._bad("parentRootedAt", r, node)
        return -1 if node == r else self._next(node, r)

    # O(log n) -- size of node's subtree if the tree were rooted at r
    def subtreeSizeRootedAt(self, r, node):
        if not (self.lo <= r <= self.hi and self.lo <= node <= self.hi):
            self._bad("subtreeSizeRootedAt", r, node)
        if node == r:
            return self.n
        if self._isAncestor(node, r):  # r hangs below node: everything but the child holding r
            return self.n - self.sz[self._kth(r, self.dep[r] - self.dep[node] - 1)]
        return self.sz[node]

    # O(log n) -- the kth node walking a -> b (k = 0 is a, k = unweightedDist(a, b) is b; -1 if k is past b); needs
    # k >= 0
    def kthNodeOnPath(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("kthNodeOnPath", a, b)
        if k < 0:
            raise IndexError(f"kthNodeOnPath: needs k >= 0, got {k}")
        dep = self.dep
        c = self._lca(a, b)
        up = dep[a] - dep[c]
        total = up + dep[b] - dep[c]
        if k > total:
            return -1
        return self._kth(a, k) if k <= up else self._kth(b, total - k)

    # O(log n) -- the neighbor of a one step toward b (-1 if a == b)
    def nextNodeOnPath(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nextNodeOnPath", a, b)
        return -1 if a == b else self._next(a, b)

    # O(log n) -- does the path a..b pass through node? (a and b count)
    def isOnPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("isOnPath", a, b, node)
        return self._onPath(a, b, node)

    # O(log n) -- fewest edges from node to any node on the path a..b (0 if node is on it)
    def unweightedDistToPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("unweightedDistToPath", a, b, node)
        return self._dist(node, self._median(a, b, node))

    # O(log n) -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    def unweightedDistBetweenPaths(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("unweightedDistBetweenPaths", a, b, c, d)
        p = self._median(a, b, c)  # where c's side meets the path a..b
        if p != self._median(a, b, d):
            return 0  # c and d meet it at different nodes, so c..d runs along it
        return self._dist(p, self._median(c, d, p))

    # O(log n) -- the one node that lies on all three paths between a, b and c
    def median(self, a, b, c):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= c <= self.hi):
            self._bad("median", a, b, c)
        return self._median(a, b, c)

    # O(log n) -- the shared part of paths a..b and c..d as its two end nodes (p, q), p first walking a -> b; p == q
    # if they share one node; (-1, -1) if they share none
    def pathIntersection(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("pathIntersection", a, b, c, d)
        p, q = self._median(a, b, c), self._median(a, b, d)  # where c's side and d's side meet the path a..b
        if p == q:
            return (p, p) if self._onPath(c, d, p) else (-1, -1)
        return (p, q) if self._dist(a, p) < self._dist(a, q) else (q, p)

    # O(K + log n) -- every node on the path a..b, in order from a (K = how many)
    def pathNodes(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("pathNodes", a, b)
        par = self.par
        c = self._lca(a, b)
        out = []
        while a != c:
            out.append(a)
            a = par[a]
        out.append(c)
        tail = []
        while b != c:
            tail.append(b)
            b = par[b]
        tail.reverse()
        return out + tail
