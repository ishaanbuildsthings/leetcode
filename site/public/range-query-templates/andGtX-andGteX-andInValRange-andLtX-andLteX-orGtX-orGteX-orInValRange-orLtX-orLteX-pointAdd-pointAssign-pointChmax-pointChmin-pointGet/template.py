# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/andGtX-andGteX-andInValRange-andLtX-andLteX-orGtX-orGteX-orInValRange-orLtX-orLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/template.py
# @operations: andGtX andGteX andInValRange andLtX andLteX getAll orGtX orGteX orInValRange orLtX orLteX pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: seg-of-trees
# @complexities:
#   andGtX: log(N)*log(U)
#   andGteX: log(N)*log(U)
#   andInValRange: log(N)*log(U)
#   andLtX: log(N)*log(U)
#   andLteX: log(N)*log(U)
#   getAll: N
#   orGtX: log(N)*log(U)
#   orGteX: log(N)*log(U)
#   orInValRange: log(N)*log(U)
#   orLtX: log(N)*log(U)
#   orLteX: log(N)*log(U)
#   pointAdd: log(N)*log(U)
#   pointAssign: log(N)*log(U)
#   pointChmax: log(N)*log(U)
#   pointChmin: log(N)*log(U)
#   pointGet: 1
#   build: N*log(N)*log(U)
# @memory:
#   layout: none
#   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)] O[1*N*log(N)*log(U)] A[1*N*log(N)*log(U)]
#   tags: none
#   other: root[2*N] arr[1*N]
#   note: segment tree over positions (2N nodes, bottom-up), each node a dynamic value seg tree over [valLo, valHi] (U = its size); value nodes are never freed, so each point update adds up to 2 log N log U of them

# xor / OR / AND of the values in a value range inside a[l..r], with point updates. A segment tree over positions
# (bottom-up: node p >= n is a[p - n], node p < n covers its children's positions); every node keeps a dynamic value
# seg tree over [valLo, valHi] of the values at its positions: per value node, the copies below it, the OR, the AND
# of the values present. a[l..r] is O(log N) segment nodes, and each answers a value range in O(log U).
# Values are integers; query arguments (x, lowVal, ...) can be anything.


class SegOfValueTrees:
    __slots__ = ('arr', 'n', 'vlo', 'vhi', 'root', 'L', 'R', 'C', 'O', 'A')

    # O(N log N log U) -- arr: the initial array (a list), 0-indexed; every value a[i] ever holds must lie in
    # [valLo, valHi] (any integers, negative is fine; U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        self.arr = list(arr)
        self.n = n = len(arr)
        self.vlo, self.vhi = valLo, valHi
        self.root = [0] * (2 * n)  # segment node p's value tree (0: empty)
        self.L, self.R, self.C = [0], [0], [0]  # value node 0 = the empty tree
        self.O = [0]  # OR of the values present below
        self.A = [-1]  # AND of the values present below
        for i, v in enumerate(arr):
            self._add(i, v, 1)

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.arr[i]

    # O(N) -- the whole array (a copy)
    def getAll(self):
        return list(self.arr)

    # O(logN logU) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        old = self.arr[i]
        if v != old:
            self._add(i, old, -1)
            self._add(i, v, 1)
            self.arr[i] = v

    # O(logN logU) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.arr[i] + v)

    # O(logN logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, max(self.arr[i], v))

    # O(logN logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, min(self.arr[i], v))

    # O(logN logU) -- OR of the values < x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else IndexError
    def orLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"orLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._or(l, r, self.vlo, x - 1)

    # O(logN logU) -- OR of the values <= x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else IndexError
    def orLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"orLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._or(l, r, self.vlo, x)

    # O(logN logU) -- OR of the values > x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else IndexError
    def orGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"orGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._or(l, r, x + 1, self.vhi)

    # O(logN logU) -- OR of the values >= x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else IndexError
    def orGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"orGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._or(l, r, x, self.vhi)

    # O(logN logU) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none; needs
    # 0 <= l <= r < n, else IndexError
    def orInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"orInValRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._or(l, r, lowVal, highVal)

    # O(logN logU) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    # IndexError
    def andLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"andLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._and(l, r, self.vlo, x - 1)

    # O(logN logU) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    # IndexError
    def andLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"andLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._and(l, r, self.vlo, x)

    # O(logN logU) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    # IndexError
    def andGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"andGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._and(l, r, x + 1, self.vhi)

    # O(logN logU) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none; needs 0 <= l <= r < n, else
    # IndexError
    def andGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"andGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._and(l, r, x, self.vhi)

    # O(logN logU) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none;
    # needs 0 <= l <= r < n, else IndexError
    def andInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"andInValRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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
        self.O.append(0)
        self.A.append(-1)
        return len(self.C) - 1

    # value tree t (0: a new one) with d more copies of v
    def _ins(self, t, v, d):
        L, R, C = self.L, self.R, self.C
        if not t:
            t = self._newNode()
        top, nl, nh = t, self.vlo, self.vhi
        path = []
        while True:
            C[t] += d
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
            O = self.O
            O[t] = v if c else 0
            A = self.A
            A[t] = v if c else -1
            for u in reversed(path[:-1]):
                O[u] = O[L[u]] | O[R[u]]
                A[u] = A[L[u]] & A[R[u]]
        return top

    # OR of the values in [lo, hi] over a[l..r]: the segment nodes covering [l, r], each a value range walk
    def _or(self, l, r, lo, hi):
        res = 0
        if lo > hi:
            return res
        root, l, r = self.root, l + self.n, r + self.n + 1
        while l < r:
            if l & 1:
                res |= self._orIn(root[l], lo, hi)
                l += 1
            if r & 1:
                r -= 1
                res |= self._orIn(root[r], lo, hi)
            l >>= 1
            r >>= 1
        return res

    # OR of value tree t's values in [lo, hi]: whole value nodes inside it, at most 4 a level
    def _orIn(self, t, lo, hi):
        L, R, F, res = self.L, self.R, self.O, 0
        stack = [(t, self.vlo, self.vhi)]
        while stack:
            t, nl, nh = stack.pop()
            if not t or nh < lo or hi < nl:
                continue
            if lo <= nl and nh <= hi:
                res |= F[t]
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
