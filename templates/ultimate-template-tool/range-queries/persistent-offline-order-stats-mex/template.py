# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/persistent-offline-order-stats-mex/template.py
# @operations: append countGtX countGteX countInValRange countLtX countLteX countOccurrences getAll kthSmallest largestLtX largestLteX maxAll minAll pointGet pop rangeMax rangeMex rangeMin size smallestGtX smallestGteX
# @data-structure-type: persistent
# @values: offline
# @complexities:
#   append: log(N)
#   countGtX: log(N)
#   countGteX: log(N)
#   countInValRange: log(N)
#   countLtX: log(N)
#   countLteX: log(N)
#   countOccurrences: log(N)
#   getAll: N
#   kthSmallest: log(N)
#   largestLtX: log(N)
#   largestLteX: log(N)
#   pointGet: 1
#   pop: 1
#   rangeMax: log(N)
#   rangeMex: log(N)
#   rangeMin: log(N)
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   size: 1
#   minAll: log(N)
#   maxAll: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: L[1*N*log(N)] R[1*N*log(N)] C[1*N*log(N)]
#   tags: none
#   other: root[1*N] arr[1*N] srt[1*N] mexRoot[1*N] ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)]
#   note: N = every value ever added (initial array plus each append); each adds one root-to-leaf path of log N nodes over the compressed values (and one in the mex tree)

# An array that grows: append(v) appends, and queries on any a[l..r] can come in between. Every value that will
# ever be added is given up front (only to compress them: nothing is added until you push it), so the persistent seg
# tree is over compressed ranks and costs are log N, never log U: version p holds a[0..p-1], a[l..r] is version r + 1
# minus version l, and each append adds one version. Query arguments (x, lowVal, ...) can be anything. 0-indexed.
# rangeMex: a second persistent tree, over the values 0..(# of distinct values) + 1, holding each value's last index.
from bisect import bisect_left, bisect_right
from random import getrandbits


class PersistentOfflineOrderStats:
    __slots__ = ('arr', 'n', 'srt', 'm', 'klo', 'khi', 'root', 'L', 'R', 'C', 'mexHi', 'mexRoot', 'ML', 'MR', 'MN')

    # O(N log N) -- arr: the initial array (a list, may be empty), 0-indexed;
    # allValuesThatWillEverBeInsertedForOfflineCompression: every value
    # append will ever get (any order, duplicates fine; arr's own values are included for you). N = # of distinct values
    def __init__(self, arr, allValuesThatWillEverBeInsertedForOfflineCompression):
        salt = getrandbits(62)  # values are salted while deduping, so no fixed input can make the set collide
        seen = {v ^ salt for v in allValuesThatWillEverBeInsertedForOfflineCompression}
        seen.update([v ^ salt for v in arr])
        self.srt = srt = sorted([v ^ salt for v in seen])
        self.m = len(srt)
        self.klo, self.khi = 0, max(self.m - 1, 0)  # the tree is over ranks 0..m-1
        self.arr, self.n = [], 0
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
        self.root = [0]
        self.mexHi = min(self.m, 1 << 30) + 1  # mex <= (# of distinct values) < this
        self.ML, self.MR, self.MN = [0], [0], [-1]  # node 0 = the empty tree (every last index -1)
        self.mexRoot = [0]
        for v in arr:
            self.append(v)

    # O(logN) -- append v (one of the values given to the constructor, else ValueError): it becomes a[n], n grows by 1
    def append(self, v):
        k = bisect_left(self.srt, v)
        if k == self.m or self.srt[k] != v:
            raise ValueError(f"append: {v} was not in the values given to the constructor")
        self.root.append(self._ins(self.root[-1], k, v))
        prev = self.mexRoot[-1]
        self.mexRoot.append(self._mexSet(prev, v, self.n) if 0 <= v <= self.mexHi else prev)
        self.arr.append(v)
        self.n += 1

    # O(1) -- remove a[n-1] and return it: the newest version is dropped (its nodes stay allocated); needs n >= 1,
    # else raises IndexError
    def pop(self):
        if self.n < 1:
            raise IndexError("pop: needs n >= 1")
        self.root.pop()
        self.mexRoot.pop()
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
        return self._countBelow(l, r, bisect_right(self.srt, highVal)) - self._countBelow(l, r,
            bisect_left(self.srt, lowVal))

    # O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._countBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._countBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return r - l + 1 - self._countBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return r - l + 1 - self._countBelow(l, r, bisect_left(self.srt, x))

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
        c = self._countBelow(l, r, bisect_left(self.srt, x))
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"smallestGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        c = self._countBelow(l, r, bisect_right(self.srt, x))
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"largestLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        c = self._countBelow(l, r, bisect_right(self.srt, x))
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"largestLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        c = self._countBelow(l, r, bisect_left(self.srt, x))
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- smallest integer >= 0 that is not in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMex(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMex: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._mexFrom(l, r, 0)

    # O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.size() < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.size() - 1)

    # O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.size() < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.size() - 1)

    # ---- internals ----

    # copy of version node with one more value (key = its compressed rank)
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
        return self.srt[nl]

    # # of i in [l, r] whose compressed rank is < x
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

    # O(logN) -- copy of node with value v's last index set to i
    def _mexSet(self, node, v, i):
        ML, MR, MN = self.ML, self.MR, self.MN
        path = []
        nl, nh = 0, (self.mexHi - 1) + 1
        while nl != nh:
            mid = (nl + nh) >> 1
            if v <= mid:
                path.append((node, True))
                node, nh = ML[node], mid
            else:
                path.append((node, False))
                node, nl = MR[node], mid + 1
        cur = len(MN)
        ML.append(0), MR.append(0), MN.append(i)
        for old, left in reversed(path):
            lc, rc = (cur, MR[old]) if left else (ML[old], cur)
            cur = len(MN)
            ML.append(lc), MR.append(rc), MN.append(min(MN[lc], MN[rc]))
        return cur

    # O(logN) -- smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    def _mexFrom(self, l, r, s):
        ML, MR, MN = self.ML, self.MR, self.MN
        stack = [(self.mexRoot[r + 1], 0, (self.mexHi - 1) + 1)]
        while stack:
            t, nl, nh = stack.pop()
            if nh < s or MN[t] >= l:  # nothing allowed here, or every value here is in a[l..r]
                continue
            if not t:  # no value here was ever seen
                return max(nl, s)
            if nl == nh:
                return nl
            mid = (nl + nh) >> 1
            stack.append((MR[t], mid + 1, nh))
            stack.append((ML[t], nl, mid))
        return (self.mexHi - 1) + 2  # (unreachable: the n + 2 values 0..n+1 can't all be in a[l..r])
