# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pair-treap-min-max-or/template.py
# @operations: append appendLeft cut getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostLtX leftmostLteX merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeOrQuery rangeRotateLeft rangeRotateRight rangeTwinSpin rightmostGtX rightmostGteX rightmostLtX rightmostLteX split trisect
# @data-structure-type: pair-treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   leftmostGtX: log(N) expected
#   leftmostGteX: log(N) expected
#   leftmostLtX: log(N) expected
#   leftmostLteX: log(N) expected
#   merge: log(N) expected
#   paste: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   rangeMax: log(N) expected
#   rangeMin: log(N) expected
#   rangeOrQuery: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangeTwinSpin: log(N) expected
#   rightmostGtX: log(N) expected
#   rightmostGteX: log(N) expected
#   rightmostLtX: log(N) expected
#   rightmostLteX: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] mn[1*N] mx[1*N] orr[1*N]
#   tags: none
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); two treaps per array (even / odd positions); every PairSwapTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

# Implicit treap pair: an array you can insert into anywhere, swap adjacent pairs in a range (rangeTwinSpin: a[l] <->
# a[l + 1], a[l + 2] <-> a[l + 3], ...), rotate, cut pieces out of (that is how to erase) and paste them back in
# O(logN) expected each. The values at even positions a[0], a[2], ... are one treap (lane E) and the odd ones another
# (lane O), in one node pool; a range [l, r] is a slice of each, and each node keeps its min, its max, its OR over its
# subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches
# return -1 when nothing qualifies.
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
    mn = [0]
    mx = [0]
    orr = [0]
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

    # O(logN) expected -- remove a[l..r] and return it as a PairSwapTreap of its own (indices from 0); needs
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

    # O(logN) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else IndexError (i = size() appends)
    def insertAt(self, i, v):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
        ae, ao = self._pmerge(ae, ao, self._newNode(v), 0)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)

    # O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    # 0 <= i <= size(), else IndexError
    def insertCopiesAt(self, i, v, k):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertCopiesAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        if k > 0:
            ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
            ae, ao = self._pmerge(ae, ao, self._build([v] * ((k + 1) // 2)), self._build([v] * (k // 2)))
            self.rE, self.rO = self._pmerge(ae, ao, ce, co)

    # O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (each lane's walk pruned by the subtree max);
    # needs 0 <= l <= r < size(), else IndexError
    def leftmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneLeftmostGtX(be, x), self._laneLeftmostGtX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return i if j < 0 else j if i < 0 else min(i, j)

    # O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (each lane's walk pruned by the subtree max);
    # needs 0 <= l <= r < size(), else IndexError
    def leftmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneLeftmostGteX(be, x), self._laneLeftmostGteX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return i if j < 0 else j if i < 0 else min(i, j)

    # O(logN) expected -- the first i in [l, r] with a[i] < x, or -1 (each lane's walk pruned by the subtree min);
    # needs 0 <= l <= r < size(), else IndexError
    def leftmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneLeftmostLtX(be, x), self._laneLeftmostLtX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return i if j < 0 else j if i < 0 else min(i, j)

    # O(logN) expected -- the first i in [l, r] with a[i] <= x, or -1 (each lane's walk pruned by the subtree min);
    # needs 0 <= l <= r < size(), else IndexError
    def leftmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneLeftmostLteX(be, x), self._laneLeftmostLteX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return i if j < 0 else j if i < 0 else min(i, j)

    # O(logN) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.rE, self.rO = self._pmerge(self.rE, self.rO, other.rE, other.rO)
        other.rE = other.rO = 0

    # O(logN) expected -- insert all of other (any PairSwapTreap, e.g. a cut piece) so it starts at a[i] (needs
    # 0 <= i <= size(), else IndexError); other is left empty
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError(f"paste: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
        ae, ao = self._pmerge(ae, ao, other.rE, other.rO)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)
        other.rE = other.rO = 0

    # O(logN) expected -- a[i] += v; needs 0 <= i < size(), else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAdd: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = self.val[t] + v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = v; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmax: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = max(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else IndexError
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

    # O(logN) expected -- max of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMax: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = self.mx[be] if not bo else max(self.mx[be], self.mx[bo])
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN) expected -- min of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMin: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = self.mn[be] if not bo else min(self.mn[be], self.mn[bo])
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN) expected -- a[l] | ... | a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeOrQuery(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeOrQuery: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        res = self.orr[be] | self.orr[bo]
        self._join(ae, ao, be, bo, ce, co)
        return res

    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is taken
    # mod the length (negative shifts right); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateLeft(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateLeft: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        k %= r - l + 1
        if k:
            ae, ao, be, bo, ce, co = self._cut(l, r)
            xe, xo, ye, yo = self._psplit(be, bo, k)
            be, bo = self._pmerge(ye, yo, xe, xo)
            self._join(ae, ao, be, bo, ce, co)

    # O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    # (negative shifts left); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateRight(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateRight: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self.rangeRotateLeft(l, r, -k)

    # O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length: a[r] stays): the
    # pairs' two lanes trade places; needs 0 <= l <= r < size(), else IndexError
    def rangeTwinSpin(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeTwinSpin: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        k = (r - l + 1) // 2
        if k:
            ae, ao, be, bo, ce, co = self._cut(l, l + 2 * k - 1)
            self._join(ae, ao, bo, be, ce, co)

    # O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (each lane's walk pruned by the subtree max);
    # needs 0 <= l <= r < size(), else IndexError
    def rightmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneRightmostGtX(be, x), self._laneRightmostGtX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return max(i, j)

    # O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (each lane's walk pruned by the subtree max);
    # needs 0 <= l <= r < size(), else IndexError
    def rightmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneRightmostGteX(be, x), self._laneRightmostGteX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return max(i, j)

    # O(logN) expected -- the last i in [l, r] with a[i] < x, or -1 (each lane's walk pruned by the subtree min);
    # needs 0 <= l <= r < size(), else IndexError
    def rightmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneRightmostLtX(be, x), self._laneRightmostLtX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return max(i, j)

    # O(logN) expected -- the last i in [l, r] with a[i] <= x, or -1 (each lane's walk pruned by the subtree min);
    # needs 0 <= l <= r < size(), else IndexError
    def rightmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        ae, ao, be, bo, ce, co = self._cut(l, r)
        i, j = self._laneRightmostLteX(be, x), self._laneRightmostLteX(bo, x)
        self._join(ae, ao, be, bo, ce, co)
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return max(i, j)

    # O(logN) expected -- (a[0..k-1], a[k..]) as two PairSwapTreaps of their own; this one is left empty; needs
    # 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError(f"split: needs 0 <= k <= size(), got k = {k}, n = {self.size()}")
        left, right = self._empty(), self._empty()
        left.rE, left.rO, right.rE, right.rO = self._psplit(self.rE, self.rO, k)
        self.rE = self.rO = 0
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PairSwapTreaps of their own; this one is left empty;
    # needs 0 <= l <= r < size(), else IndexError
    def trisect(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"trisect: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
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
        self.orr.append(v)
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
        self.orr[x] = self.orr[l] | v | self.orr[r]

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
