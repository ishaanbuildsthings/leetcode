# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pair-treap-hash-addassign-rev/template.py
# @operations: append appendLeft cut getAll insertAt isPalindrome merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeHash rangeHashReversed rangeReverse rangeTwinSpin rangesEqual split trisect
# @data-structure-type: pair-treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   isPalindrome: log(N) expected
#   merge: log(N) expected
#   paste: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   rangeAdd: log(N) expected
#   rangeAssign: log(N) expected
#   rangeHash: log(N) expected
#   rangeHashReversed: log(N) expected
#   rangeReverse: log(N) expected
#   rangeTwinSpin: log(N) expected
#   rangesEqual: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] fh[1*N] bh[1*N] pw[1*N] gs[1*N]
#   tags: rev[1*N] add[1*N] asg[1*N] hasAsg[1*N]
#   other: none
#   note: N = every value ever inserted (erased nodes are not reused); two treaps (even / odd positions) share one node pool; each lane hashes in base B^2, and a range's two lanes weave back into base B

# Implicit treap pair: an array you can insert into / erase from anywhere, reverse ranges and swap adjacent pairs in a
# range (a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ...), each in O(logN) expected, plus point ops, rangeAdd,
# rangeAssign, range hashes / isPalindrome / rangesEqual. The even positions a[0], a[2], ... are one treap (E) and the
# odd ones another (O), in one node pool; a range [l, r] is a slice of each. All indices 0-based, ranges inclusive,
# always positions in the CURRENT array.
import random


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)
_HQ = _HB * _HB % _HP  # each lane hashes in base B^2 (its neighbours in the array are 2 apart)


class PairSwapTreap:
    __slots__ = ('rE', 'rO', 'val', 'pri', 'L', 'R', 'sz', 'rev', 'add', 'asg', 'hasAsg', 'fh', 'bh', 'pw', 'gs')


    # O(N) -- arr: the initial array (may be empty); like: a PairSwapTreap whose nodes this one shares, so pieces can
    # move between the two (pieces cut from it share them already). No reset between test cases
    def __init__(self, arr=(), like=None):
        if like is None:
            self.val, self.pri, self.L, self.R, self.sz = [0], [0], [0], [0], [0]  # node 0 = the empty tree
            self.rev = [0]
            self.add = [0]
            self.asg, self.hasAsg = [0], [0]
            self.fh, self.bh, self.pw = [0], [0], [1]
            self.gs = [0]
        else:
            self.val = like.val
            self.pri = like.pri
            self.L = like.L
            self.R = like.R
            self.sz = like.sz
            self.rev = like.rev
            self.add = like.add
            self.asg = like.asg
            self.hasAsg = like.hasAsg
            self.fh = like.fh
            self.bh = like.bh
            self.pw = like.pw
            self.gs = like.gs
        self.rE = self._build(arr[0::2])  # a[0], a[2], ...
        self.rO = self._build(arr[1::2])  # a[1], a[3], ...

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.rE] + self.sz[self.rO]

    # O(logN) expected -- append v to the end
    def append(self, v):
        self.insertAt(self.size(), v)

    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- remove a[l..r] and return it as a PairSwapTreap of its own (indices from 0; drop it to erase);
    # the tail moves r - l + 1 places, so with an odd count the two tails trade places
    def cut(self, l, r):
        a, b, c, d, e, f = self._parts(l, r)
        if (r - l + 1) % 2 == 0:
            self.rE, self.rO = self._merge(a, c), self._merge(d, f)
        else:
            self.rE, self.rO = self._merge(a, f), self._merge(d, c)
        piece = PairSwapTreap(like=self)
        piece.rE, piece.rO = (b, e) if l % 2 == 0 else (e, b)
        return piece

    # O(N) -- the whole current array, every pending tag applied on the way
    def getAll(self):
        ev, od = self._inorder(self.rE), self._inorder(self.rO)
        out = [0] * (len(ev) + len(od))
        out[0::2], out[1::2] = ev, od
        return out

    # O(logN) expected -- insert v so it becomes a[i] (i <= size()); the tail after it moves one place, so its parity
    # flips: E's tail and O's tail trade places
    def insertAt(self, i, v):
        a, _, c, d, _, f = self._parts(i, i - 1)
        x, merge = self._newNode(v), self._merge
        if i % 2 == 0:
            self.rE, self.rO = merge(merge(a, x), f), merge(d, c)
        else:
            self.rE, self.rO = merge(a, f), merge(merge(d, x), c)

    # O(logN) expected -- is a[l..r] a palindrome (its two hashes agree)
    def isPalindrome(self, l, r):
        f, b = self._hashes(l, r)
        return f == b

    # O(logN) expected -- append all of other at the end, leaving it empty (it must share this treap's nodes)
    def merge(self, other):
        self.paste(self.size(), other)

    # O(logN) expected -- insert other so it starts at a[i] (0 <= i <= size()), leaving it empty; it must share this
    # treap's nodes (a piece cut from it, or built with like=). other's a[0] lands at parity i % 2, and the tail after i
    # moves other's length on: with an odd length the tails trade places
    def paste(self, i, other):
        a, _, c, d, _, f = self._parts(i, i - 1)
        x, y = (other.rE, other.rO) if i % 2 == 0 else (other.rO, other.rE)
        if other.size() % 2:
            c, f = f, c
        merge = self._merge
        self.rE, self.rO = merge(merge(a, x), c), merge(merge(d, y), f)
        other.rE = other.rO = 0

    # O(logN) expected -- a[i] += v
    def pointAdd(self, i, v):
        t, path = self._find(i)
        self.val[t] = self.val[t] + v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = v
    def pointAssign(self, i, v):
        t, path = self._find(i)
        self.val[t] = v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        t, path = self._find(i)
        self.val[t] = max(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        t, path = self._find(i)
        self.val[t] = min(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i]
    def pointGet(self, i):
        return self.val[self._find(i)[0]]

    # O(logN) expected -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        a, b, c, d, e, f = self._parts(l, r)
        self._applyAdd(b, v)
        self._applyAdd(e, v)
        self._join(a, b, c, d, e, f)

    # O(logN) expected -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        a, b, c, d, e, f = self._parts(l, r)
        self._applyAssign(b, v)
        self._applyAssign(e, v)
        self._join(a, b, c, d, e, f)

    # O(logN) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    def rangeHash(self, l, r):
        return self._hashes(l, r)[0]

    # O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    def rangeHashReversed(self, l, r):
        return self._hashes(l, r)[1]

    # O(logN) expected -- reverse a[l..r] in place: a[p] goes to l + r - p, the same parity when l + r is even (each
    # slice reverses in place) and the other parity when it is odd (the slices, then equally long, cross over reversed)
    def rangeReverse(self, l, r):
        a, b, c, d, e, f = self._parts(l, r)
        self._applyRev(b)
        self._applyRev(e)
        if (l + r) % 2:
            b, e = e, b
        self._join(a, b, c, d, e, f)

    # O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length: a[r] stays):
    # the pairs' even and odd halves are two slices of equal length, which trade places
    def rangeTwinSpin(self, l, r):
        k = (r - l + 1) // 2
        if k:
            a, b, c, d, e, f = self._parts(l, l + 2 * k - 1)
            self._join(a, e, c, d, b, f)

    # O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self._hashes(l1, r1)[0] == self._hashes(l2, r2)[0]

    # O(logN) expected -- (a[0..k-1], a[k..]) as two PairSwapTreaps of their own; this one is left empty
    def split(self, k):
        left = PairSwapTreap(like=self)
        left.rE, left.rO = self.rE, self.rO
        self.rE = self.rO = 0
        right = left.cut(k, left.size() - 1) if k < left.size() else PairSwapTreap(like=self)
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PairSwapTreaps of their own; this one is left empty
    def trisect(self, l, r):
        left, right = self.split(r + 1)
        left, mid = left.split(l)
        return left, mid, right

    # ---- internals ----

    # counts of even / odd positions below x: (x + 1) // 2 and x // 2
    def _parts(self, l, r):  # (E before, E in [l, r], E after, O before, O in [l, r], O after) as six trees
        e1, e2, o1, o2 = (l + 1) // 2, (r + 2) // 2, l // 2, (r + 1) // 2
        a, b = self._split(self.rE, e1)
        b, c = self._split(b, e2 - e1)
        d, e = self._split(self.rO, o1)
        e, f = self._split(e, o2 - o1)
        return a, b, c, d, e, f

    def _join(self, a, b, c, d, e, f):
        merge = self._merge
        self.rE, self.rO = merge(merge(a, b), c), merge(merge(d, e), f)

    # (forward, backward) hash of a[l..r]: x = the lane slice holding a[l], y = the other; in base B the array reads
    # x0 y0 x1 y1 ..., so forward = H(x) + B H(y) (odd length) or B H(x) + H(y) (even), backward = Hrev(x) + B Hrev(y)
    def _hashes(self, l, r):
        a, b, c, d, e, f = self._parts(l, r)
        x, y = (b, e) if l % 2 == 0 else (e, b)
        P, B, fh, bh = _HP, _HB, self.fh, self.bh
        fwd = (fh[x] + B * fh[y]) % P if (r - l) % 2 == 0 else (B * fh[x] + fh[y]) % P
        bwd = (bh[x] + B * bh[y]) % P
        self._join(a, b, c, d, e, f)
        return fwd, bwd

    # (node holding a[i], the nodes above it), every tag on the way pushed
    def _find(self, i):
        L, sz, t, path, k = self.L, self.sz, self.rO if i % 2 else self.rE, [], i // 2
        while True:
            self._push(t)
            ls = sz[L[t]]
            if k == ls:
                return t, path
            path.append(t)
            if k < ls:
                t = L[t]
            else:
                k -= ls + 1
                t = self.R[t]

    def _inorder(self, t):
        L, R, val = self.L, self.R, self.val
        out, stack = [], []
        while stack or t:
            while t:
                self._push(t)
                stack.append(t)
                t = L[t]
            t = stack.pop()
            out.append(val[t])
            t = R[t]
        return out

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        self.rev.append(0)
        self.add.append(0)
        self.asg.append(0)
        self.hasAsg.append(0)
        self.fh.append((v + _HO) % _HP)
        self.bh.append((v + _HO) % _HP)
        self.pw.append(_HQ)
        self.gs.append(1)
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

    def _pull(self, x):
        l, r = self.L[x], self.R[x]
        self.sz[x] = self.sz[l] + self.sz[r] + 1
        Q, P, pw, fh, bh = _HQ, _HP, self.pw, self.fh, self.bh
        hv = (self.val[x] + _HO) % P
        pw[x] = pw[l] * Q % P * pw[r] % P
        gs = self.gs
        gs[x] = ((gs[l] * Q + 1) * pw[r] + gs[r]) % P
        fh[x] = ((fh[l] * Q + hv) * pw[r] + fh[r]) % P
        bh[x] = ((bh[r] * Q + hv) * pw[l] + bh[l]) % P

    def _applyRev(self, x):
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
            self.fh[x], self.bh[x] = self.bh[x], self.fh[x]

    def _applyAdd(self, x, v):
        if not x:
            return
        self.val[x] += v
        h = v % _HP * self.gs[x] % _HP
        self.fh[x] = (self.fh[x] + h) % _HP
        self.bh[x] = (self.bh[x] + h) % _HP
        if self.hasAsg[x]:
            self.asg[x] += v
        else:
            self.add[x] += v

    def _applyAssign(self, x, v):
        if not x:
            return
        self.val[x] = v
        self.fh[x] = self.bh[x] = (v + _HO) % _HP * self.gs[x] % _HP
        self.hasAsg[x] = 1
        self.asg[x] = v
        self.add[x] = 0

    def _push(self, x):  # hand x's pending tags to its children
        if self.rev[x]:
            self._applyRev(self.L[x])
            self._applyRev(self.R[x])
            self.rev[x] = 0
        if self.hasAsg[x]:
            self._applyAssign(self.L[x], self.asg[x])
            self._applyAssign(self.R[x], self.asg[x])
            self.hasAsg[x] = 0
        elif self.add[x]:
            self._applyAdd(self.L[x], self.add[x])
            self._applyAdd(self.R[x], self.add[x])
            self.add[x] = 0

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
