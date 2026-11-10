# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/isPalindrome-longestEqualRun-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeGcd-rangeHash-rangeHashReversed-rangesEqual/template.py
# @operations: gcdAll getAll hashAll isPalindrome longestEqualRun longestPalCenteredAtI longestPalCenteredAtIPlusOne pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd rangeHash rangeHashReversed rangesEqual
# @data-structure-type: seg-tree
# @complexities:
#   getAll: N
#   isPalindrome: log(N)
#   longestEqualRun: log(N)
#   pointAdd: log(N)*log(U) ?
#   pointAssign: log(N)*log(U) ?
#   pointChmax: log(N)*log(U) ?
#   pointChmin: log(N)*log(U) ?
#   pointGet: log(N)
#   rangeGcd: log(N)+log(U) ?
#   rangeHash: log(N)
#   rangeHashReversed: log(N)
#   rangesEqual: log(N)
#   longestPalCenteredAtI: log^2(N)
#   longestPalCenteredAtIPlusOne: log^2(N)
#   hashAll: log(N)
#   gcdAll: log(N)+log(U) ?
#   build: N*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: fh[2*N] bh[2*N] g[2*N] fv[2*N] lv[2*N] pr[2*N] sr[2*N] br[2*N]
#   tags: none
#   other: PW[1*log(N)]
#   note: leaves [n, 2n) hold each value's own aggregates; hash powers are per level (a covering node of level s has 2^s leaves)

# Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
# its forward / backward hash (and B^size), its gcd, its first / last value and the equal runs at its ends and inside
# over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies. Leaves
# tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its level); an update rewrites
# a leaf, then its ancestors.
import random
from math import gcd


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


class SegTree:
    __slots__ = ('n', 'h', 'fh', 'bh', 'g', 'fv', 'lv', 'pr', 'sr', 'br', 'PW')


    # O(N log U) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.fh = [0] * n + [(v + _HO) % _HP for v in arr]
        self.bh = [0] * n + [(v + _HO) % _HP for v in arr]
        self.g = [0] * n + list(arr)
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
        return self.fv[self.n:]

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

    # O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    # 0 <= l1 <= r1 < n and 0 <= l2 <= r2 < n, else IndexError
    def rangesEqual(self, l1, r1, l2, r2):
        if not (0 <= l1 <= r1 < self.n and 0 <= l2 <= r2 < self.n):
            raise IndexError(f"rangesEqual: needs 0 <= l1 <= r1 < n and 0 <= l2 <= r2 < n, got "
                             f"l1 = {l1}, r1 = {r1}, l2 = {l2}, r2 = {r2}, n = {self.n}")
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

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

    # O(log(N)+log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else raises IndexError
    def gcdAll(self):
        if self.n < 1:
            raise IndexError("gcdAll: needs n >= 1")
        return self.rangeGcd(0, self.n - 1)

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.fh[p] = (v + _HO) % _HP
        self.bh[p] = (v + _HO) % _HP
        self.g[p] = v
        self.fv[p] = v
        self.lv[p] = v
        self.pr[p] = 1
        self.sr[p] = 1
        self.br[p] = 1

    def _leaf(self, p):  # the value at leaf p
        return self.fv[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children
        a, b = 2 * x, 2 * x + 1
        k = self.PW[s - 1]
        self.fh[x] = (self.fh[a] * k + self.fh[b]) % _HP
        self.bh[x] = (self.bh[b] * k + self.bh[a]) % _HP
        self.g[x] = gcd(self.g[a], self.g[b])
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
