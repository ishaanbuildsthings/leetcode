# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/persistent-online-order-stats/template.py
# @operations: append countGtX countGteX countInValRange countLtX countLteX countOccurrences getAll kthSmallest largestLtX largestLteX maxAll minAll pointGet pop rangeMax rangeMin size smallestGtX smallestGteX
# @data-structure-type: persistent
# @complexities:
#   append: log(U)
#   countGtX: log(U)
#   countGteX: log(U)
#   countInValRange: log(U)
#   countLtX: log(U)
#   countLteX: log(U)
#   countOccurrences: log(U)
#   getAll: N
#   kthSmallest: log(U)
#   largestLtX: log(U)
#   largestLteX: log(U)
#   pointGet: 1
#   pop: 1
#   rangeMax: log(U)
#   rangeMin: log(U)
#   smallestGtX: log(U)
#   smallestGteX: log(U)
#   size: 1
#   minAll: log(U)
#   maxAll: log(U)
#   build: N*log(U)
# @memory:
#   layout: none
#   node: L[1*N*log(U)] R[1*N*log(U)] C[1*N*log(U)]
#   tags: none
#   other: root[1*N] arr[1*N]
#   note: N = every value ever added (initial array plus each append); each adds one root-to-leaf path of log U nodes over the value range [valLo, valHi]

# An array that grows: append(v) appends, and queries on any a[l..r] can come in between. Nothing is known up
# front, so the persistent seg tree is over the value range [valLo, valHi]: version p holds a[0..p-1], a[l..r] is
# version r + 1 minus version l, and each append adds one version. Values are integers; query arguments (x, lowVal,
# ...) can be anything. 0-indexed, inclusive.


class PersistentOnlineOrderStats:
    __slots__ = ('arr', 'n', 'klo', 'khi', 'root', 'L', 'R', 'C')

    # O(N log U) -- arr: the initial array (a list, may be empty), 0-indexed; every value ever added must lie in
    # [valLo, valHi] (any integers, negative is fine; U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        self.arr, self.n = [], 0
        self.klo, self.khi = valLo, valHi
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
        self.root = [0]
        for v in arr:
            self.append(v)

    # O(logU) -- append v (valLo <= v <= valHi): it becomes a[n], and n grows by 1
    def append(self, v):
        self.root.append(self._ins(self.root[-1], v, v))
        self.arr.append(v)
        self.n += 1

    # O(1) -- remove a[n-1] and return it: the newest version is dropped (its nodes stay allocated); needs n >= 1,
    # else raises IndexError
    def pop(self):
        if self.n < 1:
            raise IndexError("pop: needs n >= 1")
        self.root.pop()
        self.n -= 1
        return self.arr.pop()

    # O(1) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        return self.arr[i]

    # O(N) -- the whole array (a copy)
    def getAll(self):
        return list(self.arr)

    # O(1) -- the current length of the array
    def size(self):
        return len(self.arr)

    # O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self.countInValRange(l, r, x, x)

    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < size(), else IndexError
    def countInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countInValRange: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        if lowVal > highVal:
            return 0
        return self._countBelow(l, r, highVal + 1) - self._countBelow(l, r, lowVal)

    # O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._countBelow(l, r, x)

    # O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._countBelow(l, r, x + 1)

    # O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return r - l + 1 - self._countBelow(l, r, x + 1)

    # O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return r - l + 1 - self._countBelow(l, r, x)

    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k <= r - l + 1,
    # else IndexError
    def kthSmallest(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"kthSmallest: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMin: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._kth(l, r, 1)

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMax: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._kth(l, r, r - l + 1)

    # O(logN) -- smallest value >= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"smallestGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        c = self._countBelow(l, r, x)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"smallestGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        c = self._countBelow(l, r, x + 1)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"largestLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        c = self._countBelow(l, r, x + 1)
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"largestLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        c = self._countBelow(l, r, x)
        return None if c == 0 else self._kth(l, r, c)

    # O(log(U)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.size() < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.size() - 1)

    # O(log(U)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.size() < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.size() - 1)

    # ---- internals ----

    # copy of version node with one more value (key = its value)
    def _ins(self, node, key, v):
        L, R, C = self.L, self.R, self.C
        path = []
        nl, nh = self.klo, self.khi
        while nl != nh:
            mid = (nl + nh) >> 1
            if key <= mid:
                path.append((node, True))
                node, nh = L[node], mid
            else:
                path.append((node, False))
                node, nl = R[node], mid + 1
        cur = len(C)
        L.append(0), R.append(0), C.append(C[node] + 1)
        for old, left in reversed(path):
            lc, rc = (cur, R[old]) if left else (L[old], cur)
            cur = len(C)
            L.append(lc), R.append(rc), C.append(C[lc] + C[rc])
        return cur

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1: walk version r + 1 minus version l
    def _kth(self, l, r, k):
        L, R, C = self.L, self.R, self.C
        a, b, nl, nh = self.root[r + 1], self.root[l], self.klo, self.khi
        while nl != nh:
            mid = (nl + nh) >> 1
            c = C[L[a]] - C[L[b]]
            if k <= c:
                a, b, nh = L[a], L[b], mid
            else:
                k -= c
                a, b, nl = R[a], R[b], mid + 1
        return nl

    # # of i in [l, r] whose value is < x
    def _countBelow(self, l, r, x):
        if x <= self.klo:
            return 0
        if x > self.khi:
            return r - l + 1
        L, R, C = self.L, self.R, self.C
        a, b, nl, nh, res = self.root[r + 1], self.root[l], self.klo, self.khi, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            if x <= mid:
                a, b, nh = L[a], L[b], mid
            else:  # the whole left half is below x
                res += C[L[a]] - C[L[b]]
                a, b, nl = R[a], R[b], mid + 1
        return res
