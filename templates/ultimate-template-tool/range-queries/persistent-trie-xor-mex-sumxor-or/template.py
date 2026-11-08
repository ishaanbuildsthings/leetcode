# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/persistent-trie-xor-mex-sumxor-or/template.py
# @operations: append countGtX countGteX countInValRange countLtX countLteX countOccurrences countXorGtK countXorGteK countXorLtK countXorLteK getAll kthSmallest kthXor largestLtX largestLteX largestXorLtK largestXorLteK maxAll maxXorAgainstX maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM mexXor minAll minXorAgainstX minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM orGtX orGteX orInValRange orLtX orLteX pointGet pop rangeMax rangeMex rangeMin rangeSum rangeXorQuery size smallestGtX smallestGteX smallestXorGtK smallestXorGteK sumXor
# @data-structure-type: persistent-trie
# @complexities:
#   append: log(U)
#   countGtX: log(U)
#   countGteX: log(U)
#   countInValRange: log(U)
#   countLtX: log(U)
#   countLteX: log(U)
#   countOccurrences: log(U)
#   countXorGtK: log(U)
#   countXorGteK: log(U)
#   countXorLtK: log(U)
#   countXorLteK: log(U)
#   getAll: N
#   kthSmallest: log(U)
#   kthXor: log(U)
#   largestLtX: log(U)
#   largestLteX: log(U)
#   largestXorLtK: log(U)
#   largestXorLteK: log(U)
#   maxAll: log(U)
#   maxXorAgainstX: log(U)
#   maxXorWithVGtM: log(U)
#   maxXorWithVGteM: log(U)
#   maxXorWithVInValRange: log(U)
#   maxXorWithVLtM: log(U)
#   maxXorWithVLteM: log(U)
#   mexXor: log(U)
#   minAll: log(U)
#   minXorAgainstX: log(U)
#   minXorWithVGtM: log(U)
#   minXorWithVGteM: log(U)
#   minXorWithVInValRange: log(U)
#   minXorWithVLtM: log(U)
#   minXorWithVLteM: log(U)
#   orGtX: log(U)*log(U)
#   orGteX: log(U)*log(U)
#   orInValRange: log(U)*log(U)
#   orLtX: log(U)*log(U)
#   orLteX: log(U)*log(U)
#   pointGet: 1
#   pop: 1
#   rangeMax: log(U)
#   rangeMex: log(U)
#   rangeMin: log(U)
#   rangeSum: log(U)
#   rangeXorQuery: log(U)
#   size: 1
#   smallestGtX: log(U)
#   smallestGteX: log(U)
#   smallestXorGtK: log(U)
#   smallestXorGteK: log(U)
#   sumXor: log(U)
#   build: N*log(U)
# @memory:
#   layout: none
#   node: L[1*N*log(U)] R[1*N*log(U)] C[1*N*log(U)] M[1*N*log(U)]
#   tags: none
#   other: root[1*N] arr[1*N] P[1*N*log(U)] OI[1*N*log(U)*log(U)]
#   note: N = every value ever added (initial array plus each append); each adds one root-to-leaf path of log U + 1 nodes, U = 2^bits

# a[l..r] as a multiset, asked about v ^ x over its values v. A persistent binary trie over the values: one level per
# bit, highest bit first, and version p holds a[0..p-1], so the values of a[l..r] are version r + 1 minus version l
# (walk both, subtract counts). Each append adds one version. Values and every x must lie in [0, 2^bits); thresholds
# (k, m, lo, hi) can be any integers. 0-indexed, inclusive.
# mexXor: every node also keeps the smallest "last index" over the values below it (as of its version; -1 if some
# value below never appeared), so a subtree is complete inside a[l..r] exactly when that is >= l.
# sumXor: prefix counts of how many values have each bit set.
# OR / AND by value: every node also keeps, per bit, the latest index (as of its version) of a value below it with that
# bit set (OR) / clear (AND); a subtree has such a value inside a[l..r] exactly when that index is >= l.
# The plain order statistics (counts, k-th, min / max, predecessor / successor) are the same walks with x = 0.


class PersistentXorTrie:
    __slots__ = ('B', 'top', 'arr', 'root', 'L', 'R', 'C', 'M', 'OI', 'P')

    # O(N log U) -- arr: the initial values (a list, may be empty), each in [0, 2^bits) (bits = 30 holds values up to
    # 1073741823); U = 2^bits
    def __init__(self, arr, bits):
        self.B, self.top = bits, (1 << bits) - 1
        self.arr = []
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty trie
        self.M = [-1]
        self.OI = [-1] * bits  # OI[node * bits + h] = latest index of a value below with bit h set (-1: none)
        self.root = [0]
        self.P = [0] * bits
        for v in arr:
            self.append(v)

    # O(logU) -- append v (0 <= v < 2^bits): it becomes a[n], and n grows by 1; raises ValueError outside that
    def append(self, v):
        if not 0 <= v <= self.top:
            raise ValueError(f"append: needs 0 <= v < 2^bits, got v = {v}, bits = {self.B}")
        self.root.append(self._ins(self.root[-1], v, len(self.arr)))
        P, B = self.P, self.B
        base = len(P) - B
        P.extend(P[base + h] + (v >> h & 1) for h in range(B))
        self.arr.append(v)

    # O(1) -- remove a[n-1] and return it (its nodes stay allocated); raises IndexError if the array is empty
    def pop(self):
        if not self.arr:
            raise IndexError("pop: the array is empty")
        self.root.pop()
        del self.P[-self.B:]
        return self.arr.pop()

    # O(1) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < len(self.arr):
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {len(self.arr)}")
        return self.arr[i]

    # O(N) -- the whole array (a copy)
    def getAll(self):
        return list(self.arr)

    # O(1) -- the current length of the array
    def size(self):
        return len(self.arr)

    # O(logU) -- largest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def maxXorAgainstX(self, l, r, x):
        self._rangeCheck("maxXorAgainstX", l, r)
        return self._extreme(self.root[r + 1], self.root[l], self.B - 1, x, 1)

    # O(logU) -- smallest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def minXorAgainstX(self, l, r, x):
        self._rangeCheck("minXorAgainstX", l, r)
        return self._extreme(self.root[r + 1], self.root[l], self.B - 1, x, 0)

    # O(logU) -- the i-th smallest of v ^ x over the values v in a[l..r], 0-indexed: kthXor(l, r, x, 0) is the smallest
    # (copies count); needs 0 <= l <= r < size() and 0 <= i <= r - l, else IndexError
    def kthXor(self, l, r, x, i):
        self._rangeCheck("kthXor", l, r)
        if not 0 <= i <= r - l:
            raise IndexError(f"kthXor: needs 0 <= i <= r - l, got i = {i}, r - l = {r - l}")
        return self._kthX(l, r, i + 1, x)

    # O(logU) -- how many values v in a[l..r] have v ^ x < k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    def countXorLtK(self, l, r, x, k):
        self._rangeCheck("countXorLtK", l, r)
        return self._cntLt(l, r, k, x)

    # O(logU) -- how many values v in a[l..r] have v ^ x <= k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    def countXorLteK(self, l, r, x, k):
        self._rangeCheck("countXorLteK", l, r)
        return self._cntLt(l, r, k + 1, x)

    # O(logU) -- how many values v in a[l..r] have v ^ x > k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    def countXorGtK(self, l, r, x, k):
        self._rangeCheck("countXorGtK", l, r)
        return r - l + 1 - self._cntLt(l, r, k + 1, x)

    # O(logU) -- how many values v in a[l..r] have v ^ x >= k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    def countXorGteK(self, l, r, x, k):
        self._rangeCheck("countXorGteK", l, r)
        return r - l + 1 - self._cntLt(l, r, k, x)

    # O(logU) -- largest v ^ x < k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def largestXorLtK(self, l, r, x, k):
        self._rangeCheck("largestXorLtK", l, r)
        c = self._cntLt(l, r, k, x)
        return self._kthX(l, r, c, x) if c else None

    # O(logU) -- largest v ^ x <= k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def largestXorLteK(self, l, r, x, k):
        self._rangeCheck("largestXorLteK", l, r)
        c = self._cntLt(l, r, k + 1, x)
        return self._kthX(l, r, c, x) if c else None

    # O(logU) -- smallest v ^ x > k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def smallestXorGtK(self, l, r, x, k):
        self._rangeCheck("smallestXorGtK", l, r)
        c = self._cntLt(l, r, k + 1, x)
        return self._kthX(l, r, c + 1, x) if c <= r - l else None

    # O(logU) -- smallest v ^ x >= k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def smallestXorGteK(self, l, r, x, k):
        self._rangeCheck("smallestXorGteK", l, r)
        c = self._cntLt(l, r, k, x)
        return self._kthX(l, r, c + 1, x) if c <= r - l else None

    # O(logU) -- smallest integer >= 0 that is not v ^ x for any value v in a[l..r] (2^bits if every one is); needs
    # 0 <= l <= r < size()
    def mexXor(self, l, r, x):
        self._rangeCheck("mexXor", l, r)
        L, R, M = self.L, self.R, self.M
        a = self.root[r + 1]
        if M[a] >= l:
            return self.top + 1
        res = 0
        for h in range(self.B - 1, -1, -1):
            z, o = (R[a], L[a]) if x >> h & 1 else (L[a], R[a])  # result bit 0 / 1
            if M[z] >= l:  # every result with bit h = 0 (and these higher bits) is taken
                res |= 1 << h
                a = o
            else:
                a = z
            if not a:
                break
        return res

    # O(logU) -- sum of v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size()
    def sumXor(self, l, r, x):
        self._rangeCheck("sumXor", l, r)
        P, B = self.P, self.B
        hi, lo, n, res = (r + 1) * B, l * B, r - l + 1, 0
        for h in range(B):
            ones = P[hi + h] - P[lo + h]
            res += (n - ones if x >> h & 1 else ones) << h
        return res

    # O(logU) -- largest v ^ x over the values v < m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVLtM(self, l, r, x, m):
        self._rangeCheck("maxXorWithVLtM", l, r)
        return self._bestIn(l, r, x, 0, m - 1, 1)

    # O(logU) -- largest v ^ x over the values v <= m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVLteM(self, l, r, x, m):
        self._rangeCheck("maxXorWithVLteM", l, r)
        return self._bestIn(l, r, x, 0, m, 1)

    # O(logU) -- largest v ^ x over the values v > m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVGtM(self, l, r, x, m):
        self._rangeCheck("maxXorWithVGtM", l, r)
        return self._bestIn(l, r, x, m + 1, self.top, 1)

    # O(logU) -- largest v ^ x over the values v >= m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVGteM(self, l, r, x, m):
        self._rangeCheck("maxXorWithVGteM", l, r)
        return self._bestIn(l, r, x, m, self.top, 1)

    # O(logU) -- smallest v ^ x over the values v < m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVLtM(self, l, r, x, m):
        self._rangeCheck("minXorWithVLtM", l, r)
        return self._bestIn(l, r, x, 0, m - 1, 0)

    # O(logU) -- smallest v ^ x over the values v <= m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVLteM(self, l, r, x, m):
        self._rangeCheck("minXorWithVLteM", l, r)
        return self._bestIn(l, r, x, 0, m, 0)

    # O(logU) -- smallest v ^ x over the values v > m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVGtM(self, l, r, x, m):
        self._rangeCheck("minXorWithVGtM", l, r)
        return self._bestIn(l, r, x, m + 1, self.top, 0)

    # O(logU) -- smallest v ^ x over the values v >= m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVGteM(self, l, r, x, m):
        self._rangeCheck("minXorWithVGteM", l, r)
        return self._bestIn(l, r, x, m, self.top, 0)

    # O(logU) -- largest v ^ x over the values v in a[l..r] with lo <= v <= hi, or None; needs 0 <= l <= r < size()
    def maxXorWithVInValRange(self, l, r, x, lo, hi):
        self._rangeCheck("maxXorWithVInValRange", l, r)
        return self._bestIn(l, r, x, lo, hi, 1)

    # O(logU) -- smallest v ^ x over the values v in a[l..r] with lo <= v <= hi, or None; needs 0 <= l <= r < size()
    def minXorWithVInValRange(self, l, r, x, lo, hi):
        self._rangeCheck("minXorWithVInValRange", l, r)
        return self._bestIn(l, r, x, lo, hi, 0)

    # ---- plain order statistics over a[l..r] (the same walks with x = 0) ----

    # O(logU) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLtX(self, l, r, x):
        self._rangeCheck("countLtX", l, r)
        return self._lt(l, r, x)

    # O(logU) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLteX(self, l, r, x):
        self._rangeCheck("countLteX", l, r)
        return self._lt(l, r, x + 1)

    # O(logU) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGtX(self, l, r, x):
        self._rangeCheck("countGtX", l, r)
        return r - l + 1 - self._lt(l, r, x + 1)

    # O(logU) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGteX(self, l, r, x):
        self._rangeCheck("countGteX", l, r)
        return r - l + 1 - self._lt(l, r, x)

    # O(logU) -- # of values v in a[l..r] with lowVal <= v <= highVal (0 if lowVal > highVal); needs 0 <= l <= r < size()
    def countInValRange(self, l, r, lowVal, highVal):
        self._rangeCheck("countInValRange", l, r)
        return self._lt(l, r, highVal + 1) - self._lt(l, r, lowVal) if lowVal <= highVal else 0

    # O(logU) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        self._rangeCheck("countOccurrences", l, r)
        return self._lt(l, r, x + 1) - self._lt(l, r, x)

    # O(logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k <= r - l + 1,
    # else IndexError
    def kthSmallest(self, l, r, k):
        self._rangeCheck("kthSmallest", l, r)
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logU) -- min of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMin(self, l, r):
        self._rangeCheck("rangeMin", l, r)
        return self._kth(l, r, 1)

    # O(logU) -- max of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMax(self, l, r):
        self._rangeCheck("rangeMax", l, r)
        return self._kth(l, r, r - l + 1)

    # O(logU) -- smallest value >= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGteX(self, l, r, x):
        self._rangeCheck("smallestGteX", l, r)
        c = self._lt(l, r, x)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logU) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGtX(self, l, r, x):
        self._rangeCheck("smallestGtX", l, r)
        c = self._lt(l, r, x + 1)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logU) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLteX(self, l, r, x):
        self._rangeCheck("largestLteX", l, r)
        c = self._lt(l, r, x + 1)
        return self._kth(l, r, c) if c else None

    # O(logU) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLtX(self, l, r, x):
        self._rangeCheck("largestLtX", l, r)
        c = self._lt(l, r, x)
        return self._kth(l, r, c) if c else None

    # O(logU) -- min of the whole array; raises IndexError if it is empty
    def minAll(self):
        if not self.size():
            raise IndexError("minAll: the array is empty")
        return self._kth(0, self.size() - 1, 1)

    # O(logU) -- max of the whole array; raises IndexError if it is empty
    def maxAll(self):
        if not self.size():
            raise IndexError("maxAll: the array is empty")
        return self._kth(0, self.size() - 1, self.size())

    # O(logU) -- smallest integer >= 0 that is not in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMex(self, l, r):
        return self.mexXor(l, r, 0)

    # O(logU) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeSum(self, l, r):
        self._rangeCheck("rangeSum", l, r)
        return self._sumAll(l, r)

    # O(logU) -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeXorQuery(self, l, r):
        self._rangeCheck("rangeXorQuery", l, r)
        return self._xorAll(l, r)

    # O(logU * logU) -- OR of the values < x in a[l..r] (0 if there are none); needs 0 <= l <= r < size(), else IndexError
    def orLtX(self, l, r, x):
        self._rangeCheck("orLtX", l, r)
        return self._orIn(l, r, 0, x - 1)

    # O(logU * logU) -- OR of the values <= x in a[l..r] (0 if there are none); needs 0 <= l <= r < size(), else IndexError
    def orLteX(self, l, r, x):
        self._rangeCheck("orLteX", l, r)
        return self._orIn(l, r, 0, x)

    # O(logU * logU) -- OR of the values > x in a[l..r] (0 if there are none); needs 0 <= l <= r < size(), else IndexError
    def orGtX(self, l, r, x):
        self._rangeCheck("orGtX", l, r)
        return self._orIn(l, r, x + 1, self.top)

    # O(logU * logU) -- OR of the values >= x in a[l..r] (0 if there are none); needs 0 <= l <= r < size(), else IndexError
    def orGteX(self, l, r, x):
        self._rangeCheck("orGteX", l, r)
        return self._orIn(l, r, x, self.top)

    # O(logU * logU) -- OR of the values v in a[l..r] with lowVal <= v <= highVal (0 if there are none); needs 0 <= l <= r < size(), else
    # IndexError
    def orInValRange(self, l, r, lowVal, highVal):
        self._rangeCheck("orInValRange", l, r)
        return self._orIn(l, r, lowVal, highVal)

    # ---- internals ----

    def _rangeCheck(self, name, l, r):
        if not 0 <= l <= r < len(self.arr):
            raise IndexError(f"{name}: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {len(self.arr)}")

    # copy of version node with one more copy of v, the value at index i
    def _ins(self, node, v, i):
        L, R, C = self.L, self.R, self.C
        M = self.M
        path = []
        for h in range(self.B - 1, -1, -1):
            path.append(node)
            node = R[node] if v >> h & 1 else L[node]
        cur = len(C)
        L.append(0), R.append(0), C.append(C[node] + 1)
        M.append(i)
        B = self.B
        OI = self.OI
        OI.extend(i if v >> h & 1 else -1 for h in range(B))
        for h in range(self.B):
            old = path[self.B - 1 - h]
            lc, rc = (L[old], cur) if v >> h & 1 else (cur, R[old])
            cur = len(C)
            L.append(lc), R.append(rc), C.append(C[lc] + C[rc])
            M.append(min(M[lc], M[rc]))
            OI.extend(max(OI[lc * B + h], OI[rc * B + h]) for h in range(B))
        return cur

    def _lt(self, l, r, k):  # how many values in a[l..r] are < k
        return self._cntLt(l, r, k, 0)

    def _kth(self, l, r, k):  # the k-th smallest (1-indexed) of a[l..r]
        return self._kthX(l, r, k, 0)

    def _sumAll(self, l, r):
        return self.sumXor(l, r, 0)

    def _xorAll(self, l, r):  # each bit is set in an odd number of values
        P, B = self.P, self.B
        hi, lo = (r + 1) * B, l * B
        return sum(((P[hi + h] - P[lo + h]) & 1) << h for h in range(B))


    # the node pairs (version r + 1, version l) whose subtrees make up the values [lo, hi] (at most 2 per level)
    def _cover(self, l, r, lo, hi):
        lo, hi, out = max(lo, 0), min(hi, self.top), []
        L, R = self.L, self.R
        stack = [(self.root[r + 1], self.root[l], 0, self.top)] if lo <= hi else []
        while stack:
            a, b, nl, nh = stack.pop()
            if not a or nh < lo or hi < nl:
                continue
            if lo <= nl and nh <= hi:
                out.append((a, b))
                continue
            mid = (nl + nh) >> 1
            stack.append((L[a], L[b], nl, mid))
            stack.append((R[a], R[b], mid + 1, nh))
        return out

    def _orIn(self, l, r, lo, hi):  # OR of the values v in a[l..r] with lo <= v <= hi (0 if none)
        OI, B, res = self.OI, self.B, 0
        for a, _ in self._cover(l, r, lo, hi):
            for h in range(B):
                if OI[a * B + h] >= l:
                    res |= 1 << h
        return res

    # how many values v in a[l..r] have v ^ x < k
    def _cntLt(self, l, r, k, x):
        if k <= 0:
            return 0
        if k > self.top:
            return r - l + 1
        L, R, C = self.L, self.R, self.C
        a, b, res = self.root[r + 1], self.root[l], 0
        for h in range(self.B - 1, -1, -1):
            if x >> h & 1:
                za, zb, oa, ob = R[a], R[b], L[a], L[b]
            else:
                za, zb, oa, ob = L[a], L[b], R[a], R[b]
            if k >> h & 1:  # every result with bit h = 0 is < k
                res += C[za] - C[zb]
                a, b = oa, ob
            else:
                a, b = za, zb
            if not a:
                break
        return res

    # the k-th smallest (1-indexed) v ^ x over the values v in a[l..r]
    def _kthX(self, l, r, k, x):
        L, R, C = self.L, self.R, self.C
        a, b, res = self.root[r + 1], self.root[l], 0
        for h in range(self.B - 1, -1, -1):
            if x >> h & 1:
                za, zb, oa, ob = R[a], R[b], L[a], L[b]
            else:
                za, zb, oa, ob = L[a], L[b], R[a], R[b]
            c = C[za] - C[zb]
            if k <= c:
                a, b = za, zb
            else:
                k -= c
                a, b = oa, ob
                res |= 1 << h
        return res

    # bits h..0 of the largest (big = 1) / smallest v ^ x below the node pair (a, b), which holds some value
    def _extreme(self, a, b, h, x, big):
        L, R, C = self.L, self.R, self.C
        res = 0
        while h >= 0:
            p = (x >> h & 1) ^ big  # the child whose result bit is big
            ua, ub = (R[a], R[b]) if p else (L[a], L[b])
            if C[ua] != C[ub]:
                a, b = ua, ub
                res |= big << h
            else:
                a, b = (L[a], L[b]) if p else (R[a], R[b])
                res |= (big ^ 1) << h
            h -= 1
        return res

    # the largest (big = 1) / smallest v ^ x over the values v in a[l..r] with lo <= v <= hi, or None. Walks down the
    # bits lo and hi share, then splits: below lo's side only the lower bound matters, below hi's only the upper one
    def _bestIn(self, l, r, x, lo, hi, big):
        lo, hi = max(lo, 0), min(hi, self.top)
        if lo > hi:
            return None
        L, R, C = self.L, self.R, self.C
        a, b, res, h = self.root[r + 1], self.root[l], 0, self.B - 1
        while h >= 0 and (lo >> h & 1) == (hi >> h & 1):
            bit = lo >> h & 1
            a, b = (R[a], R[b]) if bit else (L[a], L[b])
            if C[a] == C[b]:
                return None
            res |= (bit ^ (x >> h & 1)) << h
            h -= 1
        if h < 0:
            return res
        xb = x >> h & 1
        c0 = self._oneSide(L[a], L[b], h - 1, lo, x, big, 1, res | xb << h)
        c1 = self._oneSide(R[a], R[b], h - 1, hi, x, big, 0, res | (xb ^ 1) << h)
        if c0 is None or c1 is None:
            return c1 if c0 is None else c0
        return max(c0, c1) if big else min(c0, c1)

    # below the node pair (a, b): the best v ^ x whose bits h..0 are >= (lower = 1) / <= bound's bits h..0, or None;
    # res holds the result's bits above h. Along the path that matches bound, each step off it (to the side the bound
    # allows) is a free subtree: take it at once if its result bit beats the path's, else remember the deepest one
    def _oneSide(self, a, b, h, bound, x, big, lower, res):
        L, R, C = self.L, self.R, self.C
        if C[a] == C[b]:
            return None
        fallback = None
        while h >= 0:
            xb, bb = x >> h & 1, bound >> h & 1
            if bb != lower:  # a free side exists: v bit = lower
                fa, fb = (R[a], R[b]) if lower else (L[a], L[b])
                if C[fa] != C[fb]:
                    fres = res | (lower ^ xb) << h
                    if lower ^ xb == big:
                        return fres | self._extreme(fa, fb, h - 1, x, big)
                    fallback = (fa, fb, h, fres)
            a, b = (R[a], R[b]) if bb else (L[a], L[b])
            if C[a] == C[b]:
                break
            res |= (bb ^ xb) << h
            h -= 1
        else:
            return res  # v equal to bound below here: allowed (inclusive)
        if fallback is None:
            return None
        fa, fb, fh, fres = fallback
        return fres | self._extreme(fa, fb, fh - 1, x, big)
