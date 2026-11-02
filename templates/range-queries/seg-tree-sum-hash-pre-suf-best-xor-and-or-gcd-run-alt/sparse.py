# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/seg-tree-sum-hash-pre-suf-best-xor-and-or-gcd-run-alt/sparse.py
# @operations: isPalindrome leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxAltSubseqSum maxPrefixSum maxSubarraySum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeGcd rangeHash rangeHashReversed rangeOrQuery rangeSum rangeXorQuery rangesEqual rightmostSuffixSumGtX rightmostSuffixSumGteX
# @data-structure-type: seg-tree
# @complexities:
#   isPalindrome: log(U)
#   leftmostPrefixSumGtX: log(U)
#   leftmostPrefixSumGteX: log(U)
#   longestEqualRun: log(U)
#   maxAltSubseqSum: log(U)
#   maxPrefixSum: log(U)
#   maxSubarraySum: log(U)
#   maxSuffixSum: log(U)
#   pointAdd: log(U)*log(U) ?
#   pointAssign: log(U)*log(U) ?
#   pointChmax: log(U)*log(U) ?
#   pointChmin: log(U)*log(U) ?
#   pointGet: log(U)
#   rangeAndQuery: log(U)
#   rangeGcd: log(U) ?
#   rangeHash: log(U)
#   rangeHashReversed: log(U)
#   rangeOrQuery: log(U)
#   rangeSum: log(U)
#   rangeXorQuery: log(U)
#   rangesEqual: log(U)
#   rightmostSuffixSumGtX: log(U)
#   rightmostSuffixSumGteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[4*log(U)] fh[4*log(U)] bh[4*log(U)] pre[4*log(U)] suf[4*log(U)] best[4*log(U)] xr[4*log(U)] an[4*log(U)] orr[4*log(U)] g[4*log(U)] fv[4*log(U)] lv[4*log(U)] pr[4*log(U)] sr[4*log(U)] br[4*log(U)] a00[4*log(U)] a01[4*log(U)] a10[4*log(U)] a11[4*log(U)]
#   tags: none
#   other: PW[1*log(U)] GS[1*log(U)] children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

# Segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
# position starting at 0; point updates and range queries in O(logU), U = hi - lo + 1; each node keeps its sum, its
# forward / backward hash (and B^size), its best prefix sum, its best suffix sum, its best subarray sum, its xor, its
# AND, its OR, its gcd, its first / last value and the equal runs at its ends and inside, its best alternating (+ - +
# ...) subsequence sum for each start / end sign over its range. Ranges inclusive [l, r]; searches return lo - 1 when
# nothing qualifies. The root covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so a node
# of level s covers 2^s positions; children are created on demand as blocks of zeros, right before anything descends
# past a node.
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


class SparseSegTree:
    __slots__ = ('first', 'last', 'D', 'L', 'R', 'sm', 'fh', 'bh', 'pre', 'suf', 'best', 'xr', 'an', 'orr', 'g', 'fv',
                 'lv', 'pr', 'sr', 'br', 'a00', 'a01', 'a10', 'a11', 'PW', 'GS')


    # O(1) -- all zeros over [lo, hi]; any range of integers works (lo <= hi)
    def __init__(self, lo, hi):
        self.first, self.last = lo, hi  # (the index range: lo / hi are the clamp tags' names)
        self.D = (hi - lo).bit_length()  # the root's level: 2^D >= hi - lo + 1
        self.L, self.R = [0], [0]  # node 0: none (node 1 is the root)
        self.sm = [0]
        self.fh = [0]
        self.bh = [0]
        self.pre = [0]
        self.suf = [0]
        self.best = [0]
        self.xr = [0]
        self.an = [-1]
        self.orr = [0]
        self.g = [0]
        self.fv = [0]
        self.lv = [0]
        self.pr = [0]
        self.sr = [0]
        self.br = [0]
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

    # O(logN) -- is a[l..r] a palindrome (its two hashes agree)
    def isPalindrome(self, l, r):
        fh, bh, pw, P, f, b, p = self.fh, self.bh, self.PW, _HP, 0, 0, 1
        for t, s in self._nodes(l, r):
            f = (f * pw[s] + fh[t]) % P
            b = (bh[t] * p + b) % P
            p = p * pw[s] % P
        return f == b

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1 (a walk pruned by best prefix sums)
    def leftmostPrefixSumGtX(self, l, r, x):
        sm, P, L, R = self.sm, self.pre, self.L, self.R
        acc = 0
        for t, s, tl in self._cover(l, r):
            if acc + P[t] > x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[L[t]] > x:
                        t = L[t]
                    else:
                        acc += sm[L[t]]
                        t, tl = R[t], tl + (1 << s)
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1 (a walk pruned by best prefix sums)
    def leftmostPrefixSumGteX(self, l, r, x):
        sm, P, L, R = self.sm, self.pre, self.L, self.R
        acc = 0
        for t, s, tl in self._cover(l, r):
            if acc + P[t] >= x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[L[t]] >= x:
                        t = L[t]
                    else:
                        acc += sm[L[t]]
                        t, tl = R[t], tl + (1 << s)
                return tl
            acc += sm[t]
        return self.first - 1

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

    # O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]
    def maxAltSubseqSum(self, l, r):
        a00, a01, a10, a11 = self.a00, self.a01, self.a10, self.a11
        ns = self._nodes(l, r)
        t = ns[0][0]
        c = (a00[t], a01[t], a10[t], a11[t])
        for t, _ in ns[1:]:
            c = _altJoin(c, (a00[t], a01[t], a10[t], a11[t]))
        return max(c[0], c[1])

    # O(logN) -- max of a[l] + ... + a[i] over i in [l, r]
    def maxPrefixSum(self, l, r):
        sm, pre = self.sm, self.pre
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, acc = pre[t], sm[t]
        for t, _ in ns[1:]:
            if acc + pre[t] > res:
                res = acc + pre[t]
            acc += sm[t]
        return res

    # O(logN) -- max sum of a non-empty contiguous subarray of a[l..r]
    def maxSubarraySum(self, l, r):
        sm, pre, suf, best = self.sm, self.pre, self.suf, self.best
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, q = best[t], suf[t]  # (q: the best sum ending at the right edge so far)
        for t, _ in ns[1:]:
            res = max(res, best[t], q + pre[t])
            q = max(suf[t], sm[t] + q)
        return res

    # O(logN) -- max of a[i] + ... + a[r] over i in [l, r]
    def maxSuffixSum(self, l, r):
        sm, suf = self.sm, self.suf
        ns = self._nodes(l, r)
        t = ns[-1][0]
        res, acc = suf[t], sm[t]
        for t, _ in reversed(ns[:-1]):
            if acc + suf[t] > res:
                res = acc + suf[t]
            acc += sm[t]
        return res

    # O(logU * logU) -- a[i] += v
    def pointAdd(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, self._leaf(x) + v)
        self._up(path)

    # O(logU * logU) -- a[i] = v
    def pointAssign(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, v)
        self._up(path)

    # O(logU * logU) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, max(self._leaf(x), v))
        self._up(path)

    # O(logU * logU) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, min(self._leaf(x), v))
        self._up(path)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._leaf(self._leafOf(i)[0])

    # O(logU) -- a[l] & ... & a[r]
    def rangeAndQuery(self, l, r):
        an, res = self.an, -1
        for t, _ in self._nodes(l, r):
            res &= an[t]
        return res

    # O(logU + logU) -- gcd of |a[l]|, ..., |a[r]|
    def rangeGcd(self, l, r):
        g, res = self.g, 0
        for t, _ in self._nodes(l, r):
            res = gcd(res, g[t])
        return res

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

    # O(logU) -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r):
        orr, res = self.orr, 0
        for t, _ in self._nodes(l, r):
            res |= orr[t]
        return res

    # O(logU) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        sm, res = self.sm, 0
        for t, _ in self._nodes(l, r):
            res += sm[t]
        return res

    # O(logU) -- a[l] ^ ... ^ a[r]
    def rangeXorQuery(self, l, r):
        xr, res = self.xr, 0
        for t, _ in self._nodes(l, r):
            res ^= xr[t]
        return res

    # O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] > x, or lo - 1 (a walk pruned by best suffix sums)
    def rightmostSuffixSumGtX(self, l, r, x):
        sm, P, L, R = self.sm, self.suf, self.L, self.R
        acc = 0
        for t, s, tl in reversed(self._cover(l, r)):
            if acc + P[t] > x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[R[t]] > x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        acc += sm[R[t]]
                        t = L[t]
                return tl
            acc += sm[t]
        return self.first - 1

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] >= x, or lo - 1 (a walk pruned by best suffix sums)
    def rightmostSuffixSumGteX(self, l, r, x):
        sm, P, L, R = self.sm, self.suf, self.L, self.R
        acc = 0
        for t, s, tl in reversed(self._cover(l, r)):
            if acc + P[t] >= x:
                while s:
                    self._kids(t, s)
                    s -= 1
                    if acc + P[R[t]] >= x:
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
        self.fh.append(h)
        self.bh.append(h)
        self.pre.append(0)
        self.suf.append(0)
        self.best.append(0)
        self.xr.append(0)
        self.an.append(0)
        self.orr.append(0)
        self.g.append(0)
        self.fv.append(0)
        self.lv.append(0)
        self.pr.append(1 << s)
        self.sr.append(1 << s)
        self.br.append(1 << s)
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

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.fh[p] = (v + _HO) % _HP
        self.bh[p] = (v + _HO) % _HP
        self.pre[p] = v
        self.suf[p] = v
        self.best[p] = v
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
        a, b = self.L[x], self.R[x]
        sm = self.sm
        self.pre[x] = max(self.pre[a], sm[a] + self.pre[b])
        self.suf[x] = max(self.suf[b], sm[b] + self.suf[a])
        self.best[x] = max(self.best[a], self.best[b], self.suf[a] + self.pre[b])
        sm[x] = sm[a] + sm[b]
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
