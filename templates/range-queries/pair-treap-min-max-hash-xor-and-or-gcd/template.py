# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pair-treap-min-max-hash-xor-and-or-gcd/template.py
# @operations: append appendLeft cut getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX leftmostLtX leftmostLteX merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeGcd rangeHash rangeHashReversed rangeMax rangeMin rangeOrQuery rangeRotateLeft rangeRotateRight rangeTwinSpin rangeXorQuery rangesEqual rightmostGtX rightmostGteX rightmostLtX rightmostLteX split trisect
# @data-structure-type: pair-treap
# @complexities:
#   append: log(N)*log(U) expected ?
#   appendLeft: log(N)*log(U) expected ?
#   cut: log(N)*log(U) expected ?
#   getAll: N
#   insertAt: log(N)*log(U) expected ?
#   insertCopiesAt: log(N)*log(U) expected ?
#   isPalindrome: log(N)*log(U) expected ?
#   leftmostGtX: log(N)*log(U) expected ?
#   leftmostGteX: log(N)*log(U) expected ?
#   leftmostLtX: log(N)*log(U) expected ?
#   leftmostLteX: log(N)*log(U) expected ?
#   merge: log(N)*log(U) expected ?
#   paste: log(N)*log(U) expected ?
#   pointAdd: log(N)*log(U) expected ?
#   pointAssign: log(N)*log(U) expected ?
#   pointChmax: log(N)*log(U) expected ?
#   pointChmin: log(N)*log(U) expected ?
#   pointGet: log(N) expected
#   rangeAndQuery: log(N)*log(U) expected ?
#   rangeGcd: log(N)*log(U) expected ?
#   rangeHash: log(N)*log(U) expected ?
#   rangeHashReversed: log(N)*log(U) expected ?
#   rangeMax: log(N)*log(U) expected ?
#   rangeMin: log(N)*log(U) expected ?
#   rangeOrQuery: log(N)*log(U) expected ?
#   rangeRotateLeft: log(N)*log(U) expected ?
#   rangeRotateRight: log(N)*log(U) expected ?
#   rangeTwinSpin: log(N)*log(U) expected ?
#   rangeXorQuery: log(N)*log(U) expected ?
#   rangesEqual: log(N)*log(U) expected ?
#   rightmostGtX: log(N)*log(U) expected ?
#   rightmostGteX: log(N)*log(U) expected ?
#   rightmostLtX: log(N)*log(U) expected ?
#   rightmostLteX: log(N)*log(U) expected ?
#   split: log(N)*log(U) expected ?
#   trisect: log(N)*log(U) expected ?
#   build: N*log(U) ?
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] mn[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] xr[1*N] an[1*N] orr[1*N] g[1*N]
#   tags: none
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); two treaps per array (even / odd positions); every PairSwapTreap<T> shares one node pool; each lane hashes in base B^2 (pieces move between any of them; nothing to reset)

# Implicit treap pair: an array you can insert into anywhere, swap adjacent pairs in a range (rangeTwinSpin: a[l] <->
# a[l + 1], a[l + 2] <-> a[l + 3], ...), rotate, cut pieces out of (that is how to erase) and paste them back in
# O(logN) expected each. The values at even positions a[0], a[2], ... are one treap (lane E) and the odd ones another
# (lane O), in one node pool; a range [l, r] is a slice of each, and each node keeps its min, its max, its forward /
# backward hash (and B^size), its xor, its AND, its OR, its gcd over its subtree. All indices 0-based, ranges
# inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when nothing qualifies.
import random
from math import gcd


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)
_HQ = _HB * _HB % _HP  # each lane hashes in base B^2 (its neighbours in the array are 2 apart)


class PairSwapTreap:
    # one node pool shared by every PairSwapTreap: cut / paste move nodes between them, so a piece from one can go
    # into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    # whole run), so there is nothing to reset between test cases
    val = [0]
    pri = [0]
    L = [0]
    R = [0]
    sz = [0]
    mn = [0]
    mx = [0]
    fh = [0]
    bh = [0]
    pw = [1]
    xr = [0]
    an = [-1]
    orr = [0]
    g = [0]
    __slots__ = ("rE", "rO")

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        arr = list(arr)
        self.rE = self._build(arr[0::2])  # lane E: a[0], a[2], ...
        self.rO = self._build(arr[1::2])  # lane O: a[1], a[3], ...

    def _empty(self):  # a new, empty PairSwapTreap (on the same pool, like every one)
        return PairSwapTreap()

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.rE] + self.sz[self.rO]

    # O(logN * logU) expected -- append v to the end
    def append(self, v):
        self.rE, self.rO = self._pmerge(self.rE, self.rO, self._newNode(v), 0)

    # O(logN * logU) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN * logU) expected -- remove a[l..r] and return it as a PairSwapTreap of its own (indices from 0)
    def cut(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)
        piece = self._empty()
        piece.rE, piece.rO = be, bo
        return piece

    # O(N) -- the whole current array, every pending tag applied on the way
    def getAll(self):
        ev, od = self._inorder(self.rE), self._inorder(self.rO)
        out = [0] * (len(ev) + len(od))
        out[0::2], out[1::2] = ev, od
        return out

    # O(logN * logU) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
        ae, ao = self._pmerge(ae, ao, self._newNode(v), 0)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)

    # O(k + logN * logU) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    def insertCopiesAt(self, i, v, k):
        if k > 0:
            ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
            ae, ao = self._pmerge(ae, ao, self._build([v] * ((k + 1) // 2)), self._build([v] * (k // 2)))
            self.rE, self.rO = self._pmerge(ae, ao, ce, co)

    # O(logN * logU) expected -- is a[l..r] a palindrome (its two hashes agree)
    def isPalindrome(self, l, r):
        f, b = self._hashes(l, r)
        return f == b

    # O(logN * logU) expected -- the first i in [l, r] with a[i] > x, or -1 (each lane's walk pruned by the subtree max)
    def leftmostGtX(self, l, r, x):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneLeftmostGtX(be, x), self._laneLeftmostGtX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return i if j < 0 else j if i < 0 else min(i, j)

    # O(logN * logU) expected -- the first i in [l, r] with a[i] >= x, or -1 (each lane's walk pruned by the subtree max)
    def leftmostGteX(self, l, r, x):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneLeftmostGteX(be, x), self._laneLeftmostGteX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return i if j < 0 else j if i < 0 else min(i, j)

    # O(logN * logU) expected -- the first i in [l, r] with a[i] < x, or -1 (each lane's walk pruned by the subtree min)
    def leftmostLtX(self, l, r, x):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneLeftmostLtX(be, x), self._laneLeftmostLtX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return i if j < 0 else j if i < 0 else min(i, j)

    # O(logN * logU) expected -- the first i in [l, r] with a[i] <= x, or -1 (each lane's walk pruned by the subtree min)
    def leftmostLteX(self, l, r, x):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneLeftmostLteX(be, x), self._laneLeftmostLteX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return i if j < 0 else j if i < 0 else min(i, j)

    # O(logN * logU) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.rE, self.rO = self._pmerge(self.rE, self.rO, other.rE, other.rO)
        other.rE = other.rO = 0

    # O(logN * logU) expected -- insert all of other (any PairSwapTreap, e.g. a cut piece) so it starts at a[i]
    # (0 <= i <= size()); other is left empty
    def paste(self, i, other):
        ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
        ae, ao = self._pmerge(ae, ao, other.rE, other.rO)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)
        other.rE = other.rO = 0

    # O(logN * logU) expected -- a[i] += v
    def pointAdd(self, i, v):
        t, path = self._find(i)
        self.val[t] = self.val[t] + v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN * logU) expected -- a[i] = v
    def pointAssign(self, i, v):
        t, path = self._find(i)
        self.val[t] = v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN * logU) expected -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        t, path = self._find(i)
        self.val[t] = max(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN * logU) expected -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        t, path = self._find(i)
        self.val[t] = min(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i]
    def pointGet(self, i):
        return self.val[self._find(i)[0]]

    # O(logN * logU) expected -- a[l] & ... & a[r]
    def rangeAndQuery(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = self.an[be] & self.an[bo]
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|
    def rangeGcd(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = gcd(self.g[be], self.g[bo])
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN * logU) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    def rangeHash(self, l, r):
        return self._hashes(l, r)[0]

    # O(logN * logU) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    def rangeHashReversed(self, l, r):
        return self._hashes(l, r)[1]

    # O(logN * logU) expected -- max of a[l..r]
    def rangeMax(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = self.mx[be] if not bo else max(self.mx[be], self.mx[bo])
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN * logU) expected -- min of a[l..r]
    def rangeMin(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = self.mn[be] if not bo else min(self.mn[be], self.mn[bo])
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN * logU) expected -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = self.orr[be] | self.orr[bo]
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    # it is taken mod the length (negative shifts right)
    def rangeRotateLeft(self, l, r, k):
        k %= r - l + 1
        if k:
            ae, ao, be, bo, ce, co = self._cut(l, r)
            xe, xo, ye, yo = self._psplit(be, bo, k)
            be, bo = self._pmerge(ye, yo, xe, xo)
            self._join(ae, ao, be, bo, ce, co)

    # O(logN * logU) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left)
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)

    # O(logN * logU) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length: a[r] stays):
    # the pairs' two lanes trade places
    def rangeTwinSpin(self, l, r):
        k = (r - l + 1) // 2
        if k:
            ae, ao, be, bo, ce, co = self._cut(l, l + 2 * k - 1)
            self._join(ae, ao, bo, be, ce, co)

    # O(logN * logU) expected -- a[l] ^ ... ^ a[r]
    def rangeXorQuery(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = self.xr[be] ^ self.xr[bo]
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN * logU) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self._hashes(l1, r1)[0] == self._hashes(l2, r2)[0]

    # O(logN * logU) expected -- the last i in [l, r] with a[i] > x, or -1 (each lane's walk pruned by the subtree max)
    def rightmostGtX(self, l, r, x):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneRightmostGtX(be, x), self._laneRightmostGtX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return max(i, j)

    # O(logN * logU) expected -- the last i in [l, r] with a[i] >= x, or -1 (each lane's walk pruned by the subtree max)
    def rightmostGteX(self, l, r, x):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneRightmostGteX(be, x), self._laneRightmostGteX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return max(i, j)

    # O(logN * logU) expected -- the last i in [l, r] with a[i] < x, or -1 (each lane's walk pruned by the subtree min)
    def rightmostLtX(self, l, r, x):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneRightmostLtX(be, x), self._laneRightmostLtX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return max(i, j)

    # O(logN * logU) expected -- the last i in [l, r] with a[i] <= x, or -1 (each lane's walk pruned by the subtree min)
    def rightmostLteX(self, l, r, x):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneRightmostLteX(be, x), self._laneRightmostLteX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return max(i, j)

    # O(logN * logU) expected -- (a[0..k-1], a[k..]) as two PairSwapTreaps of their own; this one is left empty
    def split(self, k):
        left, right = self._empty(), self._empty()
        left.rE, left.rO, right.rE, right.rO = self._psplit(self.rE, self.rO, k)
        self.rE = self.rO = 0
        return left, right

    # O(logN * logU) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PairSwapTreaps of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.rE, left.rO, mid.rE, mid.rO, right.rE, right.rO = self._cut(l, r)
        self.rE = self.rO = 0
        return left, mid, right

    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        self.mn.append(v)
        self.mx.append(v)
        self.fh.append((v + _HO) % _HP)
        self.bh.append((v + _HO) % _HP)
        self.pw.append(_HQ)
        self.xr.append(v)
        self.an.append(v)
        self.orr.append(v)
        self.g.append(abs(v))
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
        m = v
        if l and self.mn[l] < m:
            m = self.mn[l]
        if r and self.mn[r] < m:
            m = self.mn[r]
        self.mn[x] = m
        m = v
        if l and self.mx[l] > m:
            m = self.mx[l]
        if r and self.mx[r] > m:
            m = self.mx[r]
        self.mx[x] = m
        B, P, pw, fh, bh = _HQ, _HP, self.pw, self.fh, self.bh
        hv = (v + _HO) % P
        pw[x] = pw[l] * B % P * pw[r] % P
        fh[x] = ((fh[l] * B + hv) * pw[r] + fh[r]) % P
        bh[x] = ((bh[r] * B + hv) * pw[l] + bh[l]) % P
        self.xr[x] = self.xr[l] ^ v ^ self.xr[r]
        self.an[x] = self.an[l] & v & self.an[r]  # (node 0: the AND of nothing, -1)
        self.orr[x] = self.orr[l] | v | self.orr[r]
        self.g[x] = gcd(gcd(self.g[l], v), self.g[r])

    def _split(self, t, k):  # (first k of t, the rest)
        if not t:
            return 0, 0
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
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        self.L[b] = self._merge(a, self.L[b])
        self._pull(b)
        return b

    # an array is a pair of lanes (E, O): E holds its values at even positions, O the odd ones

    def _psplit(self, e, o, k):  # lanes of (the first k values, the rest)
        e1, e2 = self._split(e, (k + 1) // 2)
        o1, o2 = self._split(o, k // 2)
        return (e1, o1, o2, e2) if k % 2 else (e1, o1, e2, o2)  # (an odd k: the rest starts on an odd position)

    def _pmerge(self, e1, o1, e2, o2):  # lanes of (the first array, then the second)
        if (self.sz[e1] + self.sz[o1]) % 2:
            e2, o2 = o2, e2  # (after an odd length the second's even positions are odd ones)
        return self._merge(e1, e2), self._merge(o1, o2)

    def _cut(self, l, r):  # lanes of a[..l-1], a[l..r], a[r+1..]
        ae, ao, be, bo = self._psplit(self.rE, self.rO, l)
        be, bo, ce, co = self._psplit(be, bo, r - l + 1)
        return ae, ao, be, bo, ce, co

    def _join(self, ae, ao, be, bo, ce, co):
        self.rE, self.rO = self._pmerge(*self._pmerge(ae, ao, be, bo), ce, co)

    def _find(self, i):  # (node holding a[i], the nodes above it), every tag on the way pushed
        L, sz, path, k = self.L, self.sz, [], i // 2
        t = self.rO if i % 2 else self.rE
        while True:
            ls = sz[L[t]]
            if k == ls:
                return t, path
            path.append(t)
            if k < ls:
                t = L[t]
            else:
                k -= ls + 1
                t = self.R[t]

    def _inorder(self, t):  # the values under t in order, every tag on the way pushed
        L, R, val = self.L, self.R, self.val
        out, stack = [], []
        while stack or t:
            while t:
                stack.append(t)
                t = L[t]
            t = stack.pop()
            out.append(val[t])
            t = R[t]
        return out

    # (forward, backward) hash of a[l..r]: lane E's slice x holds a[l], a[l + 2], ..., lane O's y the rest; in base B
    # the range reads x0 y0 x1 y1 ..., so forward = H(x) + B H(y) (odd length) or B H(x) + H(y) (even), and backward
    # = Hrev(x) + B Hrev(y)
    def _hashes(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        P, B, fh, bh = _HP, _HB, self.fh, self.bh
        fwd = (fh[be] + B * fh[bo]) % P if (r - l) % 2 == 0 else (B * fh[be] + fh[bo]) % P
        bwd = (bh[be] + B * bh[bo]) % P
        self._join(ae, ao, be, bo, ce, co)
        return fwd, bwd

    def _laneLeftmostGtX(self, t, x):  # the first k with lane value k > x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        if not t or not F[t] > x:
            return -1
        i = 0
        while True:
            if L[t] and F[L[t]] > x:
                t = L[t]
            elif val[t] > x:
                return i + sz[L[t]]
            else:
                i += sz[L[t]] + 1
                t = R[t]

    def _laneLeftmostGteX(self, t, x):  # the first k with lane value k >= x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        if not t or not F[t] >= x:
            return -1
        i = 0
        while True:
            if L[t] and F[L[t]] >= x:
                t = L[t]
            elif val[t] >= x:
                return i + sz[L[t]]
            else:
                i += sz[L[t]] + 1
                t = R[t]

    def _laneLeftmostLtX(self, t, x):  # the first k with lane value k < x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mn
        if not t or not F[t] < x:
            return -1
        i = 0
        while True:
            if L[t] and F[L[t]] < x:
                t = L[t]
            elif val[t] < x:
                return i + sz[L[t]]
            else:
                i += sz[L[t]] + 1
                t = R[t]

    def _laneLeftmostLteX(self, t, x):  # the first k with lane value k <= x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mn
        if not t or not F[t] <= x:
            return -1
        i = 0
        while True:
            if L[t] and F[L[t]] <= x:
                t = L[t]
            elif val[t] <= x:
                return i + sz[L[t]]
            else:
                i += sz[L[t]] + 1
                t = R[t]

    def _laneRightmostGtX(self, t, x):  # the last k with lane value k > x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        if not t or not F[t] > x:
            return -1
        i = 0
        while True:
            if R[t] and F[R[t]] > x:
                i += sz[L[t]] + 1
                t = R[t]
            elif val[t] > x:
                return i + sz[L[t]]
            else:
                t = L[t]

    def _laneRightmostGteX(self, t, x):  # the last k with lane value k >= x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        if not t or not F[t] >= x:
            return -1
        i = 0
        while True:
            if R[t] and F[R[t]] >= x:
                i += sz[L[t]] + 1
                t = R[t]
            elif val[t] >= x:
                return i + sz[L[t]]
            else:
                t = L[t]

    def _laneRightmostLtX(self, t, x):  # the last k with lane value k < x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mn
        if not t or not F[t] < x:
            return -1
        i = 0
        while True:
            if R[t] and F[R[t]] < x:
                i += sz[L[t]] + 1
                t = R[t]
            elif val[t] < x:
                return i + sz[L[t]]
            else:
                t = L[t]

    def _laneRightmostLteX(self, t, x):  # the last k with lane value k <= x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mn
        if not t or not F[t] <= x:
            return -1
        i = 0
        while True:
            if R[t] and F[R[t]] <= x:
                i += sz[L[t]] + 1
                t = R[t]
            elif val[t] <= x:
                return i + sz[L[t]]
            else:
                t = L[t]


# Example (pieces move between treaps; merge appends and leaves its argument empty):
#     t = PairSwapTreap([1, 2, 3, 4, 5])
#     left, mid, right = t.trisect(1, 3)  # left = [1], mid = [2, 3, 4], right = [5]; t is empty now
#     t.merge(right)                      # t = [5]
#     t.merge(mid)                        # t = [5, 2, 3, 4]
#     t.merge(left)                       # t = [5, 2, 3, 4, 1]
