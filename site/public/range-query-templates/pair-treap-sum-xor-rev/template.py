# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pair-treap-sum-xor-rev/template.py
# @operations: append appendLeft cut getAll insertAt insertCopiesAt merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeReverse rangeRotateLeft rangeRotateRight rangeSum rangeTwinSpin rangeXorQuery split trisect
# @data-structure-type: pair-treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   merge: log(N) expected
#   paste: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   rangeReverse: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangeSum: log(N) expected
#   rangeTwinSpin: log(N) expected
#   rangeXorQuery: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] xr[1*N]
#   tags: rev[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); two treaps per array (even / odd positions); every PairSwapTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

# Implicit treap pair: an array you can insert into anywhere, swap adjacent pairs in a range (rangeTwinSpin: a[l] <->
# a[l + 1], a[l + 2] <-> a[l + 3], ...), reverse, rotate, cut pieces out of (that is how to erase) and paste them back
# in O(logN) expected each. The values at even positions a[0], a[2], ... are one treap (lane E) and the odd ones
# another (lane O), in one node pool; a range [l, r] is a slice of each, and each node keeps its sum, its xor over its
# subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches
# return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet to its children".
import random


class PairSwapTreap:
    # one node pool shared by every PairSwapTreap: cut / paste move nodes between them, so a piece from one can go
    # into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    # whole run), so there is nothing to reset between test cases
    val = [0]
    pri = [0]
    L = [0]
    R = [0]
    sz = [0]
    sm = [0]
    xr = [0]
    rev = [0]
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

    # O(logN) expected -- append v to the end
    def append(self, v):
        self.rE, self.rO = self._pmerge(self.rE, self.rO, self._newNode(v), 0)

    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- remove a[l..r] and return it as a PairSwapTreap of its own (indices from 0)
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

    # O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
        ae, ao = self._pmerge(ae, ao, self._newNode(v), 0)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)

    # O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    def insertCopiesAt(self, i, v, k):
        if k > 0:
            ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
            ae, ao = self._pmerge(ae, ao, self._build([v] * ((k + 1) // 2)), self._build([v] * (k // 2)))
            self.rE, self.rO = self._pmerge(ae, ao, ce, co)

    # O(logN) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.rE, self.rO = self._pmerge(self.rE, self.rO, other.rE, other.rO)
        other.rE = other.rO = 0

    # O(logN) expected -- insert all of other (any PairSwapTreap, e.g. a cut piece) so it starts at a[i]
    # (0 <= i <= size()); other is left empty
    def paste(self, i, other):
        ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
        ae, ao = self._pmerge(ae, ao, other.rE, other.rO)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)
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

    # O(logN) expected -- reverse a[l..r] in place: each lane reverses, and with an even length they trade places
    def rangeReverse(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        self._applyRev(be)
        self._applyRev(bo)
        if (r - l + 1) % 2 == 0:
            be, bo = bo, be
        self._join(ae, ao, be, bo, ce, co)

    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    # it is taken mod the length (negative shifts right)
    def rangeRotateLeft(self, l, r, k):
        k %= r - l + 1
        if k:
            ae, ao, be, bo, ce, co = self._cut(l, r)
            xe, xo, ye, yo = self._psplit(be, bo, k)
            be, bo = self._pmerge(ye, yo, xe, xo)
            self._join(ae, ao, be, bo, ce, co)

    # O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left)
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)

    # O(logN) expected -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = self.sm[be] + self.sm[bo]
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length:
    # a[r] stays): the pairs' two lanes trade places
    def rangeTwinSpin(self, l, r):
        k = (r - l + 1) // 2
        if k:
            ae, ao, be, bo, ce, co = self._cut(l, l + 2 * k - 1)
            self._join(ae, ao, bo, be, ce, co)

    # O(logN) expected -- a[l] ^ ... ^ a[r]
    def rangeXorQuery(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = self.xr[be] ^ self.xr[bo]
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN) expected -- (a[0..k-1], a[k..]) as two PairSwapTreaps of their own; this one is left empty
    def split(self, k):
        left, right = self._empty(), self._empty()
        left.rE, left.rO, right.rE, right.rO = self._psplit(self.rE, self.rO, k)
        self.rE = self.rO = 0
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PairSwapTreaps of their own; this one is left empty
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
        self.sm.append(v)
        self.xr.append(v)
        self.rev.append(0)
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
        self.sm[x] = self.sm[l] + v + self.sm[r]
        self.xr[x] = self.xr[l] ^ v ^ self.xr[r]

    def _applyRev(self, x):  # reverse x's subtree
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1

    def _push(self, x):  # hand x's pending tags to its children
        if self.rev[x]:
            self._applyRev(self.L[x])
            self._applyRev(self.R[x])
            self.rev[x] = 0

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

    def _inorder(self, t):  # the values under t in order, every tag on the way pushed
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


# Example (pieces move between treaps; merge appends and leaves its argument empty):
#     t = PairSwapTreap([1, 2, 3, 4, 5])
#     left, mid, right = t.trisect(1, 3)  # left = [1], mid = [2, 3, 4], right = [5]; t is empty now
#     t.merge(right)                      # t = [5]
#     t.merge(mid)                        # t = [5, 2, 3, 4]
#     t.merge(left)                       # t = [5, 2, 3, 4, 1]
