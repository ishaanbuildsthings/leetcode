# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-tries-xor/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences countXorGtK countXorGteK countXorLtK countXorLteK getAll kthSmallest kthXor largestLtX largestLteX largestXorLtK largestXorLteK maxAll maxXorAgainstX maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM minAll minXorAgainstX minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM pointAssign pointGet rangeAssign rangeMax rangeMin rangeXorApply size smallestGtX smallestGteX smallestXorGtK smallestXorGteK
# @data-structure-type: sqrt-tries
# @complexities:
#   countGtX: sqrt(N)*log(U)
#   countGteX: sqrt(N)*log(U)
#   countInValRange: sqrt(N)*log(U)
#   countLtX: sqrt(N)*log(U)
#   countLteX: sqrt(N)*log(U)
#   countOccurrences: sqrt(N)*log(U)
#   countXorGtK: sqrt(N)*log(U)
#   countXorGteK: sqrt(N)*log(U)
#   countXorLtK: sqrt(N)*log(U)
#   countXorLteK: sqrt(N)*log(U)
#   getAll: N
#   kthSmallest: sqrt(N)*log(U)
#   kthXor: sqrt(N)*log(U)
#   largestLtX: sqrt(N)*log(U)
#   largestLteX: sqrt(N)*log(U)
#   largestXorLtK: sqrt(N)*log(U)
#   largestXorLteK: sqrt(N)*log(U)
#   maxAll: sqrt(N)*log(U)
#   maxXorAgainstX: sqrt(N)*log(U)
#   maxXorWithVGtM: sqrt(N)*log(U)
#   maxXorWithVGteM: sqrt(N)*log(U)
#   maxXorWithVInValRange: sqrt(N)*log(U)
#   maxXorWithVLtM: sqrt(N)*log(U)
#   maxXorWithVLteM: sqrt(N)*log(U)
#   minAll: sqrt(N)*log(U)
#   minXorAgainstX: sqrt(N)*log(U)
#   minXorWithVGtM: sqrt(N)*log(U)
#   minXorWithVGteM: sqrt(N)*log(U)
#   minXorWithVInValRange: sqrt(N)*log(U)
#   minXorWithVLtM: sqrt(N)*log(U)
#   minXorWithVLteM: sqrt(N)*log(U)
#   pointAssign: sqrt(N)*log(U)
#   pointGet: 1
#   rangeAssign: sqrt(N)*log(U)
#   rangeMax: sqrt(N)*log(U)
#   rangeMin: sqrt(N)*log(U)
#   rangeXorApply: sqrt(N)*log(U)
#   size: 1
#   smallestGtX: sqrt(N)*log(U)
#   smallestGteX: sqrt(N)*log(U)
#   smallestXorGtK: sqrt(N)*log(U)
#   smallestXorGteK: sqrt(N)*log(U)
#   build: N*log(U)
# @memory:
#   layout: none
#   node: L[1*N*log(U)] R[1*N*log(U)] C[1*N*log(U)]
#   tags: none
#   other: arr[1*N] tag[1*sqrt(N)] uni[1*sqrt(N)]
#   note: blocks of about sqrt N, each a binary trie of its stored values (at most its length times log U nodes, U = 2^bits) with a lazy xor and a lazy assign; a scratch trie of 2 sqrt N log U nodes for the partly covered ends of a query

# a[l..r] as a multiset, asked about v ^ x over its values v, with range xor-apply, range assign and point assign. The
# array is cut into blocks of about sqrt(N); each block keeps a binary trie (one level per bit, highest bit first) of its
# stored values, a lazy xor (its real values are stored ^ tag) and a lazy assign (the trie is one path of copies). A
# whole block updates in O(log U); a partly covered one is rewritten and its trie rebuilt. A query walks the tries of
# the whole blocks inside l..r down together, each through its own lazy xor, plus a scratch trie of the partly covered
# ends. Values and every x must lie in [0, 2^bits); thresholds (k, m, lo, hi) can be any integers. 0-indexed, inclusive.
# The plain order statistics (counts, k-th, min / max, predecessor / successor) are the same walks with x = 0.

from math import isqrt


class SqrtXorTries:
    __slots__ = ('B', 'top', 'n', 'S', 'arr', 'L', 'R', 'C', 'base', 'tag', 'uni', 'ones', 'scratch')

    # O(N logU) -- arr: the initial values (a list), each in [0, 2^bits) (bits = 30 holds values up to 1073741823);
    # U = 2^bits
    def __init__(self, arr, bits):
        n = len(arr)
        self.B, self.top, self.n = bits, (1 << bits) - 1, n
        self.S = S = max(1, isqrt(n))
        nb = (n + S - 1) // S
        for i, v in enumerate(arr):
            if not 0 <= v <= self.top:
                raise ValueError(f"__init__: needs 0 <= v < 2^bits, got v = {v} at index {i}, bits = {bits}")
        self.arr = list(arr)  # the stored values: a[i] = arr[i] ^ tag of its block, unless the block is assigned
        # node 0 = empty; block b owns the nodes from base[b] (its root) on, at most (its length) * bits + 1 of them; the
        # scratch trie for the partly covered ends of a query comes after them
        self.base, total = [], 1
        for b in range(nb):
            self.base.append(total)
            total += (min(n, b * S + S) - b * S) * bits + 1
        self.scratch = total
        total += 2 * S * bits + 1
        self.L, self.R, self.C = [0] * total, [0] * total, [0] * total
        self.tag = [0] * nb  # lazy xor of each block
        self.uni = [-1] * nb  # lazy assign: every stored value of the block is uni (-1: none)
        self.ones = [[0] * bits for _ in range(nb)]  #@sumxor  ones[b][h] = how many stored values of block b have bit h set
        for b in range(nb):
            self._rebuild(b)

    # O(sqrt(N) logU) -- a[i] = v (0 <= v < 2^bits); needs 0 <= i < size(), else IndexError (ValueError for v)
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.n}")
        self._checkVal("pointAssign", v)
        b = i // self.S
        self._push(b)
        self.arr[i] = v
        self._rebuild(b)

    # O(sqrt(N) logU) -- a[i] ^= x for every i in [l, r] (0 <= x < 2^bits); needs 0 <= l <= r < size(), else IndexError
    def rangeXorApply(self, l, r, x):
        self._checkRange("rangeXorApply", l, r)
        self._checkVal("rangeXorApply", x)
        S, arr = self.S, self.arr
        for b in range(l // S, r // S + 1):
            s, e = b * S, min(self.n, b * S + S) - 1
            if l <= s and e <= r:
                self.tag[b] ^= x
            else:
                self._push(b)
                for i in range(max(l, s), min(r, e) + 1):
                    arr[i] ^= x
                self._rebuild(b)

    # O(sqrt(N) logU) -- a[i] = v for every i in [l, r] (0 <= v < 2^bits); needs 0 <= l <= r < size(), else IndexError
    def rangeAssign(self, l, r, v):
        self._checkRange("rangeAssign", l, r)
        self._checkVal("rangeAssign", v)
        S, arr = self.S, self.arr
        for b in range(l // S, r // S + 1):
            s, e = b * S, min(self.n, b * S + S) - 1
            if l <= s and e <= r:
                self._assignBlock(b, v)
            else:
                self._push(b)
                for i in range(max(l, s), min(r, e) + 1):
                    arr[i] = v
                self._rebuild(b)

    # O(1) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.n}")
        return self._get(i)

    # O(N) -- the whole array
    def getAll(self):
        return [self._get(i) for i in range(self.n)]

    # O(1) -- the length of the array
    def size(self):
        return self.n

    # O(sqrt(N) logU) -- largest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def maxXorAgainstX(self, l, r, x):
        return self._extreme(self._span("maxXorAgainstX", l, r), self.B - 1, x, 1)

    # O(sqrt(N) logU) -- smallest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def minXorAgainstX(self, l, r, x):
        return self._extreme(self._span("minXorAgainstX", l, r), self.B - 1, x, 0)

    # O(sqrt(N) logU) -- the i-th smallest of v ^ x over the values v in a[l..r], 0-indexed: kthXor(l, r, x, 0) is the
    # smallest (copies count); needs 0 <= l <= r < size() and 0 <= i <= r - l, else IndexError
    def kthXor(self, l, r, x, i):
        src = self._span("kthXor", l, r)
        if not 0 <= i <= r - l:
            raise IndexError(f"kthXor: needs 0 <= i <= r - l, got i = {i}, r - l = {r - l}")
        return self._kthX(src, i + 1, x)

    # O(sqrt(N) logU) -- how many values v in a[l..r] have v ^ x < k (k is a VALUE, not a rank); needs
    # 0 <= l <= r < size()
    def countXorLtK(self, l, r, x, k):
        return self._cntLt(self._span("countXorLtK", l, r), r - l + 1, k, x)

    # O(sqrt(N) logU) -- how many values v in a[l..r] have v ^ x <= k (k is a VALUE, not a rank); needs
    # 0 <= l <= r < size()
    def countXorLteK(self, l, r, x, k):
        return self._cntLt(self._span("countXorLteK", l, r), r - l + 1, k + 1, x)

    # O(sqrt(N) logU) -- how many values v in a[l..r] have v ^ x > k (k is a VALUE, not a rank); needs
    # 0 <= l <= r < size()
    def countXorGtK(self, l, r, x, k):
        return r - l + 1 - self._cntLt(self._span("countXorGtK", l, r), r - l + 1, k + 1, x)

    # O(sqrt(N) logU) -- how many values v in a[l..r] have v ^ x >= k (k is a VALUE, not a rank); needs
    # 0 <= l <= r < size()
    def countXorGteK(self, l, r, x, k):
        return r - l + 1 - self._cntLt(self._span("countXorGteK", l, r), r - l + 1, k, x)

    # O(sqrt(N) logU) -- largest v ^ x < k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def largestXorLtK(self, l, r, x, k):
        src = self._span("largestXorLtK", l, r)
        c = self._cntLt(src, r - l + 1, k, x)
        return self._kthX(src, c, x) if c else None

    # O(sqrt(N) logU) -- largest v ^ x <= k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def largestXorLteK(self, l, r, x, k):
        src = self._span("largestXorLteK", l, r)
        c = self._cntLt(src, r - l + 1, k + 1, x)
        return self._kthX(src, c, x) if c else None

    # O(sqrt(N) logU) -- smallest v ^ x > k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def smallestXorGtK(self, l, r, x, k):
        src = self._span("smallestXorGtK", l, r)
        c = self._cntLt(src, r - l + 1, k + 1, x)
        return self._kthX(src, c + 1, x) if c <= r - l else None

    # O(sqrt(N) logU) -- smallest v ^ x >= k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def smallestXorGteK(self, l, r, x, k):
        src = self._span("smallestXorGteK", l, r)
        c = self._cntLt(src, r - l + 1, k, x)
        return self._kthX(src, c + 1, x) if c <= r - l else None


    # O(sqrt(N) logU) -- largest v ^ x over the values v < m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVLtM(self, l, r, x, m):
        return self._bestIn(self._span("maxXorWithVLtM", l, r), x, 0, m - 1, 1)

    # O(sqrt(N) logU) -- largest v ^ x over the values v <= m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVLteM(self, l, r, x, m):
        return self._bestIn(self._span("maxXorWithVLteM", l, r), x, 0, m, 1)

    # O(sqrt(N) logU) -- largest v ^ x over the values v > m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVGtM(self, l, r, x, m):
        return self._bestIn(self._span("maxXorWithVGtM", l, r), x, m + 1, self.top, 1)

    # O(sqrt(N) logU) -- largest v ^ x over the values v >= m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVGteM(self, l, r, x, m):
        return self._bestIn(self._span("maxXorWithVGteM", l, r), x, m, self.top, 1)

    # O(sqrt(N) logU) -- smallest v ^ x over the values v < m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVLtM(self, l, r, x, m):
        return self._bestIn(self._span("minXorWithVLtM", l, r), x, 0, m - 1, 0)

    # O(sqrt(N) logU) -- smallest v ^ x over the values v <= m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVLteM(self, l, r, x, m):
        return self._bestIn(self._span("minXorWithVLteM", l, r), x, 0, m, 0)

    # O(sqrt(N) logU) -- smallest v ^ x over the values v > m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVGtM(self, l, r, x, m):
        return self._bestIn(self._span("minXorWithVGtM", l, r), x, m + 1, self.top, 0)

    # O(sqrt(N) logU) -- smallest v ^ x over the values v >= m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVGteM(self, l, r, x, m):
        return self._bestIn(self._span("minXorWithVGteM", l, r), x, m, self.top, 0)

    # O(sqrt(N) logU) -- largest v ^ x over the values v in a[l..r] with lo <= v <= hi, or None; needs
    # 0 <= l <= r < size()
    def maxXorWithVInValRange(self, l, r, x, lo, hi):
        return self._bestIn(self._span("maxXorWithVInValRange", l, r), x, lo, hi, 1)

    # O(sqrt(N) logU) -- smallest v ^ x over the values v in a[l..r] with lo <= v <= hi, or None; needs
    # 0 <= l <= r < size()
    def minXorWithVInValRange(self, l, r, x, lo, hi):
        return self._bestIn(self._span("minXorWithVInValRange", l, r), x, lo, hi, 0)

    # ---- plain order statistics over a[l..r] (the same walks with x = 0) ----

    # O(sqrt(N) logU) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLtX(self, l, r, x):
        self._rangeCheck("countLtX", l, r)
        return self._lt(l, r, x)

    # O(sqrt(N) logU) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLteX(self, l, r, x):
        self._rangeCheck("countLteX", l, r)
        return self._lt(l, r, x + 1)

    # O(sqrt(N) logU) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGtX(self, l, r, x):
        self._rangeCheck("countGtX", l, r)
        return r - l + 1 - self._lt(l, r, x + 1)

    # O(sqrt(N) logU) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGteX(self, l, r, x):
        self._rangeCheck("countGteX", l, r)
        return r - l + 1 - self._lt(l, r, x)

    # O(sqrt(N) logU) -- # of values v in a[l..r] with lowVal <= v <= highVal (0 if lowVal > highVal); needs 0 <= l <= r < size()
    def countInValRange(self, l, r, lowVal, highVal):
        self._rangeCheck("countInValRange", l, r)
        return self._lt(l, r, highVal + 1) - self._lt(l, r, lowVal) if lowVal <= highVal else 0

    # O(sqrt(N) logU) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        self._rangeCheck("countOccurrences", l, r)
        return self._lt(l, r, x + 1) - self._lt(l, r, x)

    # O(sqrt(N) logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k <= r - l + 1,
    # else IndexError
    def kthSmallest(self, l, r, k):
        self._rangeCheck("kthSmallest", l, r)
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(sqrt(N) logU) -- min of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMin(self, l, r):
        self._rangeCheck("rangeMin", l, r)
        return self._kth(l, r, 1)

    # O(sqrt(N) logU) -- max of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMax(self, l, r):
        self._rangeCheck("rangeMax", l, r)
        return self._kth(l, r, r - l + 1)

    # O(sqrt(N) logU) -- smallest value >= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGteX(self, l, r, x):
        self._rangeCheck("smallestGteX", l, r)
        c = self._lt(l, r, x)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(sqrt(N) logU) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGtX(self, l, r, x):
        self._rangeCheck("smallestGtX", l, r)
        c = self._lt(l, r, x + 1)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(sqrt(N) logU) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLteX(self, l, r, x):
        self._rangeCheck("largestLteX", l, r)
        c = self._lt(l, r, x + 1)
        return self._kth(l, r, c) if c else None

    # O(sqrt(N) logU) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLtX(self, l, r, x):
        self._rangeCheck("largestLtX", l, r)
        c = self._lt(l, r, x)
        return self._kth(l, r, c) if c else None

    # O(sqrt(N) logU) -- min of the whole array; raises IndexError if it is empty
    def minAll(self):
        if not self.size():
            raise IndexError("minAll: the array is empty")
        return self._kth(0, self.size() - 1, 1)

    # O(sqrt(N) logU) -- max of the whole array; raises IndexError if it is empty
    def maxAll(self):
        if not self.size():
            raise IndexError("maxAll: the array is empty")
        return self._kth(0, self.size() - 1, self.size())

    # ---- internals ----

    def _checkRange(self, name, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"{name}: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.n}")

    def _checkVal(self, name, v):
        if not 0 <= v <= self.top:
            raise ValueError(f"{name}: needs 0 <= value < 2^bits, got {v}, bits = {self.B}")

    def _get(self, i):
        b = i // self.S
        return (self.arr[i] if self.uni[b] < 0 else self.uni[b]) ^ self.tag[b]

    # c copies of v into the trie at root, new nodes taken from free on; returns the next free node
    def _insert(self, root, v, c, free):
        L, R, C = self.L, self.R, self.C
        t = root
        C[t] += c
        for h in range(self.B - 1, -1, -1):
            K = R if v >> h & 1 else L
            u = K[t]
            if not u:
                u, free = free, free + 1
                L[u] = R[u] = C[u] = 0
                K[t] = u
            t = u
            C[t] += c
        return free

    # block b's trie (and bit counts) from its stored values; its lazy tags must be clear
    def _rebuild(self, b):
        root, S, B = self.base[b], self.S, self.B
        self.L[root] = self.R[root] = self.C[root] = 0
        free = root + 1
        for i in range(b * S, min(self.n, b * S + S)):
            v = self.arr[i]
            free = self._insert(root, v, 1, free)

    # every value of block b becomes v: its trie is one path of copies
    def _assignBlock(self, b, v):
        root, size = self.base[b], min(self.n, b * self.S + self.S) - b * self.S
        self.L[root] = self.R[root] = self.C[root] = 0
        self._insert(root, v, size, root + 1)
        self.tag[b], self.uni[b] = 0, v

    # write block b's lazy tags into its stored values (its trie must be rebuilt after)
    def _push(self, b):
        t, u, arr = self.tag[b], self.uni[b], self.arr
        if u >= 0:
            for i in range(b * self.S, min(self.n, b * self.S + self.S)):
                arr[i] = u ^ t
        elif t:
            for i in range(b * self.S, min(self.n, b * self.S + self.S)):
                arr[i] ^= t
        self.tag[b], self.uni[b] = 0, -1

    def _rangeCheck(self, name, l, r):
        self._checkRange(name, l, r)

    def _lt(self, l, r, k):  # how many values in a[l..r] are < k
        return self._cntLt(self._sources(l, r), r - l + 1, k, 0)

    def _kth(self, l, r, k):  # the k-th smallest (1-indexed) of a[l..r]
        return self._kthX(self._sources(l, r), k, 0)

    # checks 0 <= l <= r < size(); the tries whose values make up a[l..r]
    def _span(self, name, l, r):
        self._checkRange(name, l, r)
        return self._sources(l, r)

    # the tries whose values make up a[l..r], as (node, lazy xor) pairs: the whole blocks, plus the scratch trie holding
    # the partly covered ends
    def _sources(self, l, r):
        S, src, ends = self.S, [], []
        for b in range(l // S, r // S + 1):
            s, e = b * S, min(self.n, b * S + S) - 1
            if l <= s and e <= r:
                src.append((self.base[b], self.tag[b]))
            else:
                ends += [self._get(i) for i in range(max(l, s), min(r, e) + 1)]
        if ends:
            root = self.scratch
            self.L[root] = self.R[root] = self.C[root] = 0
            free = root + 1
            for v in ends:
                free = self._insert(root, v, 1, free)
            src.append((root, 0))
        return src

    def _cnt(self, src):
        C = self.C
        return sum(C[t] for t, _ in src)

    def _down(self, src, bit, h):  # the children for real bit h = bit (each through its lazy xor; empty ones dropped)
        L, R, out = self.L, self.R, []
        for t, g in src:
            u = R[t] if bit ^ (g >> h & 1) else L[t]
            if u:
                out.append((u, g))
        return out

    # how many values v below src (cnt of them in all) have v ^ x < k
    def _cntLt(self, src, cnt, k, x):
        if k <= 0:
            return 0
        if k > self.top:
            return cnt
        res = 0
        for h in range(self.B - 1, -1, -1):
            xb = x >> h & 1
            if k >> h & 1:  # every result with bit h = 0 is < k
                res += self._cnt(self._down(src, xb, h))
                src = self._down(src, xb ^ 1, h)
            else:
                src = self._down(src, xb, h)
            if not src:
                break
        return res

    # the k-th smallest (1-indexed) v ^ x over the values below src
    def _kthX(self, src, k, x):
        res = 0
        for h in range(self.B - 1, -1, -1):
            xb = x >> h & 1
            z = self._down(src, xb, h)
            c = self._cnt(z)
            if k <= c:
                src = z
            else:
                k -= c
                src = self._down(src, xb ^ 1, h)
                res |= 1 << h
        return res

    # bits h..0 of the largest (big = 1) / smallest v ^ x below src, which holds some value
    def _extreme(self, src, h, x, big):
        res = 0
        while h >= 0:
            p = (x >> h & 1) ^ big  # the child whose result bit is big
            u = self._down(src, p, h)
            if self._cnt(u):
                src = u
                res |= big << h
            else:
                src = self._down(src, p ^ 1, h)
                res |= (big ^ 1) << h
            h -= 1
        return res

    # the largest (big = 1) / smallest v ^ x over the values v below src with lo <= v <= hi, or None. Walks down the
    # bits lo and hi share, then splits: below lo's side only the lower bound matters, below hi's only the upper one
    def _bestIn(self, src, x, lo, hi, big):
        lo, hi = max(lo, 0), min(hi, self.top)
        if lo > hi:
            return None
        res, h = 0, self.B - 1
        while h >= 0 and (lo >> h & 1) == (hi >> h & 1):
            bit = lo >> h & 1
            src = self._down(src, bit, h)
            if not self._cnt(src):
                return None
            res |= (bit ^ (x >> h & 1)) << h
            h -= 1
        if h < 0:
            return res
        xb = x >> h & 1
        c0 = self._oneSide(self._down(src, 0, h), h - 1, lo, x, big, 1, res | xb << h)
        c1 = self._oneSide(self._down(src, 1, h), h - 1, hi, x, big, 0, res | (xb ^ 1) << h)
        if c0 is None or c1 is None:
            return c1 if c0 is None else c0
        return max(c0, c1) if big else min(c0, c1)

    # below src: the best v ^ x whose bits h..0 are >= (lower = 1) / <= bound's bits h..0, or None; res holds the
    # result's bits above h. Along the path that matches bound, each step off it (to the side the bound allows) is a
    # free subtree: take it at once if its result bit beats the path's, else remember the deepest one
    def _oneSide(self, src, h, bound, x, big, lower, res):
        if not self._cnt(src):
            return None
        fallback = None
        while h >= 0:
            xb, bb = x >> h & 1, bound >> h & 1
            if bb != lower:  # a free side exists: v bit = lower
                f = self._down(src, lower, h)
                if self._cnt(f):
                    fres = res | (lower ^ xb) << h
                    if lower ^ xb == big:
                        return fres | self._extreme(f, h - 1, x, big)
                    fallback = (f, h, fres)
            src = self._down(src, bb, h)
            if not self._cnt(src):
                break
            res |= (bb ^ xb) << h
            h -= 1
        else:
            return res  # v equal to bound below here: allowed (inclusive)
        if fallback is None:
            return None
        f, fh, fres = fallback
        return fres | self._extreme(f, fh - 1, x, big)
