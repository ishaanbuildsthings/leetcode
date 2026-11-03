# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/isPalindrome-minPrefixSum-minSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeHash-rangeHashReversed-rangeSum-rangeXorQuery-rangesEqual/sparse.py
# @operations: isPalindrome minPrefixSum minSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeHash rangeHashReversed rangeSum rangeXorQuery rangesEqual
# @data-structure-type: seg-tree
# @complexities:
#   isPalindrome: log(U)
#   minPrefixSum: log(U)
#   minSuffixSum: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeHash: log(U)
#   rangeHashReversed: log(U)
#   rangeSum: log(U)
#   rangeXorQuery: log(U)
#   rangesEqual: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[4*log(U)] fh[4*log(U)] bh[4*log(U)] npre[4*log(U)] nsuf[4*log(U)] xr[4*log(U)]
#   tags: none
#   other: PW[1*log(U)] GS[1*log(U)] children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

# Segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
# position starting at 0; point updates and range queries in O(logU), U = hi - lo + 1; each node keeps its sum, its
# forward / backward hash (and B^size), its min prefix sum, its min suffix sum, its xor over its range. Ranges
# inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U positions from lo (the
# ones past hi are zeros nobody reads), so a node of level s covers 2^s positions; children are created on demand as
# blocks of zeros, right before anything descends past a node.
import random


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


class SparseSegTree:
    __slots__ = ('first', 'last', 'D', 'L', 'R', 'sm', 'fh', 'bh', 'npre', 'nsuf', 'xr', 'PW', 'GS')


    # O(1) -- all zeros over [lo, hi]; any range of integers works (lo <= hi)
    def __init__(self, lo, hi):
        self.first, self.last = lo, hi  # (the index range: lo / hi are the clamp tags' names)
        self.D = (hi - lo).bit_length()  # the root's level: 2^D >= hi - lo + 1
        self.L, self.R = [0], [0]  # node 0: none (node 1 is the root)
        self.sm = [0]
        self.fh = [0]
        self.bh = [0]
        self.npre = [0]
        self.nsuf = [0]
        self.xr = [0]
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

    # O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeSum(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        sm, res = self.sm, 0
        for t, _ in self._nodes(l, r):
            res += sm[t]
        return res

    # O(logU) -- a[l] ^ ... ^ a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeXorQuery(self, l, r):
        if not self.first <= l <= r <= self.last:
            raise IndexError(f"rangeXorQuery: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        xr, res = self.xr, 0
        for t, _ in self._nodes(l, r):
            res ^= xr[t]
        return res

    # O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    # lo <= l1 <= r1 <= hi and lo <= l2 <= r2 <= hi, else IndexError
    def rangesEqual(self, l1, r1, l2, r2):
        if not (self.first <= l1 <= r1 <= self.last and self.first <= l2 <= r2 <= self.last):
            raise IndexError(f"rangesEqual: needs lo <= l1 <= r1 <= hi and lo <= l2 <= r2 <= hi, got "
                             f"l1 = {l1}, r1 = {r1}, l2 = {l2}, r2 = {r2}")
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # ---- internals ----

    def _newZero(self, s):  # a new node: a block of 2^s zeros
        h = _HO * self.GS[s] % _HP  # (0 hashes as _HO)
        self.L.append(0)
        self.R.append(0)
        self.sm.append(0)
        self.fh.append(h)
        self.bh.append(h)
        self.npre.append(0)
        self.nsuf.append(0)
        self.xr.append(0)
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
        self.npre[p] = v
        self.nsuf[p] = v
        self.xr[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children
        a, b = self.L[x], self.R[x]
        sm = self.sm
        self.npre[x] = min(self.npre[a], sm[a] + self.npre[b])
        self.nsuf[x] = min(self.nsuf[b], sm[b] + self.nsuf[a])
        sm[x] = sm[a] + sm[b]
        k = self.PW[s - 1]
        self.fh[x] = (self.fh[a] * k + self.fh[b]) % _HP
        self.bh[x] = (self.bh[b] * k + self.bh[a]) % _HP
        self.xr[x] = self.xr[a] ^ self.xr[b]
