# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/isPalindrome-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeHash-rangeHashReversed-rangeSum-rangesEqual/letters.py
# @operations: getAll isPalindrome pointAssign pointChmax pointChmin pointGet rangeHash rangeHashReversed rangesEqual
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   isPalindrome: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeHash: log(N)
#   rangeHashReversed: log(N)
#   rangesEqual: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] fh[2*N] bh[2*N]
#   tags: add[1*N]
#   other: PW[1*log(N)] GS[1*log(N)]
#   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only; hash powers are per level (a covering node of level s has 2^s leaves)

# Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
# operations that make sense on characters are listed.
# Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAdd) and range queries in O(logN);
# each node keeps its sum, its forward / backward hash (and B^size) over its range. All indices 0-based, ranges
# inclusive [l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is
# a perfect subtree of 2^s leaves (s = its level), and every internal node holds its pending tags ("applied here, not
# yet to my children"): an update pushes the tags on its two boundary leaf paths, tags the covering nodes, then
# rebuilds both paths, each node redoing its own pending tag.
import random


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


class LazySegTree:
    __slots__ = ('n', 'h', 'sm', 'fh', 'bh', 'add', 'PW', 'GS')


    # O(N) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.fh = [0] * n + [(ord(v) + _HO) % _HP for v in arr]
        self.bh = [0] * n + [(ord(v) + _HO) % _HP for v in arr]
        self.add = [0] * n
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

    # O(logN) -- is a[l..r] a palindrome (its two hashes agree)
    def isPalindrome(self, l, r):
        fh, bh, pw, P, f, b, p = self.fh, self.bh, self.PW, _HP, 0, 0, 1
        for t, s in self._nodes(l, r):
            f = (f * pw[s] + fh[t]) % P
            b = (bh[t] * p + b) % P
            p = p * pw[s] % P
        return f == b

    # O(logN) -- a[i] = v
    def pointAssign(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        self._pushPath(p)
        return self._leaf(p)

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

    # O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.fh[p] = (ord(v) + _HO) % _HP
        self.bh[p] = (ord(v) + _HO) % _HP

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children, then redo its own pending tags
        a, b = 2 * x, 2 * x + 1
        self.sm[x] = self.sm[a] + self.sm[b]
        k = self.PW[s - 1]
        self.fh[x] = (self.fh[a] * k + self.fh[b]) % _HP
        self.bh[x] = (self.bh[b] * k + self.bh[a]) % _HP
        if self.add[x]:
            self._setAdd(x, s, self.add[x])

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

    def _setAdd(self, x, s, v):  # every value under node x gains v
        self.sm[x] += v << s
        h = v % _HP * self.GS[s] % _HP
        self.fh[x] = (self.fh[x] + h) % _HP
        self.bh[x] = (self.bh[x] + h) % _HP

    def _applyAdd(self, x, s, v):
        self._setAdd(x, s, v)
        if x < self.n:
            self.add[x] += v

    def _push(self, x, s):  # hand node x's pending tags to its children
        a, b = 2 * x, 2 * x + 1
        c = s - 1  # (their level)
        if self.add[x]:
            v = self.add[x]
            self._applyAdd(a, c, v)
            self._applyAdd(b, c, v)
            self.add[x] = 0

    def _pushPath(self, p):  # hand down every pending tag on the path from the root to leaf p
        for s in range(self.h, 0, -1):
            self._push(p >> s, s)
