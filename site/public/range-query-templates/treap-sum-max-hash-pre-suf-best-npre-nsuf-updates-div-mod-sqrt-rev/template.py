# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/treap-sum-max-hash-pre-suf-best-npre-nsuf-updates-div-mod-sqrt-rev/template.py
# @operations: append appendLeft cut getAll hashAll hashAllReversed insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX leftmostPrefixSumGtX leftmostPrefixSumGteX leftmostPrefixSumLtX leftmostPrefixSumLteX longestPalCenteredAtI longestPalCenteredAtIPlusOne maxAll maxPrefixSum maxSubarraySum maxSuffixSum merge minPrefixSum minSuffixSum paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeFloorDiv rangeFloorSqrt rangeHash rangeHashReversed rangeMax rangeMod rangeReverse rangeRotateLeft rangeRotateRight rangeSum rangesEqual rightmostGtX rightmostGteX rightmostSuffixSumGtX rightmostSuffixSumGteX rightmostSuffixSumLtX rightmostSuffixSumLteX size split sumAll trisect
# @data-structure-type: treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: K+log(N) expected
#   isPalindrome: log(N) expected
#   leftmostGtX: log(N) expected
#   leftmostGteX: log(N) expected
#   leftmostPrefixSumGtX: log(N) expected
#   leftmostPrefixSumGteX: log(N) expected
#   leftmostPrefixSumLtX: log(N) expected
#   leftmostPrefixSumLteX: log(N) expected
#   maxPrefixSum: log(N) expected
#   maxSubarraySum: log(N) expected
#   maxSuffixSum: log(N) expected
#   merge: log(N) expected
#   minPrefixSum: log(N) expected
#   minSuffixSum: log(N) expected
#   paste: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   rangeFloorDiv: log(N)*log(U) amortized
#   rangeFloorSqrt: log(N)*log(log(U)) amortized
#   rangeHash: log(N) expected
#   rangeHashReversed: log(N) expected
#   rangeMax: log(N) expected
#   rangeMod: log(N)*log(U) amortized
#   rangeReverse: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangeSum: log(N) expected
#   rangesEqual: log(N) expected
#   rightmostGtX: log(N) expected
#   rightmostGteX: log(N) expected
#   rightmostSuffixSumGtX: log(N) expected
#   rightmostSuffixSumGteX: log(N) expected
#   rightmostSuffixSumLtX: log(N) expected
#   rightmostSuffixSumLteX: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   size: 1
#   pop: log(N) expected
#   popLeft: log(N) expected
#   longestPalCenteredAtI: log^2(N) expected
#   longestPalCenteredAtIPlusOne: log^2(N) expected
#   hashAll: 1
#   sumAll: 1
#   maxAll: 1
#   hashAllReversed: 1
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] pre[1*N] suf[1*N] best[1*N] npre[1*N] nsuf[1*N]
#   tags: rev[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

# Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
# out of (that is how to erase) and paste them back in O(logN) expected each, with rangeFloorDiv, rangeMod,
# rangeFloorSqrt; each node keeps its sum, its max, its forward / backward hash (and B^size), its best prefix sum, its
# best suffix sum, its best subarray sum, its min prefix sum, its min suffix sum over its subtree. All indices 0-based,
# ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when nothing qualifies.
# Lazy tags mean "already applied to this node, not yet to its children".
import random
from math import isqrt


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


class ImplicitTreap:
    # one node pool shared by every ImplicitTreap: cut / paste move nodes between them, so a piece from one can go
    # into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    # whole run), so there is nothing to reset between test cases
    val = [0]
    pri = [0]
    L = [0]
    R = [0]
    sz = [0]
    sm = [0]
    mx = [0]
    fh = [0]
    bh = [0]
    pw = [1]
    pre = [0]
    suf = [0]
    best = [0]
    npre = [0]
    nsuf = [0]
    rev = [0]
    __slots__ = ("root",)

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr))

    def _empty(self):  # a new, empty ImplicitTreap (on the same pool, like every one)
        return ImplicitTreap()

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN) expected -- append v to the end
    def append(self, v):
        self.root = self._merge(self.root, self._newNode(v))

    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0); needs
    # 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"cut: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        self.root = self._merge(a, c)
        piece = self._empty()
        piece.root = b
        return piece

    # O(N) -- the whole current array, every pending tag applied on the way
    def getAll(self):
        L, R, val = self.L, self.R, self.val
        out, stack, t = [], [], self.root
        while stack or t:
            while t:
                self._push(t)
                stack.append(t)
                t = L[t]
            t = stack.pop()
            out.append(val[t])
            t = R[t]
        return out

    # O(logN) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else IndexError (i = size() appends)
    def insertAt(self, i, v):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._newNode(v)), c)

    # O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    # 0 <= i <= size(), else IndexError
    def insertCopiesAt(self, i, v, k):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertCopiesAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        if k > 0:
            a, c = self._split(self.root, i)
            self.root = self._merge(self._merge(a, self._build([v] * k)), c)

    # O(logN) expected -- is a[l..r] a palindrome (its two hashes agree); needs 0 <= l <= r < size(), else IndexError
    def isPalindrome(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"isPalindrome: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.fh[b] == self.bh[b]
        self._release(mark)
        return res

    # O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max); needs
    # 0 <= l <= r < size(), else IndexError
    def leftmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        ps = []
        self._pieces(self.root, l, r, ps)
        pos = l  # (the index of the current piece's first value)
        for t, whole in ps:
            if not whole:
                if val[t] > x:
                    return pos
                pos += 1
                continue
            if F[t] > x:
                i = 0
                while True:
                    self._push(t)
                    if L[t] and F[L[t]] > x:
                        t = L[t]
                    elif val[t] > x:
                        return pos + i + sz[L[t]]
                    else:
                        i += sz[L[t]] + 1
                        t = R[t]
            pos += sz[t]
        return -1

    # O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max); needs
    # 0 <= l <= r < size(), else IndexError
    def leftmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        ps = []
        self._pieces(self.root, l, r, ps)
        pos = l  # (the index of the current piece's first value)
        for t, whole in ps:
            if not whole:
                if val[t] >= x:
                    return pos
                pos += 1
                continue
            if F[t] >= x:
                i = 0
                while True:
                    self._push(t)
                    if L[t] and F[L[t]] >= x:
                        t = L[t]
                    elif val[t] >= x:
                        return pos + i + sz[L[t]]
                    else:
                        i += sz[L[t]] + 1
                        t = R[t]
            pos += sz[t]
        return -1

    # O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums);
    # needs 0 <= l <= r < size(), else IndexError
    def leftmostPrefixSumGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostPrefixSumGtX: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.pre
        ps = []
        self._pieces(self.root, l, r, ps)
        pos, acc = l, 0  # (the index of the current piece's first value; the sum before it)
        for t, whole in ps:
            if not whole:
                acc += val[t]
                if acc > x:
                    return pos
                pos += 1
                continue
            if acc + P[t] > x:
                i = 0
                while True:
                    self._push(t)
                    lt = L[t]
                    if lt and acc + P[lt] > x:
                        t = lt
                        continue
                    acc += sm[lt]
                    if acc + val[t] > x:
                        return pos + i + sz[lt]
                    acc += val[t]
                    i += sz[lt] + 1
                    t = R[t]
            acc += sm[t]
            pos += sz[t]
        return -1

    # O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (a walk pruned by best prefix sums);
    # needs 0 <= l <= r < size(), else IndexError
    def leftmostPrefixSumGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostPrefixSumGteX: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.pre
        ps = []
        self._pieces(self.root, l, r, ps)
        pos, acc = l, 0  # (the index of the current piece's first value; the sum before it)
        for t, whole in ps:
            if not whole:
                acc += val[t]
                if acc >= x:
                    return pos
                pos += 1
                continue
            if acc + P[t] >= x:
                i = 0
                while True:
                    self._push(t)
                    lt = L[t]
                    if lt and acc + P[lt] >= x:
                        t = lt
                        continue
                    acc += sm[lt]
                    if acc + val[t] >= x:
                        return pos + i + sz[lt]
                    acc += val[t]
                    i += sz[lt] + 1
                    t = R[t]
            acc += sm[t]
            pos += sz[t]
        return -1

    # O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] < x, or -1 (a walk pruned by min prefix sums);
    # needs 0 <= l <= r < size(), else IndexError
    def leftmostPrefixSumLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostPrefixSumLtX: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.npre
        ps = []
        self._pieces(self.root, l, r, ps)
        pos, acc = l, 0  # (the index of the current piece's first value; the sum before it)
        for t, whole in ps:
            if not whole:
                acc += val[t]
                if acc < x:
                    return pos
                pos += 1
                continue
            if acc + P[t] < x:
                i = 0
                while True:
                    self._push(t)
                    lt = L[t]
                    if lt and acc + P[lt] < x:
                        t = lt
                        continue
                    acc += sm[lt]
                    if acc + val[t] < x:
                        return pos + i + sz[lt]
                    acc += val[t]
                    i += sz[lt] + 1
                    t = R[t]
            acc += sm[t]
            pos += sz[t]
        return -1

    # O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] <= x, or -1 (a walk pruned by min prefix sums);
    # needs 0 <= l <= r < size(), else IndexError
    def leftmostPrefixSumLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostPrefixSumLteX: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.npre
        ps = []
        self._pieces(self.root, l, r, ps)
        pos, acc = l, 0  # (the index of the current piece's first value; the sum before it)
        for t, whole in ps:
            if not whole:
                acc += val[t]
                if acc <= x:
                    return pos
                pos += 1
                continue
            if acc + P[t] <= x:
                i = 0
                while True:
                    self._push(t)
                    lt = L[t]
                    if lt and acc + P[lt] <= x:
                        t = lt
                        continue
                    acc += sm[lt]
                    if acc + val[t] <= x:
                        return pos + i + sz[lt]
                    acc += val[t]
                    i += sz[lt] + 1
                    t = R[t]
            acc += sm[t]
            pos += sz[t]
        return -1

    # O(logN) expected -- max of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def maxPrefixSum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"maxPrefixSum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.pre[b]
        self._release(mark)
        return res

    # O(logN) expected -- max sum of a non-empty contiguous subarray of a[l..r]; needs 0 <= l <= r < size(), else
    # IndexError
    def maxSubarraySum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"maxSubarraySum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.best[b]
        self._release(mark)
        return res

    # O(logN) expected -- max of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def maxSuffixSum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"maxSuffixSum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.suf[b]
        self._release(mark)
        return res

    # O(logN) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(logN) expected -- min of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def minPrefixSum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"minPrefixSum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.npre[b]
        self._release(mark)
        return res

    # O(logN) expected -- min of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def minSuffixSum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"minSuffixSum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.nsuf[b]
        self._release(mark)
        return res

    # O(logN) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i] (needs
    # 0 <= i <= size(), else IndexError); other is left empty
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError(f"paste: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), c)
        other.root = 0

    # O(logN) expected -- a[i] += v; needs 0 <= i < size(), else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAdd: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = self.val[t] + v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = v; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmax: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = max(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmin: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = min(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        return self.val[self._find(i)[0]]

    # amortized O(logN * logU) expected -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing); needs
    # 0 <= l <= r < size(), else IndexError
    def rangeFloorDiv(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeFloorDiv: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        if x >= 2:
            self._upd(self.root, l, r, lambda t, off: self._shrink(t, 1, lambda v: v // x),
                      lambda w, off: w // x if w >= 1 else w)

    # amortized O(logN * loglogU) expected -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0); needs
    # 0 <= l <= r < size(), else IndexError
    def rangeFloorSqrt(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeFloorSqrt: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self._upd(self.root, l, r, lambda t, off: self._shrink(t, 2, isqrt),
                      lambda w, off: isqrt(w) if w >= 2 else w)

    # O(logN) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    # 0 <= l <= r < size(), else IndexError
    def rangeHash(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeHash: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.fh[b]
        self._release(mark)
        return res

    # O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs
    # 0 <= l <= r < size(), else IndexError
    def rangeHashReversed(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeHashReversed: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.bh[b]
        self._release(mark)
        return res

    # O(logN) expected -- max of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMax: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.mx[b]
        self._release(mark)
        return res

    # amortized O(logN * logU) expected -- a[i] %= x for i in [l, r] (values >= 0, x >= 1); needs
    # 0 <= l <= r < size(), else IndexError
    def rangeMod(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMod: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        if x >= 1:
            self._upd(self.root, l, r, lambda t, off: self._shrink(t, x, lambda v: v % x),
                      lambda w, off: w % x if w >= x else w)

    # O(logN) expected -- reverse a[l..r] in place; needs 0 <= l <= r < size(), else IndexError
    def rangeReverse(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeReverse: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        self._applyRev(b)
        self._join(a, b, c)

    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is taken
    # mod the length (negative shifts right); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateLeft(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateLeft: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)

    # O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    # (negative shifts left); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateRight(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateRight: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self.rangeRotateLeft(l, r, -k)

    # O(logN) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeSum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.sm[b]
        self._release(mark)
        return res

    # O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    # 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), else IndexError
    def rangesEqual(self, l1, r1, l2, r2):
        if not (0 <= l1 <= r1 < self.size() and 0 <= l2 <= r2 < self.size()):
            raise IndexError(f"rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), got "
                             f"l1 = {l1}, r1 = {r1}, l2 = {l2}, r2 = {r2}, n = {self.size()}")
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max); needs
    # 0 <= l <= r < size(), else IndexError
    def rightmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        ps = []
        self._pieces(self.root, l, r, ps)
        end = r  # (the index of the current piece's last value)
        for t, whole in reversed(ps):
            if not whole:
                if val[t] > x:
                    return end
                end -= 1
                continue
            if F[t] > x:
                start, i = end - sz[t] + 1, 0
                while True:
                    self._push(t)
                    if R[t] and F[R[t]] > x:
                        i += sz[L[t]] + 1
                        t = R[t]
                    elif val[t] > x:
                        return start + i + sz[L[t]]
                    else:
                        t = L[t]
            end -= sz[t]
        return -1

    # O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max); needs
    # 0 <= l <= r < size(), else IndexError
    def rightmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        ps = []
        self._pieces(self.root, l, r, ps)
        end = r  # (the index of the current piece's last value)
        for t, whole in reversed(ps):
            if not whole:
                if val[t] >= x:
                    return end
                end -= 1
                continue
            if F[t] >= x:
                start, i = end - sz[t] + 1, 0
                while True:
                    self._push(t)
                    if R[t] and F[R[t]] >= x:
                        i += sz[L[t]] + 1
                        t = R[t]
                    elif val[t] >= x:
                        return start + i + sz[L[t]]
                    else:
                        t = L[t]
            end -= sz[t]
        return -1

    # O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums);
    # needs 0 <= l <= r < size(), else IndexError
    def rightmostSuffixSumGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostSuffixSumGtX: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.suf
        ps = []
        self._pieces(self.root, l, r, ps)
        end, acc = r, 0  # (the index of the current piece's last value; the sum after it)
        for t, whole in reversed(ps):
            if not whole:
                acc += val[t]
                if acc > x:
                    return end
                end -= 1
                continue
            if acc + P[t] > x:
                start, i = end - sz[t] + 1, 0
                while True:
                    self._push(t)
                    rt = R[t]
                    if rt and acc + P[rt] > x:
                        i += sz[L[t]] + 1
                        t = rt
                        continue
                    acc += sm[rt]
                    if acc + val[t] > x:
                        return start + i + sz[L[t]]
                    acc += val[t]
                    t = L[t]
            acc += sm[t]
            end -= sz[t]
        return -1

    # O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (a walk pruned by best suffix sums);
    # needs 0 <= l <= r < size(), else IndexError
    def rightmostSuffixSumGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostSuffixSumGteX: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.suf
        ps = []
        self._pieces(self.root, l, r, ps)
        end, acc = r, 0  # (the index of the current piece's last value; the sum after it)
        for t, whole in reversed(ps):
            if not whole:
                acc += val[t]
                if acc >= x:
                    return end
                end -= 1
                continue
            if acc + P[t] >= x:
                start, i = end - sz[t] + 1, 0
                while True:
                    self._push(t)
                    rt = R[t]
                    if rt and acc + P[rt] >= x:
                        i += sz[L[t]] + 1
                        t = rt
                        continue
                    acc += sm[rt]
                    if acc + val[t] >= x:
                        return start + i + sz[L[t]]
                    acc += val[t]
                    t = L[t]
            acc += sm[t]
            end -= sz[t]
        return -1

    # O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] < x, or -1 (a walk pruned by min suffix sums); needs
    # 0 <= l <= r < size(), else IndexError
    def rightmostSuffixSumLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostSuffixSumLtX: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.nsuf
        ps = []
        self._pieces(self.root, l, r, ps)
        end, acc = r, 0  # (the index of the current piece's last value; the sum after it)
        for t, whole in reversed(ps):
            if not whole:
                acc += val[t]
                if acc < x:
                    return end
                end -= 1
                continue
            if acc + P[t] < x:
                start, i = end - sz[t] + 1, 0
                while True:
                    self._push(t)
                    rt = R[t]
                    if rt and acc + P[rt] < x:
                        i += sz[L[t]] + 1
                        t = rt
                        continue
                    acc += sm[rt]
                    if acc + val[t] < x:
                        return start + i + sz[L[t]]
                    acc += val[t]
                    t = L[t]
            acc += sm[t]
            end -= sz[t]
        return -1

    # O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] <= x, or -1 (a walk pruned by min suffix sums);
    # needs 0 <= l <= r < size(), else IndexError
    def rightmostSuffixSumLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostSuffixSumLteX: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.nsuf
        ps = []
        self._pieces(self.root, l, r, ps)
        end, acc = r, 0  # (the index of the current piece's last value; the sum after it)
        for t, whole in reversed(ps):
            if not whole:
                acc += val[t]
                if acc <= x:
                    return end
                end -= 1
                continue
            if acc + P[t] <= x:
                start, i = end - sz[t] + 1, 0
                while True:
                    self._push(t)
                    rt = R[t]
                    if rt and acc + P[rt] <= x:
                        i += sz[L[t]] + 1
                        t = rt
                        continue
                    acc += sm[rt]
                    if acc + val[t] <= x:
                        return start + i + sz[L[t]]
                    acc += val[t]
                    t = L[t]
            acc += sm[t]
            end -= sz[t]
        return -1

    # O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty; needs
    # 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError(f"split: needs 0 <= k <= size(), got k = {k}, n = {self.size()}")
        left, right = self._empty(), self._empty()
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty; needs
    # 0 <= l <= r < size(), else IndexError
    def trisect(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"trisect: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.root, mid.root, right.root = self._cut(l, r)
        self.root = 0
        return left, mid, right

    # O(log(N) expected) -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        n = self.size()
        if n < 1:
            raise IndexError("pop: needs size() >= 1")
        v = self.pointGet(n - 1)
        self.cut(n - 1, n - 1)
        return v

    # O(log(N) expected) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises
    # IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        v = self.pointGet(0)
        self.cut(0, 0)
        return v

    # O(log^2(N) expected) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)): a binary
    # search on its radius, log N calls of isPalindrome; needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtI(self, i):
        n = self.size()
        if not 0 <= i < n:
            raise IndexError(f"longestPalCenteredAtI: needs 0 <= i < n, got i = {i}, n = {n}")
        lo, hi = 0, min(i, n - 1 - i)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.isPalindrome(i - mid, i + mid):
                lo = mid
            else:
                hi = mid - 1
        return i - lo, i + lo

    # O(log^2(N) expected) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i),
    # the empty
    # range, when there is none (so also for i = n - 1): a binary search on its radius, log N calls of isPalindrome;
    # needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtIPlusOne(self, i):
        n = self.size()
        if not 0 <= i < n:
            raise IndexError(f"longestPalCenteredAtIPlusOne: needs 0 <= i < n, got i = {i}, n = {n}")
        lo, hi = 0, min(i + 1, n - 1 - i)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.isPalindrome(i - mid + 1, i + mid):
                lo = mid
            else:
                hi = mid - 1
        return i - lo + 1, i + lo

    # O(1) -- hash of the whole array a[0..n-1], read off the root: the same base and mod as rangeHash (shared by every
    # structure this run, so it compares with another one's hashes); needs n >= 1, else raises IndexError
    def hashAll(self):
        if self.size() < 1:
            raise IndexError("hashAll: needs n >= 1")
        return self.fh[self.root]

    # O(1) -- sum of the whole array a[0..n-1] (read off the root); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.size() < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.sm[self.root]

    # O(1) -- max of the whole array a[0..n-1] (read off the root); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.size() < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.mx[self.root]

    # O(1) -- hash of the whole array reversed, a[n-1], ..., a[0] (read off the root); it uses the same base and mod as
    # rangeHash, so it equals rangeHash of any range holding those values in that order (and any structure's hashes this
    # run); needs n >= 1, else raises IndexError
    def hashAllReversed(self):
        if self.size() < 1:
            raise IndexError("hashAllReversed: needs n >= 1")
        return self.bh[self.root]

    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        self.sm.append(v)
        self.mx.append(v)
        self.fh.append((v + _HO) % _HP)
        self.bh.append((v + _HO) % _HP)
        self.pw.append(_HB)
        self.pre.append(v)
        self.suf.append(v)
        self.best.append(v)
        self.npre.append(v)
        self.nsuf.append(v)
        self.rev.append(0)
        return x

    # a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    def _build(self, vals):
        pri, L, R = self.pri, self.L, self.R
        stack = []
        for v in vals:
            x, last = self._newNode(v), 0
            while stack and pri[stack[-1]] < pri[x]:
                last = stack.pop()
            L[x] = last
            if stack:
                R[stack[-1]] = x
            stack.append(x)
        root = stack[0] if stack else 0
        order, todo = [], ([root] if root else [])
        while todo:
            x = todo.pop()
            order.append(x)
            if L[x]:
                todo.append(L[x])
            if R[x]:
                todo.append(R[x])
        for x in reversed(order):
            self._pull(x)
        return root

    def _pull(self, x):  # recompute x from its children
        l, r = self.L[x], self.R[x]
        self.sz[x] = self.sz[l] + self.sz[r] + 1
        v = self.val[x]
        s, p, q, b, u, w = v, v, v, v, v, v  # the node alone, then with its left / right parts
        if l:
            ls, lp, lq, lb, lu, lw = self.sm[l], self.pre[l], self.suf[l], self.best[l], self.npre[l], self.nsuf[l]
            s, p, q, b, u, w = ls + s, max(lp, ls + p), max(q, s + lq), max(lb, b, lq + p), min(lu, ls + u), min(w,
                s + lw)
        if r:
            rs, rp, rq, rb, ru, rw = self.sm[r], self.pre[r], self.suf[r], self.best[r], self.npre[r], self.nsuf[r]
            s, p, q, b, u, w = s + rs, max(p, s + rp), max(rq, rs + q), max(b, rb, q + rp), min(u, s + ru), min(rw,
                rs + w)
        self.sm[x], self.pre[x], self.suf[x], self.best[x], self.npre[x], self.nsuf[x] = s, p, q, b, u, w
        m = v
        if l and self.mx[l] > m:
            m = self.mx[l]
        if r and self.mx[r] > m:
            m = self.mx[r]
        self.mx[x] = m
        B, P, pw, fh, bh = _HB, _HP, self.pw, self.fh, self.bh
        hv = (v + _HO) % P
        pw[x] = pw[l] * B % P * pw[r] % P
        fh[x] = ((fh[l] * B + hv) * pw[r] + fh[r]) % P
        bh[x] = ((bh[r] * B + hv) * pw[l] + bh[l]) % P

    def _applyRev(self, x):  # reverse x's subtree
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
            self.fh[x], self.bh[x] = self.bh[x], self.fh[x]
            self.pre[x], self.suf[x] = self.suf[x], self.pre[x]
            self.npre[x], self.nsuf[x] = self.nsuf[x], self.npre[x]

    def _push(self, x):  # hand x's pending tags to its children
        if self.rev[x]:
            self._applyRev(self.L[x])
            self._applyRev(self.R[x])
            self.rev[x] = 0

    def _shrink(self, t, lim, f):  # every value v >= lim under t becomes f(v) (the rest are fixed)
        if not t or self.mx[t] < lim:
            return
        self._push(t)
        v = self.val[t]
        if v >= lim:
            self.val[t] = f(v)
        self._shrink(self.L[t], lim, f)
        self._shrink(self.R[t], lim, f)
        self._pull(t)

    def _split(self, t, k):  # (first k of t, the rest)
        if not t:
            return 0, 0
        self._push(t)
        L, R = self.L, self.R
        if self.sz[L[t]] >= k:
            a, L[t] = self._split(L[t], k)
            self._pull(t)
            return a, t
        R[t], b = self._split(R[t], k - self.sz[L[t]] - 1)
        self._pull(t)
        return t, b

    def _merge(self, a, b):  # a's elements, then b's
        if not a or not b:
            return a or b
        if self.pri[a] > self.pri[b]:
            self._push(a)
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        self._push(b)
        self.L[b] = self._merge(a, self.L[b])
        self._pull(b)
        return b

    def _cut(self, l, r):  # (a[0..l-1], a[l..r], a[r+1..])
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    def _join(self, a, b, c):
        self.root = self._merge(self._merge(a, b), c)

    def _find(self, i):  # (node holding a[i], the nodes above it), every tag on the way pushed
        L, sz, t, path = self.L, self.sz, self.root, []
        while True:
            self._push(t)
            ls = sz[L[t]]
            if i == ls:
                return t, path
            path.append(t)
            if i < ls:
                t = L[t]
            else:
                i -= ls + 1
                t = self.R[t]

    def _pieces(self, t, l, r, out):
        # a[l..r] of t's subtree as (node, whole subtree?) in order; tags on the way pushed
        if not t or r < 0 or l >= self.sz[t]:
            return
        if l <= 0 and self.sz[t] - 1 <= r:
            out.append((t, True))
            return
        self._push(t)
        ls = self.sz[self.L[t]]
        self._pieces(self.L[t], l, r, out)
        if l <= ls <= r:
            out.append((t, False))
        self._pieces(self.R[t], l - ls - 1, r - ls - 1, out)

    def _rangeNode(self, l, r):  # (a temporary node holding a[l..r]'s aggregates, the pool size _release goes back to)
        mark = len(self.val)
        return self._rq(self.root, l, r), mark

    # a node over a[l..r] of t's subtree: t itself when it is all of it, else temporaries made only where two parts meet
    # (pending tags on the way pushed down)
    def _rq(self, t, l, r):
        sz = self.sz
        if not t or r < 0 or l >= sz[t]:
            return 0
        if l <= 0 and sz[t] - 1 <= r:
            return t
        self._push(t)
        ls = sz[self.L[t]]
        if r < ls:
            return self._rq(self.L[t], l, r)
        if l > ls:
            return self._rq(self.R[t], l - ls - 1, r - ls - 1)
        a, b = self._rq(self.L[t], l, r), self._rq(self.R[t], l - ls - 1, r - ls - 1)
        y = self._clone(t)
        self.L[y], self.R[y] = a, b
        self._pull(y)
        return y

    def _clone(self, x):  # a temporary copy of node x (sharing its children), dropped by _release
        y = len(self.val)
        for arr in (self.val, self.pri, self.L, self.R, self.sz, self.sm, self.mx, self.fh, self.bh, self.pw,
                    self.pre, self.suf, self.best, self.npre, self.nsuf, self.rev):
            arr.append(arr[x])
        return y

    def _release(self, mark):  # drop every node made after mark (temporaries: no tree points to them)
        for arr in (self.val, self.pri, self.L, self.R, self.sz, self.sm, self.mx, self.fh, self.bh, self.pw,
                    self.pre, self.suf, self.best, self.npre, self.nsuf, self.rev):
            del arr[mark:]

    # the update on a[l..r] of t's subtree, in place: f(x, off) on a node x covered whole, h(w, off) the new value of a
    # lone value w (off: the distance from l). Only the nodes on the range's two boundary paths are recomputed, nothing
    # is cut out
    def _upd(self, t, l, r, f, h):
        sz = self.sz
        if not t or r < 0 or l >= sz[t]:
            return
        if l <= 0 and sz[t] - 1 <= r:
            f(t, -l)
            return
        self._push(t)
        ls = sz[self.L[t]]
        self._upd(self.L[t], l, r, f, h)
        self._upd(self.R[t], l - ls - 1, r - ls - 1, f, h)
        if l <= ls <= r:
            self.val[t] = h(self.val[t], ls - l)
        self._pull(t)


# Example (pieces move between treaps; merge appends and leaves its argument empty):
#     t = ImplicitTreap([1, 2, 3, 4, 5])
#     left, mid, right = t.trisect(1, 3)  # left = [1], mid = [2, 3, 4], right = [5]; t is empty now
#     t.merge(right)                      # t = [5]
#     t.merge(mid)                        # t = [5, 2, 3, 4]
#     t.merge(left)                       # t = [5, 2, 3, 4, 1]
