# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/beats-sum-min-max-hash-npre-nsuf-nbest-alt-updates-div-mod-sqrt/sparse.py
# @operations: isPalindrome leftmostGtX leftmostGteX leftmostLtX leftmostLteX leftmostPrefixSumLtX leftmostPrefixSumLteX maxAltSubseqSum minPrefixSum minSubarraySum minSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv rangeFloorSqrt rangeHash rangeHashReversed rangeMax rangeMin rangeMod rangeSum rangesEqual rightmostGtX rightmostGteX rightmostLtX rightmostLteX rightmostSuffixSumLtX rightmostSuffixSumLteX
# @data-structure-type: beats
# @complexities:
#   isPalindrome: log(U)
#   leftmostGtX: log(U)
#   leftmostGteX: log(U)
#   leftmostLtX: log(U)
#   leftmostLteX: log(U)
#   leftmostPrefixSumLtX: log(U)
#   leftmostPrefixSumLteX: log(U)
#   maxAltSubseqSum: log(U)
#   minPrefixSum: log(U)
#   minSubarraySum: log(U)
#   minSuffixSum: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeFloorDiv: log(U)*log(U) amortized
#   rangeFloorSqrt: log(U)*log(log(U)) amortized
#   rangeHash: log(U)
#   rangeHashReversed: log(U)
#   rangeMax: log(U)
#   rangeMin: log(U)
#   rangeMod: log(U)*log(U) amortized
#   rangeSum: log(U)
#   rangesEqual: log(U)
#   rightmostGtX: log(U)
#   rightmostGteX: log(U)
#   rightmostLtX: log(U)
#   rightmostLteX: log(U)
#   rightmostSuffixSumLtX: log(U)
#   rightmostSuffixSumLteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[4*log(U)] mn[4*log(U)] mx[4*log(U)] fh[4*log(U)] bh[4*log(U)] npre[4*log(U)] nsuf[4*log(U)] nbest[4*log(U)] a00[4*log(U)] a01[4*log(U)] a10[4*log(U)] a11[4*log(U)]
#   tags: none
#   other: PW[1*log(U)] GS[1*log(U)] children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates), amortized for the shrink walks; node data per field, children L / R

# Shrink segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
# position starting at 0; range updates (rangeFloorDiv, rangeMod, rangeFloorSqrt) and range queries in O(logU), U = hi
# - lo + 1; each node keeps its sum, its min, its max, its forward / backward hash (and B^size), its min prefix sum,
# its min suffix sum, its min subarray sum, its best alternating (+ - + ...) subsequence sum for each start / end sign
# over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U
# positions from lo (the ones past hi are zeros nobody reads), so a node of level s covers 2^s positions; children are
# created on demand as blocks of zeros, right before anything descends past a node. mod / floor div / floor sqrt walk
# down every node whose max still changes.
import random
from math import isqrt


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


INF, NEG = float("inf"), float("-inf")


def _altJoin(A, B):  # A's part, then B's: (++, +-, -+, --) = best by (start sign, end sign)
    a0, a1, a2, a3 = A
    b0, b1, b2, b3 = B
    return (max(a0, b0, a0 + b2, a1 + b0), max(a1, b1, a0 + b3, a1 + b1),
            max(a2, b2, a2 + b2, a3 + b0), max(a3, b3, a2 + b3, a3 + b1))


class SparseShrinkSegTree:
    __slots__ = ('first', 'last', 'D', 'L', 'R', 'sm', 'mn', 'mx', 'fh', 'bh', 'npre', 'nsuf', 'nbest', 'a00', 'a01',
                 'a10', 'a11', 'PW', 'GS')


    # O(1) -- all zeros over [lo, hi]; any range of integers works (lo <= hi)
    def __init__(self, lo, hi):
        self.first, self.last = lo, hi  # (the index range: lo / hi are the clamp tags' names)
        self.D = (hi - lo).bit_length()  # the root's level: 2^D >= hi - lo + 1
        self.L, self.R = [0], [0]  # node 0: none (node 1 is the root)
        self.sm = [0]
        self.mn = [0]
        self.mx = [0]
        self.fh = [0]
        self.bh = [0]
        self.npre = [0]
        self.nsuf = [0]
        self.nbest = [0]
        self.a00 = [0]
        self.a01 = [0]
        self.a10 = [0]
        self.a11 = [0]
        pw = self.PW = [_HB]  # PW[s] = B^(2^s), GS[s] = 1 + B + ... + B^(2^s - 1): per level
        gs = self.GS = [1]
        for k in range(self.D):
            gs.append((gs[k] * pw[k] + gs[k]) % _HP)
            pw.append(pw[k] * pw[k] % _HP)
        self._newZero(self.D)

    # O(logN) -- is a[l..r] a palindrome (its two hashes agree); needs lo <= l <= r <= hi, else IndexError
    def isPalindrome(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"isPalindrome: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        fh, bh, pw, P, f, b, p = self.fh, self.bh, self.PW, _HP, 0, 0, 1
        for t, s in self._nodes(l, r):
            f = (f * pw[s] + fh[t]) % P
            b = (bh[t] * p + b) % P
            p = p * pw[s] % P
        return f == b

    # O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostGtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[L[t]] > x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

    # O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostGteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] >= x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[L[t]] >= x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

    # O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostLtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mn, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] < x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[L[t]] < x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

    # O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostLteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mn, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] <= x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[L[t]] <= x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] < x, or lo - 1 (a walk pruned by min prefix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostPrefixSumLtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostPrefixSumLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.npre, self.L, self.R
        acc = 0
        for t, s, tl in self._cover(l, r):
            if acc + P[t] < x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[L[t]] < x:
                        t = L[t]
                    else:
                        acc += sm[L[t]]
                        t, tl = R[t], tl + (1 << s)
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] <= x, or lo - 1 (a walk pruned by min prefix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostPrefixSumLteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"leftmostPrefixSumLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.npre, self.L, self.R
        acc = 0
        for t, s, tl in self._cover(l, r):
            if acc + P[t] <= x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[L[t]] <= x:
                        t = L[t]
                    else:
                        acc += sm[L[t]]
                        t, tl = R[t], tl + (1 << s)
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs lo <= l <= r <= hi, else
    # IndexError
    def maxAltSubseqSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"maxAltSubseqSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        a00, a01, a10, a11 = self.a00, self.a01, self.a10, self.a11
        ns = self._nodes(l, r)
        t = ns[0][0]
        c = (a00[t], a01[t], a10[t], a11[t])
        for t, _ in ns[1:]:
            c = _altJoin(c, (a00[t], a01[t], a10[t], a11[t]))
        return max(c[0], c[1])

    # O(logN) -- min of a[l] + ... + a[i] over i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def minPrefixSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"minPrefixSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, npre = self.sm, self.npre
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, acc = npre[t], sm[t]
        for t, _ in ns[1:]:
            if acc + npre[t] < res:
                res = acc + npre[t]
            acc += sm[t]
        return res

    # O(logN) -- min sum of a non-empty contiguous subarray of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def minSubarraySum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"minSubarraySum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, npre, nsuf, nbest = self.sm, self.npre, self.nsuf, self.nbest
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, q = nbest[t], nsuf[t]  # (q: the min sum ending at the right edge so far)
        for t, _ in ns[1:]:
            res = min(res, nbest[t], q + npre[t])
            q = min(nsuf[t], sm[t] + q)
        return res

    # O(logN) -- min of a[i] + ... + a[r] over i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def minSuffixSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"minSuffixSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, nsuf = self.sm, self.nsuf
        ns = self._nodes(l, r)
        t = ns[-1][0]
        res, acc = nsuf[t], sm[t]
        for t, _ in reversed(ns[:-1]):
            if acc + nsuf[t] < res:
                res = acc + nsuf[t]
            acc += sm[t]
        return res

    # O(logU) -- a[i] += v; needs lo <= i <= hi, else IndexError
    def pointAdd(self, i, v):
        if not self.first <= i <= self.last:
            raise IndexError(f"pointAdd: needs lo <= i <= hi, got i = {i}")
        x, path = self._leafOf(i)
        self._setLeaf(x, self._leaf(x) + v)
        self._up(path)

    # O(logU) -- a[i] = v; needs lo <= i <= hi, else IndexError
    def pointAssign(self, i, v):
        if not self.first <= i <= self.last:
            raise IndexError(f"pointAssign: needs lo <= i <= hi, got i = {i}")
        x, path = self._leafOf(i)
        self._setLeaf(x, v)
        self._up(path)

    # O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else IndexError
    def pointChmax(self, i, v):
        if not self.first <= i <= self.last:
            raise IndexError(f"pointChmax: needs lo <= i <= hi, got i = {i}")
        x, path = self._leafOf(i)
        self._setLeaf(x, max(self._leaf(x), v))
        self._up(path)

    # O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else IndexError
    def pointChmin(self, i, v):
        if not self.first <= i <= self.last:
            raise IndexError(f"pointChmin: needs lo <= i <= hi, got i = {i}")
        x, path = self._leafOf(i)
        self._setLeaf(x, min(self._leaf(x), v))
        self._up(path)

    # O(logU) -- a[i]; needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.first <= i <= self.last:
            raise IndexError(f"pointGet: needs lo <= i <= hi, got i = {i}")
        return self._leaf(self._leafOf(i)[0])

    # amortized O(logU * logU) -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing); needs
    # lo <= l <= r <= hi, else IndexError
    def rangeFloorDiv(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeFloorDiv: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if x >= 2:
            self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._shrink(t, s, 1, lambda v: v // x))

    # amortized O(logU * loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0); needs lo <= l <= r <= hi,
    # else IndexError
    def rangeFloorSqrt(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeFloorSqrt: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._shrink(t, s, 2, isqrt))

    # O(logN) -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    # lo <= l <= r <= hi, else IndexError
    def rangeHash(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeHash: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        fh, pw, P, res = self.fh, self.PW, _HP, 0
        for t, s in self._nodes(l, r):
            res = (res * pw[s] + fh[t]) % P
        return res

    # O(logN) -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs lo <= l <= r <= hi,
    # else IndexError
    def rangeHashReversed(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeHashReversed: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        bh, pw, P, res, p = self.bh, self.PW, _HP, 0, 1
        for t, s in self._nodes(l, r):  # (each node read backwards goes in front of what came before it)
            res = (bh[t] * p + res) % P
            p = p * pw[s] % P
        return res

    # O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMax(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeMax: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        mx, res = self.mx, NEG
        for t, _ in self._nodes(l, r):
            if mx[t] > res:
                res = mx[t]
        return res

    # O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMin(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeMin: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        mn, res = self.mn, INF
        for t, _ in self._nodes(l, r):
            if mn[t] < res:
                res = mn[t]
        return res

    # amortized O(logU * logU) -- a[i] %= x for i in [l, r] (values >= 0, x >= 1); needs lo <= l <= r <= hi, else
    # IndexError
    def rangeMod(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeMod: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if x >= 1:
            self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._shrink(t, s, x, lambda v: v % x))

    # O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, res = self.sm, 0
        for t, _ in self._nodes(l, r):
            res += sm[t]
        return res

    # O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    # lo <= l1 <= r1 <= hi and lo <= l2 <= r2 <= hi, else IndexError
    def rangesEqual(self, l1, r1, l2, r2):
        if not (self.first <= l1 <= r1 <= self.last and self.first <= l2 <= r2 <= self.last):
            raise IndexError(f"rangesEqual: needs lo <= l1 <= r1 <= hi and lo <= l2 <= r2 <= hi, got "
                             f"l1 = {l1}, r1 = {r1}, l2 = {l2}, r2 = {r2}")
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostGtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[R[t]] > x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]
                return tl
        return self.first - 1

    # O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostGteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] >= x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[R[t]] >= x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]
                return tl
        return self.first - 1

    # O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostLtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mn, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] < x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[R[t]] < x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]
                return tl
        return self.first - 1

    # O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostLteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F, L, R = self.mn, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] <= x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    s -= 1
                    if F[R[t]] <= x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]
                return tl
        return self.first - 1

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] < x, or lo - 1 (a walk pruned by min suffix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostSuffixSumLtX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostSuffixSumLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.nsuf, self.L, self.R
        acc = 0
        for t, s, tl in reversed(self._cover(l, r)):
            if acc + P[t] < x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[R[t]] < x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        acc += sm[R[t]]
                        t = L[t]
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] <= x, or lo - 1 (a walk pruned by min suffix sums); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostSuffixSumLteX(self, l, r, x):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rightmostSuffixSumLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, P, L, R = self.sm, self.nsuf, self.L, self.R
        acc = 0
        for t, s, tl in reversed(self._cover(l, r)):
            if acc + P[t] <= x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[R[t]] <= x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        acc += sm[R[t]]
                        t = L[t]
                return tl
            acc += sm[t]
        return self.first - 1

    # ---- internals ----

    def _newZero(self, s):  # a new node: a block of 2^s zeros
        h = _HO * self.GS[s] % _HP  # (0 hashes as _HO)
        self.L.append(0)
        self.R.append(0)
        self.sm.append(0)
        self.mn.append(0)
        self.mx.append(0)
        self.fh.append(h)
        self.bh.append(h)
        self.npre.append(0)
        self.nsuf.append(0)
        self.nbest.append(0)
        self.a00.append(0)
        self.a01.append(0 if s else NEG)
        self.a10.append(0 if s else NEG)
        self.a11.append(0)
        return len(self.L) - 1

    def _kids(self, x, s):  # create node x's children (blocks of zeros) if it has none yet
        if not self.L[x]:
            a = self._newZero(s - 1)
            self.L[x], self.R[x] = a, self._newZero(s - 1)

    def _cover(self, l, r):  # the nodes covering a[l..r], left to right, as (node, level, first index)
        out = []
        self._collect(1, self.D, self.first, l, r, out)
        return out

    def _collect(self, x, s, tl, l, r, out):
        if l <= tl and tl + (1 << s) - 1 <= r:
            out.append((x, s, tl))
            return
        self._kids(x, s)
        m = tl + (1 << (s - 1))
        if l < m:
            self._collect(self.L[x], s - 1, tl, l, r, out)
        if r >= m:
            self._collect(self.R[x], s - 1, m, l, r, out)

    def _nodes(self, l, r):  # the covering nodes left to right, each with its level
        return [(x, s) for x, s, _ in self._cover(l, r)]

    def _update(self, x, s, tl, l, r, f):  # f(node, level, first index) on every node covering a[l..r], then pull up
        if l <= tl and tl + (1 << s) - 1 <= r:
            f(x, s, tl)
            return
        self._kids(x, s)
        m = tl + (1 << (s - 1))
        if l < m:
            self._update(self.L[x], s - 1, tl, l, r, f)
        if r >= m:
            self._update(self.R[x], s - 1, m, l, r, f)
        self._pull(x, s)

    def _leafOf(self, i):  # (the leaf holding a[i], the nodes above it top-down), every tag on the way pushed
        x, s, tl, path = 1, self.D, self.first, []
        while s:
            self._kids(x, s)
            path.append(x)
            s -= 1
            if i >= tl + (1 << s):
                tl += 1 << s
                x = self.R[x]
            else:
                x = self.L[x]
        return x, path

    def _up(self, path):  # recompute the nodes of path, deepest first (path[k] has level D - k)
        for k in range(len(path) - 1, -1, -1):
            self._pull(path[k], self.D - k)

    def _shrink(self, x, s, lim, f):  # every value v >= lim under node x (level s) becomes f(v) (the rest are fixed)
        if self.mx[x] < lim:
            return
        if s == 0:
            self._setLeaf(x, f(self.mx[x]))
            return
        self._kids(x, s)
        self._shrink(self.L[x], s - 1, lim, f)
        self._shrink(self.R[x], s - 1, lim, f)
        self._pull(x, s)

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.mn[p] = v
        self.mx[p] = v
        self.fh[p] = (v + _HO) % _HP
        self.bh[p] = (v + _HO) % _HP
        self.npre[p] = v
        self.nsuf[p] = v
        self.nbest[p] = v
        self.a00[p] = v
        self.a01[p] = NEG
        self.a10[p] = NEG
        self.a11[p] = -v

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children
        a, b = self.L[x], self.R[x]
        sm = self.sm
        self.npre[x] = min(self.npre[a], sm[a] + self.npre[b])
        self.nsuf[x] = min(self.nsuf[b], sm[b] + self.nsuf[a])
        self.nbest[x] = min(self.nbest[a], self.nbest[b], self.nsuf[a] + self.npre[b])
        sm[x] = sm[a] + sm[b]
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w
        k = self.PW[s - 1]
        self.fh[x] = (self.fh[a] * k + self.fh[b]) % _HP
        self.bh[x] = (self.bh[b] * k + self.bh[a]) % _HP
        A = (self.a00[a], self.a01[a], self.a10[a], self.a11[a])
        B = (self.a00[b], self.a01[b], self.a10[b], self.a11[b])
        self.a00[x], self.a01[x], self.a10[x], self.a11[x] = _altJoin(A, B)
