# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/seg-tree-sum-min-hash-pre-suf-best-npre-nsuf-nbest-xor-and-or-gcd-run-alt/template.py
# @operations: andAll gcdAll getAll hashAll isPalindrome leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX leftmostPrefixSumLtX leftmostPrefixSumLteX longestEqualRun longestPalCenteredAtI longestPalCenteredAtIPlusOne maxAltSubseqSum maxPrefixSum maxSubarraySum maxSuffixSum minAll minPrefixSum minSubarraySum minSuffixSum orAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeGcd rangeHash rangeHashReversed rangeMin rangeOrQuery rangeSum rangeXorQuery rangesEqual rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX rightmostSuffixSumLtX rightmostSuffixSumLteX sumAll xorAll
# @data-structure-type: seg-tree
# @complexities:
#   getAll: N
#   isPalindrome: log(N)
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   leftmostPrefixSumGtX: log(N)
#   leftmostPrefixSumGteX: log(N)
#   leftmostPrefixSumLtX: log(N)
#   leftmostPrefixSumLteX: log(N)
#   longestEqualRun: log(N)
#   maxAltSubseqSum: log(N)
#   maxPrefixSum: log(N)
#   maxSubarraySum: log(N)
#   maxSuffixSum: log(N)
#   minPrefixSum: log(N)
#   minSubarraySum: log(N)
#   minSuffixSum: log(N)
#   pointAdd: log(N)*log(U) ?
#   pointAssign: log(N)*log(U) ?
#   pointChmax: log(N)*log(U) ?
#   pointChmin: log(N)*log(U) ?
#   pointGet: log(N)
#   rangeAndQuery: log(N)
#   rangeGcd: log(N)+log(U) ?
#   rangeHash: log(N)
#   rangeHashReversed: log(N)
#   rangeMin: log(N)
#   rangeOrQuery: log(N)
#   rangeSum: log(N)
#   rangeXorQuery: log(N)
#   rangesEqual: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   rightmostSuffixSumGtX: log(N)
#   rightmostSuffixSumGteX: log(N)
#   rightmostSuffixSumLtX: log(N)
#   rightmostSuffixSumLteX: log(N)
#   longestPalCenteredAtI: log^2(N)
#   longestPalCenteredAtIPlusOne: log^2(N)
#   hashAll: log(N)
#   sumAll: log(N)
#   minAll: log(N)
#   gcdAll: log(N)+log(U) ?
#   xorAll: log(N)
#   andAll: log(N)
#   orAll: log(N)
#   build: N*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] mn[2*N] fh[2*N] bh[2*N] pre[2*N] suf[2*N] best[2*N] npre[2*N] nsuf[2*N] nbest[2*N] xr[2*N] an[2*N] orr[2*N] g[2*N] fv[2*N] lv[2*N] pr[2*N] sr[2*N] br[2*N] a00[2*N] a01[2*N] a10[2*N] a11[2*N]
#   tags: none
#   other: PW[1*log(N)]
#   note: leaves [n, 2n) hold each value's own aggregates; hash powers are per level (a covering node of level s has 2^s leaves)

# Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
# its sum, its min, its forward / backward hash (and B^size), its best prefix sum, its best suffix sum, its best
# subarray sum, its min prefix sum, its min suffix sum, its min subarray sum, its xor, its AND, its OR, its gcd, its
# first / last value and the equal runs at its ends and inside, its best alternating (+ - + ...) subsequence sum for
# each start / end sign over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing
# qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its level);
# an update rewrites a leaf, then its ancestors.
import random
from math import gcd


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


INF, NEG = float("inf"), float("-inf")


def _altJoin(A, B):  # A's part, then B's: (++, +-, -+, --) = best by (start sign, end sign)
    a0, a1, a2, a3 = A
    b0, b1, b2, b3 = B
    return (max(a0, b0, a0 + b2, a1 + b0), max(a1, b1, a0 + b3, a1 + b1),
            max(a2, b2, a2 + b2, a3 + b0), max(a3, b3, a2 + b3, a3 + b1))


class SegTree:
    __slots__ = ('n', 'h', 'sm', 'mn', 'fh', 'bh', 'pre', 'suf', 'best', 'npre', 'nsuf', 'nbest', 'xr', 'an', 'orr',
                 'g', 'fv', 'lv', 'pr', 'sr', 'br', 'a00', 'a01', 'a10', 'a11', 'PW')


    # O(N log U) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.mn = [0] * n + list(arr)
        self.fh = [0] * n + [(v + _HO) % _HP for v in arr]
        self.bh = [0] * n + [(v + _HO) % _HP for v in arr]
        self.pre = [0] * n + list(arr)
        self.suf = [0] * n + list(arr)
        self.best = [0] * n + list(arr)
        self.npre = [0] * n + list(arr)
        self.nsuf = [0] * n + list(arr)
        self.nbest = [0] * n + list(arr)
        self.xr = [0] * n + list(arr)
        self.an = [0] * n + list(arr)
        self.orr = [0] * n + list(arr)
        self.g = [0] * n + list(arr)
        self.fv = [0] * n + list(arr)
        self.lv = [0] * n + list(arr)
        self.pr = [0] * n + [1] * n
        self.sr = [0] * n + [1] * n
        self.br = [0] * n + [1] * n
        self.a00 = [0] * n + list(arr)
        self.a01 = [0] * n + [NEG] * n
        self.a10 = [0] * n + [NEG] * n
        self.a11 = [0] * n + [-v for v in arr]
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

    # O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] < x:  # the first covering node with a passing value: walk down it
                while t < n:
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
                    t = 2 * t if F[2 * t] <= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums); needs
    # 0 <= l <= r < n, else IndexError
    def leftmostPrefixSumGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostPrefixSumGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.pre
        acc = 0
        for t, s in self._nodes(l, r):
            if acc + P[t] > x:
                while t < n:
                    if acc + P[2 * t] > x:
                        t = 2 * t
                    else:
                        acc += sm[2 * t]
                        t = 2 * t + 1
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (a walk pruned by best prefix sums); needs
    # 0 <= l <= r < n, else IndexError
    def leftmostPrefixSumGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostPrefixSumGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.pre
        acc = 0
        for t, s in self._nodes(l, r):
            if acc + P[t] >= x:
                while t < n:
                    if acc + P[2 * t] >= x:
                        t = 2 * t
                    else:
                        acc += sm[2 * t]
                        t = 2 * t + 1
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] < x, or -1 (a walk pruned by min prefix sums); needs
    # 0 <= l <= r < n, else IndexError
    def leftmostPrefixSumLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostPrefixSumLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.npre
        acc = 0
        for t, s in self._nodes(l, r):
            if acc + P[t] < x:
                while t < n:
                    if acc + P[2 * t] < x:
                        t = 2 * t
                    else:
                        acc += sm[2 * t]
                        t = 2 * t + 1
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] <= x, or -1 (a walk pruned by min prefix sums); needs
    # 0 <= l <= r < n, else IndexError
    def leftmostPrefixSumLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostPrefixSumLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.npre
        acc = 0
        for t, s in self._nodes(l, r):
            if acc + P[t] <= x:
                while t < n:
                    if acc + P[2 * t] <= x:
                        t = 2 * t
                    else:
                        acc += sm[2 * t]
                        t = 2 * t + 1
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- the longest run of equal adjacent values in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def longestEqualRun(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"longestEqualRun: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs 0 <= l <= r < n, else
    # IndexError
    def maxAltSubseqSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxAltSubseqSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        a00, a01, a10, a11 = self.a00, self.a01, self.a10, self.a11
        ns = self._nodes(l, r)
        t = ns[0][0]
        c = (a00[t], a01[t], a10[t], a11[t])
        for t, _ in ns[1:]:
            c = _altJoin(c, (a00[t], a01[t], a10[t], a11[t]))
        return max(c[0], c[1])

    # O(logN) -- max of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def maxPrefixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxPrefixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, pre = self.sm, self.pre
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, acc = pre[t], sm[t]
        for t, _ in ns[1:]:
            if acc + pre[t] > res:
                res = acc + pre[t]
            acc += sm[t]
        return res

    # O(logN) -- max sum of a non-empty contiguous subarray of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def maxSubarraySum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxSubarraySum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, pre, suf, best = self.sm, self.pre, self.suf, self.best
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, q = best[t], suf[t]  # (q: the best sum ending at the right edge so far)
        for t, _ in ns[1:]:
            res = max(res, best[t], q + pre[t])
            q = max(suf[t], sm[t] + q)
        return res

    # O(logN) -- max of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def maxSuffixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxSuffixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, suf = self.sm, self.suf
        ns = self._nodes(l, r)
        t = ns[-1][0]
        res, acc = suf[t], sm[t]
        for t, _ in reversed(ns[:-1]):
            if acc + suf[t] > res:
                res = acc + suf[t]
            acc += sm[t]
        return res

    # O(logN) -- min of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def minPrefixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"minPrefixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, npre = self.sm, self.npre
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, acc = npre[t], sm[t]
        for t, _ in ns[1:]:
            if acc + npre[t] < res:
                res = acc + npre[t]
            acc += sm[t]
        return res

    # O(logN) -- min sum of a non-empty contiguous subarray of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def minSubarraySum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"minSubarraySum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, npre, nsuf, nbest = self.sm, self.npre, self.nsuf, self.nbest
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, q = nbest[t], nsuf[t]  # (q: the min sum ending at the right edge so far)
        for t, _ in ns[1:]:
            res = min(res, nbest[t], q + npre[t])
            q = min(nsuf[t], sm[t] + q)
        return res

    # O(logN) -- min of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def minSuffixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"minSuffixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, nsuf = self.sm, self.nsuf
        ns = self._nodes(l, r)
        t = ns[-1][0]
        res, acc = nsuf[t], sm[t]
        for t, _ in reversed(ns[:-1]):
            if acc + nsuf[t] < res:
                res = acc + nsuf[t]
            acc += sm[t]
        return res

    # O(logN * logU) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, self._leaf(p) + v)
        self._rebuild(p)

    # O(logN * logU) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN * logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN * logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        return self._leaf(p)

    # O(logN) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeAndQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAndQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, an = self.n, self.an
        res, lo, hi = -1, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res &= an[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res &= an[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN + logU) -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < n, else IndexError
    def rangeGcd(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeGcd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, g = self.n, self.g
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res = gcd(res, g[lo])
                lo += 1
            if hi & 1:
                hi -= 1
                res = gcd(res, g[hi])
            lo >>= 1
            hi >>= 1
        return res

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

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeOrQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeOrQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeXorQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeXorQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, xr = self.n, self.xr
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res ^= xr[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res ^= xr[hi]
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

    # O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] < x:  # the last covering node with a passing value: walk down it
                while t < n:
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
                    t = 2 * t + 1 if F[2 * t + 1] <= x else 2 * t
                return t - n
        return -1

    # O(logN) -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums); needs
    # 0 <= l <= r < n, else IndexError
    def rightmostSuffixSumGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostSuffixSumGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.suf
        acc = 0
        for t, s in reversed(self._nodes(l, r)):
            if acc + P[t] > x:
                while t < n:
                    if acc + P[2 * t + 1] > x:
                        t = 2 * t + 1
                    else:
                        acc += sm[2 * t + 1]
                        t = 2 * t
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (a walk pruned by best suffix sums); needs
    # 0 <= l <= r < n, else IndexError
    def rightmostSuffixSumGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostSuffixSumGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.suf
        acc = 0
        for t, s in reversed(self._nodes(l, r)):
            if acc + P[t] >= x:
                while t < n:
                    if acc + P[2 * t + 1] >= x:
                        t = 2 * t + 1
                    else:
                        acc += sm[2 * t + 1]
                        t = 2 * t
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- last i in [l, r] with a[i] + ... + a[r] < x, or -1 (a walk pruned by min suffix sums); needs
    # 0 <= l <= r < n, else IndexError
    def rightmostSuffixSumLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostSuffixSumLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.nsuf
        acc = 0
        for t, s in reversed(self._nodes(l, r)):
            if acc + P[t] < x:
                while t < n:
                    if acc + P[2 * t + 1] < x:
                        t = 2 * t + 1
                    else:
                        acc += sm[2 * t + 1]
                        t = 2 * t
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- last i in [l, r] with a[i] + ... + a[r] <= x, or -1 (a walk pruned by min suffix sums); needs
    # 0 <= l <= r < n, else IndexError
    def rightmostSuffixSumLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostSuffixSumLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.nsuf
        acc = 0
        for t, s in reversed(self._nodes(l, r)):
            if acc + P[t] <= x:
                while t < n:
                    if acc + P[2 * t + 1] <= x:
                        t = 2 * t + 1
                    else:
                        acc += sm[2 * t + 1]
                        t = 2 * t
                return t - n
            acc += sm[t]
        return -1

    # O(log^2(N)) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)): a binary search on
    # its radius, log N calls of isPalindrome; needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtI(self, i):
        n = self.n
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

    # O(log^2(N)) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the
    # empty
    # range, when there is none (so also for i = n - 1): a binary search on its radius, log N calls of isPalindrome;
    # needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtIPlusOne(self, i):
        n = self.n
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

    # O(log(N)) -- hash of the whole array a[0..n-1]: the same base and mod as rangeHash (shared by every structure
    # this run, so it compares with another one's hashes); needs n >= 1, else raises IndexError
    def hashAll(self):
        if self.n < 1:
            raise IndexError("hashAll: needs n >= 1")
        return self.rangeHash(0, self.n - 1)

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)

    # O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.n < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.n - 1)

    # O(log(N)+log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else raises IndexError
    def gcdAll(self):
        if self.n < 1:
            raise IndexError("gcdAll: needs n >= 1")
        return self.rangeGcd(0, self.n - 1)

    # O(log(N)) -- xor of the whole array a[0..n-1] (rangeXorQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def xorAll(self):
        if self.n < 1:
            raise IndexError("xorAll: needs n >= 1")
        return self.rangeXorQuery(0, self.n - 1)

    # O(log(N)) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def andAll(self):
        if self.n < 1:
            raise IndexError("andAll: needs n >= 1")
        return self.rangeAndQuery(0, self.n - 1)

    # O(log(N)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def orAll(self):
        if self.n < 1:
            raise IndexError("orAll: needs n >= 1")
        return self.rangeOrQuery(0, self.n - 1)

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.mn[p] = v
        self.fh[p] = (v + _HO) % _HP
        self.bh[p] = (v + _HO) % _HP
        self.pre[p] = v
        self.suf[p] = v
        self.best[p] = v
        self.npre[p] = v
        self.nsuf[p] = v
        self.nbest[p] = v
        self.xr[p] = v
        self.an[p] = v
        self.orr[p] = v
        self.g[p] = v
        self.fv[p] = v
        self.lv[p] = v
        self.pr[p] = 1
        self.sr[p] = 1
        self.br[p] = 1
        self.a00[p] = v
        self.a01[p] = NEG
        self.a10[p] = NEG
        self.a11[p] = -v

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children
        a, b = 2 * x, 2 * x + 1
        sm = self.sm
        self.pre[x] = max(self.pre[a], sm[a] + self.pre[b])
        self.suf[x] = max(self.suf[b], sm[b] + self.suf[a])
        self.best[x] = max(self.best[a], self.best[b], self.suf[a] + self.pre[b])
        self.npre[x] = min(self.npre[a], sm[a] + self.npre[b])
        self.nsuf[x] = min(self.nsuf[b], sm[b] + self.nsuf[a])
        self.nbest[x] = min(self.nbest[a], self.nbest[b], self.nsuf[a] + self.npre[b])
        sm[x] = sm[a] + sm[b]
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        k = self.PW[s - 1]
        self.fh[x] = (self.fh[a] * k + self.fh[b]) % _HP
        self.bh[x] = (self.bh[b] * k + self.bh[a]) % _HP
        self.xr[x] = self.xr[a] ^ self.xr[b]
        self.an[x] = self.an[a] & self.an[b]
        self.orr[x] = self.orr[a] | self.orr[b]
        self.g[x] = gcd(self.g[a], self.g[b])
        h, j = 1 << (s - 1), self.lv[a] == self.fv[b]
        pa, sb = self.pr[a], self.sr[b]
        self.br[x] = max(self.br[a], self.br[b], self.sr[a] + self.pr[b] if j else 0)
        self.pr[x] = pa + self.pr[b] if j and pa == h else pa
        self.sr[x] = sb + self.sr[a] if j and sb == h else sb
        self.fv[x] = self.fv[a]
        self.lv[x] = self.lv[b]
        A = (self.a00[a], self.a01[a], self.a10[a], self.a11[a])
        B = (self.a00[b], self.a01[b], self.a10[b], self.a11[b])
        self.a00[x], self.a01[x], self.a10[x], self.a11[x] = _altJoin(A, B)

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
