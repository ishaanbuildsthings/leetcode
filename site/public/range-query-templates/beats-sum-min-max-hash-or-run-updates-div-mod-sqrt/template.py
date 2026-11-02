# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/beats-sum-min-max-hash-or-run-updates-div-mod-sqrt/template.py
# @operations: getAll isPalindrome leftmostGtX leftmostGteX leftmostLtX leftmostLteX longestEqualRun pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv rangeFloorSqrt rangeHash rangeHashReversed rangeMax rangeMin rangeMod rangeOrQuery rangeSum rangesEqual rightmostGtX rightmostGteX rightmostLtX rightmostLteX
# @data-structure-type: beats
# @complexities:
#   getAll: N
#   isPalindrome: log(N)
#   leftmostGtX: log(N)
#   leftmostGteX: log(N)
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   longestEqualRun: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeFloorDiv: log(N)*log(U) amortized
#   rangeFloorSqrt: log(N)*log(log(U)) amortized
#   rangeHash: log(N)
#   rangeHashReversed: log(N)
#   rangeMax: log(N)
#   rangeMin: log(N)
#   rangeMod: log(N)*log(U) amortized
#   rangeOrQuery: log(N)
#   rangeSum: log(N)
#   rangesEqual: log(N)
#   rightmostGtX: log(N)
#   rightmostGteX: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] mn[2*N] mx[2*N] fh[2*N] bh[2*N] orr[2*N] fv[2*N] lv[2*N] pr[2*N] sr[2*N] br[2*N]
#   tags: none
#   other: PW[1*log(N)]
#   note: leaves [n, 2n) hold each value's own aggregates; hash powers are per level (a covering node of level s has 2^s leaves)

# Shrink segment tree with composable aggregates (2N iterative): range updates (rangeFloorDiv, rangeMod,
# rangeFloorSqrt; mod / floor div / floor sqrt walk down every node whose max still changes, and each value can only
# shrink O(logU) times) and range queries in O(logN); each node keeps its sum, its min, its max, its forward /
# backward hash (and B^size), its OR, its first / last value and the equal runs at its ends and inside over its range.
# All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n); a node
# used by a query or update is a perfect subtree of 2^s leaves (s = its level); an update rewrites a leaf, then its
# ancestors.
import random
from math import isqrt


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


INF, NEG = float("inf"), float("-inf")


class ShrinkSegTree:
    __slots__ = ('n', 'h', 'sm', 'mn', 'mx', 'fh', 'bh', 'orr', 'fv', 'lv', 'pr', 'sr', 'br', 'PW')


    # O(N) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.mn = [0] * n + list(arr)
        self.mx = [0] * n + list(arr)
        self.fh = [0] * n + [(v + _HO) % _HP for v in arr]
        self.bh = [0] * n + [(v + _HO) % _HP for v in arr]
        self.orr = [0] * n + list(arr)
        self.fv = [0] * n + list(arr)
        self.lv = [0] * n + list(arr)
        self.pr = [0] * n + [1] * n
        self.sr = [0] * n + [1] * n
        self.br = [0] * n + [1] * n
        pw = self.PW = [_HB]  # PW[s] = B^(2^s): the hash power of a level-s node
        while len(pw) <= self.h:
            pw.append(pw[-1] * pw[-1] % _HP)
        for x in range(n - 1, 0, -1):
            s, y = 0, x
            while y < n:  # (x's level: down its left edge to the leaves)
                y <<= 1
                s += 1
            self._pull(x, s)

    # O(N) -- the whole array
    def getAll(self):
        return self.sm[self.n:]

    # O(logN) -- is a[l..r] a palindrome (its two hashes agree)
    def isPalindrome(self, l, r):
        fh, bh, pw, P, f, b, p = self.fh, self.bh, self.PW, _HP, 0, 0, 1
        for t, s in self._nodes(l, r):
            f = (f * pw[s] + fh[t]) % P
            b = (bh[t] * p + b) % P
            p = p * pw[s] % P
        return f == b

    # O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    def leftmostGtX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] > x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    def leftmostGteX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] >= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] >= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    def leftmostLtX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] < x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] < x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min)
    def leftmostLteX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] <= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] <= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the longest run of equal adjacent values in a[l..r]
    def longestEqualRun(self, l, r):
        pr, sr, br, fv, lv = self.pr, self.sr, self.br, self.fv, self.lv
        ns = self._nodes(l, r)
        t, s = ns[0]
        p, q, res, k, last = pr[t], sr[t], br[t], 1 << s, lv[t]  # (prefix run, suffix run, best, length, last value)
        for t, s in ns[1:]:
            j = last == fv[t]
            if j and q + pr[t] > res:
                res = q + pr[t]
            if br[t] > res:
                res = br[t]
            if j and p == k:
                p += pr[t]
            q = q + sr[t] if j and sr[t] == 1 << s else sr[t]
            k += 1 << s
            last = lv[t]
        return res

    # O(logN) -- a[i] += v
    def pointAdd(self, i, v):
        p = i + self.n
        self._setLeaf(p, self._leaf(p) + v)
        self._rebuild(p)

    # O(logN) -- a[i] = v
    def pointAssign(self, i, v):
        p = i + self.n
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        p = i + self.n
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        p = i + self.n
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        return self._leaf(p)

    # amortized O(logN * logU) -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing)
    def rangeFloorDiv(self, l, r, x):
        if x >= 2:
            self._shrinkRange(l, r, 1, lambda v: v // x)

    # amortized O(logN * loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0)
    def rangeFloorSqrt(self, l, r):
        self._shrinkRange(l, r, 2, isqrt)

    # O(logN) -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    def rangeHash(self, l, r):
        fh, pw, P, res = self.fh, self.PW, _HP, 0
        for t, s in self._nodes(l, r):
            res = (res * pw[s] + fh[t]) % P
        return res

    # O(logN) -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    def rangeHashReversed(self, l, r):
        bh, pw, P, res, p = self.bh, self.PW, _HP, 0, 1
        for t, s in self._nodes(l, r):  # (each node read backwards goes in front of what came before it)
            res = (bh[t] * p + res) % P
            p = p * pw[s] % P
        return res

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        n, mx = self.n, self.mx
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

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        n, mn = self.n, self.mn
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

    # amortized O(logN * logU) -- a[i] %= x for i in [l, r] (values >= 0, x >= 1)
    def rangeMod(self, l, r, x):
        if x >= 1:
            self._shrinkRange(l, r, x, lambda v: v % x)

    # O(logN) -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r):
        n, orr = self.n, self.orr
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

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        n, sm = self.n, self.sm
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res += sm[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res += sm[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    def rightmostGtX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] > x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    def rightmostGteX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] >= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] >= x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    def rightmostLtX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] < x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] < x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min)
    def rightmostLteX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] <= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] <= x else 2 * t
                return t - n
        return -1

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.mn[p] = v
        self.mx[p] = v
        self.fh[p] = (v + _HO) % _HP
        self.bh[p] = (v + _HO) % _HP
        self.orr[p] = v
        self.fv[p] = v
        self.lv[p] = v
        self.pr[p] = 1
        self.sr[p] = 1
        self.br[p] = 1

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children
        a, b = 2 * x, 2 * x + 1
        self.sm[x] = self.sm[a] + self.sm[b]
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w
        k = self.PW[s - 1]
        self.fh[x] = (self.fh[a] * k + self.fh[b]) % _HP
        self.bh[x] = (self.bh[b] * k + self.bh[a]) % _HP
        self.orr[x] = self.orr[a] | self.orr[b]
        h, j = 1 << (s - 1), self.lv[a] == self.fv[b]
        pa, sb = self.pr[a], self.sr[b]
        self.br[x] = max(self.br[a], self.br[b], self.sr[a] + self.pr[b] if j else 0)
        self.pr[x] = pa + self.pr[b] if j and pa == h else pa
        self.sr[x] = sb + self.sr[a] if j and sb == h else sb
        self.fv[x] = self.fv[a]
        self.lv[x] = self.lv[b]

    def _rebuild(self, p):  # recompute every ancestor of leaf p
        s = 0
        while p > 1:
            p >>= 1
            s += 1
            self._pull(p, s)

    def _nodes(self, l, r):  # the O(logN) nodes covering a[l..r], left to right, each with its level
        n = self.n
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
        self._shrink(2 * x, s - 1, lim, f)
        self._shrink(2 * x + 1, s - 1, lim, f)
        self._pull(x, s)
