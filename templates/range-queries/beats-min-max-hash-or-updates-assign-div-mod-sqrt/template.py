# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/beats-min-max-hash-or-updates-assign-div-mod-sqrt/template.py
# @operations: getAll isPalindrome leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeFloorDiv rangeFloorSqrt rangeHash rangeHashReversed rangeMax rangeMin rangeMod rangeOrQuery rangesEqual rightmostGtX rightmostGteX rightmostLtX rightmostLteX
# @data-structure-type: beats
# @complexities:
#   getAll: N
#   isPalindrome: log(N)
#   leftmostGtX: log(N)
#   leftmostGteX: log(N)
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAssign: log(N)
#   rangeFloorDiv: log(N)*log(U) amortized
#   rangeFloorSqrt: log(N)*log(log(U)) amortized
#   rangeHash: log(N)
#   rangeHashReversed: log(N)
#   rangeMax: log(N)
#   rangeMin: log(N)
#   rangeMod: log(N)*log(U) amortized
#   rangeOrQuery: log(N)
#   rangesEqual: log(N)
#   rightmostGtX: log(N)
#   rightmostGteX: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: mn[2*N] mx[2*N] fh[2*N] bh[2*N] orr[2*N]
#   tags: asg[1*N] hasAsg[1*N]
#   other: PW[1*log(N)] GS[1*log(N)]
#   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only; hash powers are per level (a covering node of level s has 2^s leaves)

# Shrink segment tree with composable aggregates (2N iterative): range updates (rangeAssign, rangeFloorDiv, rangeMod,
# rangeFloorSqrt; mod / floor div / floor sqrt walk down every node whose max still changes, and each value can only
# shrink O(logU) times) and range queries in O(logN); each node keeps its min, its max, its forward / backward hash
# (and B^size), its OR over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing
# qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its level),
# and every internal node holds its pending tags ("applied here, not yet to my children"): an update pushes the tags
# on its two boundary leaf paths, tags the covering nodes, then rebuilds both paths, each node redoing its own pending
# tag.
import random
from math import isqrt


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


INF, NEG = float("inf"), float("-inf")


class ShrinkSegTree:
    __slots__ = ('n', 'h', 'mn', 'mx', 'fh', 'bh', 'orr', 'asg', 'hasAsg', 'PW', 'GS')


    # O(N) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.mn = [0] * n + list(arr)
        self.mx = [0] * n + list(arr)
        self.fh = [0] * n + [(v + _HO) % _HP for v in arr]
        self.bh = [0] * n + [(v + _HO) % _HP for v in arr]
        self.orr = [0] * n + list(arr)
        self.asg = [0] * n
        self.hasAsg = [0] * n
        pw = self.PW = [_HB]  # PW[s] = B^(2^s): the hash power of a level-s node
        while len(pw) <= self.h:
            pw.append(pw[-1] * pw[-1] % _HP)
        gs = self.GS = [1]  # GS[s] = 1 + B + ... + B^(2^s - 1): what a level-s node of all 1s hashes to
        for k in range(self.h):
            gs.append((gs[k] * pw[k] + gs[k]) % _HP)
        for x in range(n - 1, 0, -1):
            s, y = 0, x
            while y < n:  # (x's level: down its left edge to the leaves)
                y <<= 1
                s += 1
            self._pull(x, s)

    # O(N) -- the whole array, every pending tag pushed down on the way
    def getAll(self):
        n = self.n
        for x in range(1, n):  # (parents before children)
            s, y = 0, x
            while y < n:
                y <<= 1
                s += 1
            self._push(x, s)
        return [self._leaf(p) for p in range(n, 2 * n)]

    # O(logN) -- is a[l..r] a palindrome (its two hashes agree); needs 0 <= l <= r < n, else IndexError
    def isPalindrome(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"isPalindrome: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        fh, bh, pw, P, f, b, p = self.fh, self.bh, self.PW, _HP, 0, 0, 1
        for t, s in self._nodes(l, r):
            f = (f * pw[s] + fh[t]) % P
            b = (bh[t] * p + b) % P
            p = p * pw[s] % P
        return f == b

    # O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t if F[2 * t] > x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] >= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t if F[2 * t] >= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] < x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t if F[2 * t] < x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] <= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t if F[2 * t] <= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, self._leaf(p) + v)
        self._rebuild(p)

    # O(logN) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        return self._leaf(p)

    # O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi, s = l + n, r + n + 1, 0
        while lo < hi:
            if lo & 1:
                self._applyAssign(lo, s, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._applyAssign(hi, s, v)
            lo >>= 1
            hi >>= 1
            s += 1
        self._rebuild(l + n)
        self._rebuild(r + n)

    # amortized O(logN * logU) -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing); needs
    # 0 <= l <= r < n, else IndexError
    def rangeFloorDiv(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeFloorDiv: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if x >= 2:
            self._shrinkRange(l, r, 1, lambda v: v // x)

    # amortized O(logN * loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0); needs 0 <= l <= r < n,
    # else IndexError
    def rangeFloorSqrt(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeFloorSqrt: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._shrinkRange(l, r, 2, isqrt)

    # O(logN) -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    # 0 <= l <= r < n, else IndexError
    def rangeHash(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeHash: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        fh, pw, P, res = self.fh, self.PW, _HP, 0
        for t, s in self._nodes(l, r):
            res = (res * pw[s] + fh[t]) % P
        return res

    # O(logN) -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs 0 <= l <= r < n, else
    # IndexError
    def rangeHashReversed(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeHashReversed: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        bh, pw, P, res, p = self.bh, self.PW, _HP, 0, 1
        for t, s in self._nodes(l, r):  # (each node read backwards goes in front of what came before it)
            res = (bh[t] * p + res) % P
            p = p * pw[s] % P
        return res

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, mx = self.n, self.mx
        self._pushPath(l + n)
        self._pushPath(r + n)
        res, lo, hi = NEG, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                if mx[lo] > res:
                    res = mx[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                if mx[hi] > res:
                    res = mx[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, mn = self.n, self.mn
        self._pushPath(l + n)
        self._pushPath(r + n)
        res, lo, hi = INF, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                if mn[lo] < res:
                    res = mn[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                if mn[hi] < res:
                    res = mn[hi]
            lo >>= 1
            hi >>= 1
        return res

    # amortized O(logN * logU) -- a[i] %= x for i in [l, r] (values >= 0, x >= 1); needs 0 <= l <= r < n, else
    # IndexError
    def rangeMod(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if x >= 1:
            self._shrinkRange(l, r, x, lambda v: v % x)

    # O(logN) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeOrQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeOrQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, orr = self.n, self.orr
        self._pushPath(l + n)
        self._pushPath(r + n)
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res |= orr[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res |= orr[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    # 0 <= l1 <= r1 < n and 0 <= l2 <= r2 < n, else IndexError
    def rangesEqual(self, l1, r1, l2, r2):
        if not (0 <= l1 <= r1 < self.n and 0 <= l2 <= r2 < self.n):
            raise IndexError(f"rangesEqual: needs 0 <= l1 <= r1 < n and 0 <= l2 <= r2 < n, got "
                             f"l1 = {l1}, r1 = {r1}, l2 = {l2}, r2 = {r2}, n = {self.n}")
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t + 1 if F[2 * t + 1] > x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] >= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t + 1 if F[2 * t + 1] >= x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] < x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t + 1 if F[2 * t + 1] < x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] <= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t + 1 if F[2 * t + 1] <= x else 2 * t
                return t - n
        return -1

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.mn[p] = v
        self.mx[p] = v
        self.fh[p] = (v + _HO) % _HP
        self.bh[p] = (v + _HO) % _HP
        self.orr[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.mn[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children, then redo its own pending tags
        a, b = 2 * x, 2 * x + 1
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w
        k = self.PW[s - 1]
        self.fh[x] = (self.fh[a] * k + self.fh[b]) % _HP
        self.bh[x] = (self.bh[b] * k + self.bh[a]) % _HP
        self.orr[x] = self.orr[a] | self.orr[b]
        if self.hasAsg[x]:
            self._setAssign(x, s, self.asg[x])

    def _rebuild(self, p):  # recompute every ancestor of leaf p
        s = 0
        while p > 1:
            p >>= 1
            s += 1
            self._pull(p, s)

    def _nodes(self, l, r):  # the O(logN) nodes covering a[l..r], left to right, each with its level
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi, s, left, right = l + n, r + n + 1, 0, [], []
        while lo < hi:
            if lo & 1:
                left.append((lo, s))
                lo += 1
            if hi & 1:
                hi -= 1
                right.append((hi, s))
            lo >>= 1
            hi >>= 1
            s += 1
        return left + right[::-1]

    def _shrinkRange(self, l, r, lim, f):  # every value v >= lim in a[l..r] becomes f(v)
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi, s = l + n, r + n + 1, 0
        while lo < hi:
            if lo & 1:
                self._shrink(lo, s, lim, f)
                lo += 1
            if hi & 1:
                hi -= 1
                self._shrink(hi, s, lim, f)
            lo >>= 1
            hi >>= 1
            s += 1
        self._rebuild(l + n)
        self._rebuild(r + n)

    def _shrink(self, x, s, lim, f):  # every value v >= lim under node x (level s) becomes f(v) (the rest are fixed)
        if self.mx[x] < lim:
            return
        if x >= self.n:
            self._setLeaf(x, f(self.mx[x]))
            return
        if self.mn[x] == self.mx[x]:  # all equal: one assign
            self._applyAssign(x, s, f(self.mx[x]))
            return
        self._push(x, s)
        self._shrink(2 * x, s - 1, lim, f)
        self._shrink(2 * x + 1, s - 1, lim, f)
        self._pull(x, s)

    def _setAssign(self, x, s, v):  # every value under node x becomes v
        self.mn[x] = v
        self.mx[x] = v
        self.orr[x] = v
        self.fh[x] = self.bh[x] = (v + _HO) % _HP * self.GS[s] % _HP

    def _applyAssign(self, x, s, v):
        self._setAssign(x, s, v)
        if x < self.n:
            self.asg[x], self.hasAsg[x] = v, 1

    def _push(self, x, s):  # hand node x's pending tags to its children
        a, b = 2 * x, 2 * x + 1
        c = s - 1  # (their level)
        if self.hasAsg[x]:
            v = self.asg[x]
            self._applyAssign(a, c, v)
            self._applyAssign(b, c, v)
            self.hasAsg[x] = 0

    def _pushPath(self, p):  # hand down every pending tag on the path from the root to leaf p
        for s in range(self.h, 0, -1):
            self._push(p >> s, s)
