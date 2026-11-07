# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pair-treap-sum-min-gcd-updates-add-assign-rev/template.py
# @operations: append appendLeft cut gcdAll getAll insertAt insertCopiesAt leftmostLtX leftmostLteX merge minAll paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAdd rangeAssign rangeGcd rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum rangeTwinSpin rightmostLtX rightmostLteX size split sumAll trisect
# @data-structure-type: pair-treap
# @complexities:
#   append: log(N)*log(U) expected ?
#   appendLeft: log(N)*log(U) expected ?
#   cut: log(N)*log(U) expected ?
#   getAll: N
#   insertAt: log(N)*log(U) expected ?
#   insertCopiesAt: log(N)*log(U) expected ?
#   leftmostLtX: log(N)*log(U) expected ?
#   leftmostLteX: log(N)*log(U) expected ?
#   merge: log(N)*log(U) expected ?
#   paste: log(N)*log(U) expected ?
#   pointAdd: log(N)*log(U) expected ?
#   pointAssign: log(N)*log(U) expected ?
#   pointChmax: log(N)*log(U) expected ?
#   pointChmin: log(N)*log(U) expected ?
#   pointGet: log(N) expected
#   rangeAdd: log(N)*log(U) expected ?
#   rangeAssign: log(N)*log(U) expected ?
#   rangeGcd: log(N)*log(U) expected ?
#   rangeMin: log(N)*log(U) expected ?
#   rangeReverse: log(N)*log(U) expected ?
#   rangeRotateLeft: log(N)*log(U) expected ?
#   rangeRotateRight: log(N)*log(U) expected ?
#   rangeSum: log(N)*log(U) expected ?
#   rangeTwinSpin: log(N)*log(U) expected ?
#   rightmostLtX: log(N)*log(U) expected ?
#   rightmostLteX: log(N)*log(U) expected ?
#   split: log(N)*log(U) expected ?
#   trisect: log(N)*log(U) expected ?
#   size: 1
#   pop: log(N)*log(U) expected ?
#   popLeft: log(N)*log(U) expected ?
#   sumAll: 1
#   minAll: log(N)*log(U) expected ?
#   gcdAll: log(N)*log(U) expected ?
#   build: N*log(U) ?
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] g[1*N] fv[1*N] lv[1*N]
#   tags: rev[1*N] asg[1*N] hasAsg[1*N] add[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); two treaps per array (even / odd positions); every PairSwapTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

# Implicit treap pair: an array you can insert into anywhere, swap adjacent pairs in a range (rangeTwinSpin: a[l] <->
# a[l + 1], a[l + 2] <-> a[l + 3], ...), reverse, rotate, cut pieces out of (that is how to erase) and paste them back
# in O(logN) expected each, with rangeAdd, rangeAssign. The values at even positions a[0], a[2], ... are one treap
# (lane E) and the odd ones another (lane O), in one node pool; a range [l, r] is a slice of each, and each node keeps
# its sum, its min, its gcd over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the
# position in the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this
# node, not yet to its children"; a pending assign comes before a pending add.
import random
from math import gcd


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
    mn = [0]
    g = [0]
    fv = [0]
    lv = [0]
    rev = [0]
    asg = [0]
    hasAsg = [0]
    add = [0]
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

    # O(logN * logU) expected -- remove a[l..r] and return it as a PairSwapTreap of its own (indices from 0); needs
    # 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"cut: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
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

    # O(logN * logU) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else IndexError (i = size()
    # appends)
    def insertAt(self, i, v):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
        ae, ao = self._pmerge(ae, ao, self._newNode(v), 0)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)

    # O(k + logN * logU) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    # 0 <= i <= size(), else IndexError
    def insertCopiesAt(self, i, v, k):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertCopiesAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        if k > 0:
            ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
            ae, ao = self._pmerge(ae, ao, self._build([v] * ((k + 1) // 2)), self._build([v] * (k // 2)))
            self.rE, self.rO = self._pmerge(ae, ao, ce, co)

    # O(logN * logU) expected -- the first i in [l, r] with a[i] < x, or -1 (each lane's walk pruned by the subtree
    # min); needs 0 <= l <= r < size(), else IndexError
    def leftmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        be, bo, mark = self._laneNodes(l, r)
        i, j = self._laneLeftmostLtX(be, x), self._laneLeftmostLtX(bo, x)
        self._release(mark)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return i if j < 0 else j if i < 0 else min(i, j)

    # O(logN * logU) expected -- the first i in [l, r] with a[i] <= x, or -1 (each lane's walk pruned by the subtree
    # min); needs 0 <= l <= r < size(), else IndexError
    def leftmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        be, bo, mark = self._laneNodes(l, r)
        i, j = self._laneLeftmostLteX(be, x), self._laneLeftmostLteX(bo, x)
        self._release(mark)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return i if j < 0 else j if i < 0 else min(i, j)

    # O(logN * logU) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.rE, self.rO = self._pmerge(self.rE, self.rO, other.rE, other.rO)
        other.rE = other.rO = 0

    # O(logN * logU) expected -- insert all of other (any PairSwapTreap, e.g. a cut piece) so it starts at a[i] (needs
    # 0 <= i <= size(), else IndexError); other is left empty
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError(f"paste: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
        ae, ao = self._pmerge(ae, ao, other.rE, other.rO)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)
        other.rE = other.rO = 0

    # O(logN * logU) expected -- a[i] += v; needs 0 <= i < size(), else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAdd: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = self.val[t] + v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN * logU) expected -- a[i] = v; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN * logU) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmax: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = max(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN * logU) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmin: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = min(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        return self.val[self._find(i)[0]]

    # O(logN * logU) expected -- a[i] += v for i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        (te, le, he), (to, lo, ho) = self._lanes(l, r)
        self._upd(te, le, he, lambda x, off: self._applyAdd(x, v), lambda w, off: w + v)
        self._upd(to, lo, ho, lambda x, off: self._applyAdd(x, v), lambda w, off: w + v)

    # O(logN * logU) expected -- a[i] = v for i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        (te, le, he), (to, lo, ho) = self._lanes(l, r)
        self._upd(te, le, he, lambda x, off: self._applyAssign(x, v), lambda w, off: v)
        self._upd(to, lo, ho, lambda x, off: self._applyAssign(x, v), lambda w, off: v)

    # O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < size(), else IndexError
    def rangeGcd(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeGcd: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        be, bo, mark = self._laneNodes(l, r)
        fv, g = self.fv, self.g
        res = gcd(gcd(fv[be], g[be]), g[bo])
        if bo:
            res = gcd(res, fv[bo] - fv[be])
        self._release(mark)
        return res

    # O(logN * logU) expected -- min of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMin: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        be, bo, mark = self._laneNodes(l, r)
        res = self.mn[be] if not bo else min(self.mn[be], self.mn[bo])
        self._release(mark)
        return res

    # O(logN * logU) expected -- reverse a[l..r] in place: each lane reverses, and with an even length they trade
    # places; needs 0 <= l <= r < size(), else IndexError
    def rangeReverse(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeReverse: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        self._applyRev(be)
        self._applyRev(bo)
        if (r - l + 1) % 2 == 0:
            be, bo = bo, be
        self._join(ae, ao, be, bo, ce, co)

    # O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it
    # is taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateLeft(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateLeft: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        k %= r - l + 1
        if k:
            ae, ao, be, bo, ce, co = self._cut(l, r)
            xe, xo, ye, yo = self._psplit(be, bo, k)
            be, bo = self._pmerge(ye, yo, xe, xo)
            self._join(ae, ao, be, bo, ce, co)

    # O(logN * logU) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateRight(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateRight: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self.rangeRotateLeft(l, r, -k)

    # O(logN * logU) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeSum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        be, bo, mark = self._laneNodes(l, r)
        res = self.sm[be] + self.sm[bo]
        self._release(mark)
        return res

    # O(logN * logU) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length: a[r]
    # stays): the pairs' two lanes trade places; needs 0 <= l <= r < size(), else IndexError
    def rangeTwinSpin(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeTwinSpin: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        k = (r - l + 1) // 2
        if k:
            ae, ao, be, bo, ce, co = self._cut(l, l + 2 * k - 1)
            self._join(ae, ao, bo, be, ce, co)

    # O(logN * logU) expected -- the last i in [l, r] with a[i] < x, or -1 (each lane's walk pruned by the subtree
    # min); needs 0 <= l <= r < size(), else IndexError
    def rightmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        be, bo, mark = self._laneNodes(l, r)
        i, j = self._laneRightmostLtX(be, x), self._laneRightmostLtX(bo, x)
        self._release(mark)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return max(i, j)

    # O(logN * logU) expected -- the last i in [l, r] with a[i] <= x, or -1 (each lane's walk pruned by the subtree
    # min); needs 0 <= l <= r < size(), else IndexError
    def rightmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        be, bo, mark = self._laneNodes(l, r)
        i, j = self._laneRightmostLteX(be, x), self._laneRightmostLteX(bo, x)
        self._release(mark)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return max(i, j)

    # O(logN * logU) expected -- (a[0..k-1], a[k..]) as two PairSwapTreaps of their own; this one is left empty; needs
    # 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError(f"split: needs 0 <= k <= size(), got k = {k}, n = {self.size()}")
        left, right = self._empty(), self._empty()
        left.rE, left.rO, right.rE, right.rO = self._psplit(self.rE, self.rO, k)
        self.rE = self.rO = 0
        return left, right

    # O(logN * logU) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PairSwapTreaps of their own; this one is left
    # empty; needs 0 <= l <= r < size(), else IndexError
    def trisect(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"trisect: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.rE, left.rO, mid.rE, mid.rO, right.rE, right.rO = self._cut(l, r)
        self.rE = self.rO = 0
        return left, mid, right

    # O(log(N)*log(U) expected ?) -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        n = self.size()
        if n < 1:
            raise IndexError("pop: needs size() >= 1")
        v = self.pointGet(n - 1)
        self.cut(n - 1, n - 1)
        return v

    # O(log(N)*log(U) expected ?) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        v = self.pointGet(0)
        self.cut(0, 0)
        return v

    # O(1) -- sum of the whole array a[0..n-1] (read off the root); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.size() < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.sm[self.rE] + self.sm[self.rO]

    # O(log(N)*log(U) expected ?) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.size() < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.size() - 1)

    # O(log(N)*log(U) expected ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else raises IndexError
    def gcdAll(self):
        if self.size() < 1:
            raise IndexError("gcdAll: needs n >= 1")
        return self.rangeGcd(0, self.size() - 1)

    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        self.sm.append(v)
        self.mn.append(v)
        self.g.append(0)
        self.fv.append(v)
        self.lv.append(v)
        self.rev.append(0)
        self.asg.append(0)
        self.hasAsg.append(0)
        self.add.append(0)
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
        m = v
        if l and self.mn[l] < m:
            m = self.mn[l]
        if r and self.mn[r] < m:
            m = self.mn[r]
        self.mn[x] = m
        g = gcd(self.g[l], self.g[r])
        if l:
            g = gcd(g, v - self.lv[l])
        if r:
            g = gcd(g, self.fv[r] - v)
        self.g[x] = g
        self.fv[x] = self.fv[l] if l else v
        self.lv[x] = self.lv[r] if r else v

    def _applyRev(self, x):  # reverse x's subtree
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
            self.fv[x], self.lv[x] = self.lv[x], self.fv[x]

    def _applyAssign(self, x, v):  # every value of x's subtree becomes v
        if x:
            n = self.sz[x]
            self.val[x] = v
            self.sm[x] = v * n
            self.mn[x] = v
            self.g[x] = 0
            self.fv[x] = self.lv[x] = v
            self.asg[x], self.hasAsg[x] = v, 1
            self.add[x] = 0  # (an add pending below the assign is gone)

    def _applyAdd(self, x, v):  # every value of x's subtree gains v
        if x:
            self.val[x] += v
            self.sm[x] += v * self.sz[x]
            self.mn[x] += v
            self.fv[x] += v
            self.lv[x] += v
            self.add[x] += v

    def _push(self, x):  # hand x's pending tags to its children
        if self.rev[x]:
            self._applyRev(self.L[x])
            self._applyRev(self.R[x])
            self.rev[x] = 0
        if self.hasAsg[x]:
            self._applyAssign(self.L[x], self.asg[x])
            self._applyAssign(self.R[x], self.asg[x])
            self.hasAsg[x] = 0
        if self.add[x]:
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

    def _laneLeftmostLtX(self, t, x):  # the first k with lane value k < x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mn
        if not t or not F[t] < x:
            return -1
        i = 0
        while True:
            self._push(t)
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
            self._push(t)
            if L[t] and F[L[t]] <= x:
                t = L[t]
            elif val[t] <= x:
                return i + sz[L[t]]
            else:
                i += sz[L[t]] + 1
                t = R[t]

    def _laneRightmostLtX(self, t, x):  # the last k with lane value k < x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mn
        if not t or not F[t] < x:
            return -1
        i = 0
        while True:
            self._push(t)
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
            self._push(t)
            if R[t] and F[R[t]] <= x:
                i += sz[L[t]] + 1
                t = R[t]
            elif val[t] <= x:
                return i + sz[L[t]]
            else:
                t = L[t]



    # a node over a[l..r] of t's subtree: t itself when it is all of it, else temporaries made only where two parts meet
    # (pending tags on the way pushed down)
    def _rq(self, t, l, r):
        sz = self.sz
        if not t or r < 0 or l >= sz[t]:
            return 0
        if l <= 0 and sz[t] - 1 <= r:
            return t
        self._push(t)
        ls = sz[self.L[t]]
        if r < ls:
            return self._rq(self.L[t], l, r)
        if l > ls:
            return self._rq(self.R[t], l - ls - 1, r - ls - 1)
        a, b = self._rq(self.L[t], l, r), self._rq(self.R[t], l - ls - 1, r - ls - 1)
        y = self._clone(t)
        self.L[y], self.R[y] = a, b
        self._pull(y)
        return y

    def _clone(self, x):  # a temporary copy of node x (sharing its children), dropped by _release
        y = len(self.val)
        for arr in (self.val, self.pri, self.L, self.R, self.sz, self.sm, self.mn, self.g, self.fv, self.lv,
                    self.rev, self.asg, self.hasAsg, self.add):
            arr.append(arr[x])
        return y

    def _release(self, mark):  # drop every node made after mark (temporaries: no tree points to them)
        for arr in (self.val, self.pri, self.L, self.R, self.sz, self.sm, self.mn, self.g, self.fv, self.lv,
                    self.rev, self.asg, self.hasAsg, self.add):
            del arr[mark:]

    # the update on a[l..r] of t's subtree, in place: f(x, off) on a node x covered whole, h(w, off) the new value of a
    # lone value w (off: the distance from l). Only the nodes on the range's two boundary paths are recomputed, nothing
    # is cut out
    def _upd(self, t, l, r, f, h):
        sz = self.sz
        if not t or r < 0 or l >= sz[t]:
            return
        if l <= 0 and sz[t] - 1 <= r:
            f(t, -l)
            return
        self._push(t)
        ls = sz[self.L[t]]
        self._upd(self.L[t], l, r, f, h)
        self._upd(self.R[t], l - ls - 1, r - ls - 1, f, h)
        if l <= ls <= r:
            self.val[t] = h(self.val[t], ls - l)
        self._pull(t)

    def _lanes(self, l, r):  # (lane, first k, last k) holding a[l], a[l + 2], ..., then the one holding a[l + 1], a[l + 3], ...
        roots = (self.rE, self.rO)
        e = (roots[l % 2], l // 2, (r - (r - l) % 2) // 2)
        o = (roots[(l + 1) % 2], (l + 1) // 2, (r - (r - l - 1) % 2) // 2) if l < r else (0, 0, -1)
        return e, o

    def _laneNodes(self, l, r):  # (temporary nodes over the two lane slices of a[l..r], the pool size _release goes back to)
        mark = len(self.val)
        (te, le, he), (to, lo, ho) = self._lanes(l, r)
        return self._rq(te, le, he), self._rq(to, lo, ho), mark


# Example (pieces move between treaps; merge appends and leaves its argument empty):
#     t = PairSwapTreap([1, 2, 3, 4, 5])
#     left, mid, right = t.trisect(1, 3)  # left = [1], mid = [2, 3, 4], right = [5]; t is empty now
#     t.merge(right)                      # t = [5]
#     t.merge(mid)                        # t = [5, 2, 3, 4]
#     t.merge(left)                       # t = [5, 2, 3, 4, 1]
