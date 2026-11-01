# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/andGtX-andGteX-andInValRange-andLtX-andLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-xorGtX-xorGteX-xorInValRange-xorLtX-xorLteX/template.py
# @operations: andGtX andGteX andInValRange andLtX andLteX getAll pointAdd pointAssign pointChmax pointChmin pointGet xorGtX xorGteX xorInValRange xorLtX xorLteX
# @data-structure-type: seg-of-trees
# @complexities:
#   andGtX: log(N)*log(U)
#   andGteX: log(N)*log(U)
#   andInValRange: log(N)*log(U)
#   andLtX: log(N)*log(U)
#   andLteX: log(N)*log(U)
#   getAll: N
#   pointAdd: log(N)*log(U)
#   pointAssign: log(N)*log(U)
#   pointChmax: log(N)*log(U)
#   pointChmin: log(N)*log(U)
#   pointGet: 1
#   xorGtX: log(N)*log(U)
#   xorGteX: log(N)*log(U)
#   xorInValRange: log(N)*log(U)
#   xorLtX: log(N)*log(U)
#   xorLteX: log(N)*log(U)
#   build: N*log(N)*log(U)
# @memory:
#   layout: none
#   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)] X[1*N*log(N)*log(U)] A[1*N*log(N)*log(U)]
#   tags: none
#   other: root[2*N] arr[1*N]
#   note: segment tree over positions (2N nodes, bottom-up), each node a dynamic value seg tree over [valLo, valHi] (U = its size); value nodes are never freed, so each point update adds up to 2 log N log U of them

# xor / OR / AND of the values in a value range inside a[l..r], with point updates. A segment tree over positions
# (bottom-up: node p >= n is a[p - n], node p < n covers its children's positions); every node keeps a dynamic value
# seg tree over [valLo, valHi] of the values at its positions: per value node, the copies below it, the xor, the AND
# of the values present. a[l..r] is O(log N) segment nodes, and each answers a value range in O(log U).
# Values are integers; query arguments (x, lowVal, ...) can be anything.


class SegOfValueTrees:
    __slots__ = ('arr', 'n', 'vlo', 'vhi', 'root', 'L', 'R', 'C', 'X', 'A')

    # O(N log N log U) -- arr: the initial array (a list), 0-indexed; every value a[i] ever holds must lie in
    # [valLo, valHi] (any integers, negative is fine; U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        self.arr = list(arr)
        self.n = n = len(arr)
        self.vlo, self.vhi = valLo, valHi
        self.root = [0] * (2 * n)  # segment node p's value tree (0: empty)
        self.L, self.R, self.C = [0], [0], [0]  # value node 0 = the empty tree
        self.X = [0]  # xor of the values present below
        self.A = [-1]  # AND of the values present below
        for i, v in enumerate(arr):
            self._add(i, v, 1)

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]

    # O(N) -- the whole array (a copy)
    def getAll(self):
        return list(self.arr)

    # O(logN logU) -- a[i] = v
    def pointAssign(self, i, v):
        old = self.arr[i]
        if v != old:
            self._add(i, old, -1)
            self._add(i, v, 1)
            self.arr[i] = v

    # O(logN logU) -- a[i] += v
    def pointAdd(self, i, v):
        self.pointAssign(i, self.arr[i] + v)

    # O(logN logU) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        self.pointAssign(i, max(self.arr[i], v))

    # O(logN logU) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        self.pointAssign(i, min(self.arr[i], v))

    # O(logN logU) -- xor of the values < x in a[l..r] (copies count); 0 if there are none
    def xorLtX(self, l, r, x):
        return self._xor(l, r, self.vlo, x - 1)

    # O(logN logU) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none
    def xorLteX(self, l, r, x):
        return self._xor(l, r, self.vlo, x)

    # O(logN logU) -- xor of the values > x in a[l..r] (copies count); 0 if there are none
    def xorGtX(self, l, r, x):
        return self._xor(l, r, x + 1, self.vhi)

    # O(logN logU) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none
    def xorGteX(self, l, r, x):
        return self._xor(l, r, x, self.vhi)

    # O(logN logU) -- xor of the a[i] with lowVal <= a[i] <= highVal in a[l..r] (copies count); 0 if there are none
    def xorInValRange(self, l, r, lowVal, highVal):
        return self._xor(l, r, lowVal, highVal)

    # O(logN logU) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none
    def andLtX(self, l, r, x):
        return self._and(l, r, self.vlo, x - 1)

    # O(logN logU) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none
    def andLteX(self, l, r, x):
        return self._and(l, r, self.vlo, x)

    # O(logN logU) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none
    def andGtX(self, l, r, x):
        return self._and(l, r, x + 1, self.vhi)

    # O(logN logU) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none
    def andGteX(self, l, r, x):
        return self._and(l, r, x, self.vhi)

    # O(logN logU) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none
    def andInValRange(self, l, r, lowVal, highVal):
        return self._and(l, r, lowVal, highVal)

    # ---- internals ----

    # a[i] = v gains d copies in every segment node over i
    def _add(self, i, v, d):
        root, p = self.root, i + self.n
        while p:
            root[p] = self._ins(root[p], v, d)
            p >>= 1

    def _newNode(self):
        self.L.append(0), self.R.append(0), self.C.append(0)
        self.X.append(0)
        self.A.append(-1)
        return len(self.C) - 1

    # value tree t (0: a new one) with d more copies of v
    def _ins(self, t, v, d):
        L, R, C = self.L, self.R, self.C
        X = self.X
        if not t:
            t = self._newNode()
        top, nl, nh = t, self.vlo, self.vhi
        path = []
        while True:
            C[t] += d
            if d & 1:
                X[t] ^= v
            path.append(t)
            if nl == nh:
                break
            mid = (nl + nh) >> 1
            if v <= mid:
                if not L[t]:
                    L[t] = self._newNode()
                t, nh = L[t], mid
            else:
                if not R[t]:
                    R[t] = self._newNode()
                t, nl = R[t], mid + 1
        c = C[t]
        if not c or c == d:  # v appeared or disappeared here: OR / AND again up the path
            A = self.A
            A[t] = v if c else -1
            for u in reversed(path[:-1]):
                A[u] = A[L[u]] & A[R[u]]
        return top

    # xor of the values in [lo, hi] over a[l..r]: the segment nodes covering [l, r], each a value range walk
    def _xor(self, l, r, lo, hi):
        res = 0
        if lo > hi:
            return res
        root, l, r = self.root, l + self.n, r + self.n + 1
        while l < r:
            if l & 1:
                res ^= self._xorIn(root[l], lo, hi)
                l += 1
            if r & 1:
                r -= 1
                res ^= self._xorIn(root[r], lo, hi)
            l >>= 1
            r >>= 1
        return res

    # xor of value tree t's values in [lo, hi]: whole value nodes inside it, at most 4 a level
    def _xorIn(self, t, lo, hi):
        L, R, F, res = self.L, self.R, self.X, 0
        stack = [(t, self.vlo, self.vhi)]
        while stack:
            t, nl, nh = stack.pop()
            if not t or nh < lo or hi < nl:
                continue
            if lo <= nl and nh <= hi:
                res ^= F[t]
                continue
            mid = (nl + nh) >> 1
            stack.append((L[t], nl, mid))
            stack.append((R[t], mid + 1, nh))
        return res

    # AND of the values in [lo, hi] over a[l..r]: the segment nodes covering [l, r], each a value range walk
    def _and(self, l, r, lo, hi):
        res = -1
        if lo > hi:
            return res
        root, l, r = self.root, l + self.n, r + self.n + 1
        while l < r:
            if l & 1:
                res &= self._andIn(root[l], lo, hi)
                l += 1
            if r & 1:
                r -= 1
                res &= self._andIn(root[r], lo, hi)
            l >>= 1
            r >>= 1
        return res

    # AND of value tree t's values in [lo, hi]: whole value nodes inside it, at most 4 a level
    def _andIn(self, t, lo, hi):
        L, R, F, res = self.L, self.R, self.A, -1
        stack = [(t, self.vlo, self.vhi)]
        while stack:
            t, nl, nh = stack.pop()
            if not t or nh < lo or hi < nl:
                continue
            if lo <= nl and nh <= hi:
                res &= F[t]
                continue
            mid = (nl + nh) >> 1
            stack.append((L[t], nl, mid))
            stack.append((R[t], mid + 1, nh))
        return res
