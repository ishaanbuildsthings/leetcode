# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/treap-value-map-counts-sums/template.py
# @operations: append appendLeft countOccurrences cut getAll insertAt insertCopiesAt leftmostIndexOf leftmostIndexOfInRange merge paste pointAssign pointGet pop popLeft rangeAssign rangeReplace rangeRotateLeft rangeRotateRight rangeSum rightmostIndexOf rightmostIndexOfInRange size split sumAll trisect
# @data-structure-type: treap
# @complexities:
#   append: U*log(N) expected
#   appendLeft: U*log(N) expected
#   countOccurrences: U*log(N) expected
#   cut: U*log(N) expected
#   getAll: N*log(N) expected
#   insertAt: U*log(N) expected
#   insertCopiesAt: U*log(N) expected
#   leftmostIndexOf: U*log(N) expected
#   leftmostIndexOfInRange: U*log(N) expected
#   merge: U*log(N) expected
#   paste: U*log(N) expected
#   pointAssign: U*log(N) expected
#   pointGet: log(N) expected
#   rangeAssign: U*log(N) expected
#   rangeReplace: U*log(N) expected
#   rangeRotateLeft: U*log(N) expected
#   rangeRotateRight: U*log(N) expected
#   rangeSum: U*log(N) expected
#   rightmostIndexOf: U*log(N) expected
#   rightmostIndexOfInRange: U*log(N) expected
#   split: U*log(N) expected
#   trisect: U*log(N) expected
#   size: 1
#   pop: U*log(N) expected
#   popLeft: U*log(N) expected
#   sumAll: U*log(N) expected
#   build: N*U
# @memory:
#   layout: none
#   node: val[1*N] L[1*N] R[1*N] sz[1*N] pri[1*N] cnt[1*N*U] sm[1*N]
#   tags: mp[1*N*U]
#   other: none
#   note: N = every value ever inserted (nodes are never freed); U = valHi - valLo + 1; every ValueMapTreap shares one node pool; a pending tag is a whole map old value -> new value, so a push costs O(U)

import random

# Implicit treap whose lazy tag is a value map (mass change, CF 911G, with sequence edits): an array you can insert
# into anywhere, rotate, cut pieces out of (that is how to erase) and paste them back; plus rangeReplace(l, r, x, y)
# (every x in a[l..r] becomes y) and rangeAssign, in O(U log N) expected, U = valHi - valLo + 1: good when the values
# are few. A pending tag is a map old value -> new value, so any mix of changes composes into one map. Each node also
# keeps how many times each value appears in its subtree and its sum (countOccurrences, where x first / last appears,
# rangeSum; read without changing anything). All indices 0-based, ranges inclusive [l, r], an index always the
# position in the CURRENT array; searches return -1 when nothing qualifies.
class ValueMapTreap:
    # one node pool shared by every ValueMapTreap: pieces move between them (node 0 = the empty tree); nodes are never
    # freed. val[x]: x's value - valLo (every map that reached x already applied); mp[x]: the map x still owes its
    # children (None: none)
    val = [0]
    pri = [0]
    L = [0]
    R = [0]
    sz = [0]
    mp = [None]
    cnt = [None]
    sm = [0]
    __slots__ = ("root", "valLo", "U")

    # O(N*U) -- arr: the initial array (a list); every value it will ever hold must be in [valLo, valHi]
    def __init__(self, arr, valLo, valHi):
        self.valLo, self.U = valLo, valHi - valLo + 1
        self.root = self._build([self._off(v) for v in arr])

    def _empty(self):  # a new, empty one (same pool, same value range)
        piece = ValueMapTreap.__new__(ValueMapTreap)
        piece.root, piece.valLo, piece.U = 0, self.valLo, self.U
        return piece

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(U*logN) expected -- append v to the end; needs valLo <= v <= valHi
    def append(self, v):
        self.root = self._merge(self.root, self._new(self._off(v)))

    # O(U*logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(U*logN) expected -- insert v so it becomes a[i]; needs valLo <= v <= valHi; needs 0 <= i <= size(), else
    # IndexError
    def insertAt(self, i, v):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._new(self._off(v))), c)

    # O(k*U + U*logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    # 0 <= i <= size(), else IndexError
    def insertCopiesAt(self, i, v, k):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertCopiesAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        if k > 0:
            o = self._off(v)
            a, c = self._split(self.root, i)
            self.root = self._merge(self._merge(a, self._build([o] * k)), c)

    # O(U*logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0); needs
    # 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"cut: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        self.root = self._merge(a, c)
        piece = self._empty()
        piece.root = b
        return piece

    # O(U*logN) expected -- insert all of other (e.g. a cut piece) so it starts at a[i]; other is left empty; needs
    # 0 <= i <= size(), else IndexError
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError(f"paste: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), c)
        other.root = 0

    # O(U*logN) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(U*logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty; needs
    # 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError(f"split: needs 0 <= k <= size(), got k = {k}, n = {self.size()}")
        left, right = self._empty(), self._empty()
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(U*logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty; needs
    # 0 <= l <= r < size(), else IndexError
    def trisect(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"trisect: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.root, mid.root, right.root = self._cut(l, r)
        self.root = 0
        return left, mid, right

    # O(U*logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    # taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateLeft(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateLeft: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)

    # O(U*logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    # (negative shifts left); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateRight(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateRight: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self.rangeRotateLeft(l, r, -k)

    # O(logN) expected -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        L, R, sz, t, f, path = self.L, self.R, self.sz, self.root, 0, []
        while True:
            lt, rt = (R[t], L[t]) if f else (L[t], R[t])
            ls = sz[lt]
            if i == ls:
                break
            path.append(t)
            if i < ls:
                t = lt
            else:
                i -= ls + 1
                t = rt
        v = self.val[t]
        for y in reversed(path):  # (a map higher up is newer: apply them bottom-up)
            m = self.mp[y]
            if m is not None:
                v = m[v]
        return v + self.valLo

    # O(U*logN) expected -- a[i] = v; needs valLo <= v <= valHi; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        o = self._off(v)
        a, b, c = self._cut(i, i)
        self.val[b] = o
        self._pull(b)
        self._join(a, b, c)

    # O(U*logN) expected -- every a[i] == x with l <= i <= r becomes y; needs valLo <= y <= valHi; needs
    # 0 <= l <= r < size(), else IndexError
    def rangeReplace(self, l, r, x, y):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeReplace: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b = self._off(y)
        a = x - self.valLo
        if 0 <= a < self.U and a != b:
            p, q, s = self._cut(l, r)
            self._applyRep(q, a, b)
            self._join(p, q, s)

    # O(U*logN) expected -- a[l..r] = v; needs valLo <= v <= valHi; needs 0 <= l <= r < size(), else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        o = self._off(v)
        a, b, c = self._cut(l, r)
        self._applyMap(b, [o] * self.U)
        self._join(a, b, c)

    # O(N logN) expected -- the whole current array (read without changing anything)
    def getAll(self):
        L, R, val, mp, lo, out, path = self.L, self.R, self.val, self.mp, self.valLo, [], []

        def go(t, f):
            if not t:
                return
            lt, rt = (R[t], L[t]) if f else (L[t], R[t])
            path.append(t)
            go(lt, f)
            path.pop()
            v = val[t]
            for y in reversed(path):
                if mp[y] is not None:
                    v = mp[y][v]
            out.append(v + lo)
            path.append(t)
            go(rt, f)
            path.pop()
        go(self.root, 0)
        return out

    # O(U*logN) expected -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a = x - self.valLo
        if not 0 <= a < self.U:
            return 0
        return self._fold(self.root, l, r, None, 0, lambda t, g: self._countWhole(t, a, g), lambda v: v == a)

    # O(U*logN) expected -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        return self._findIn(0, self.size() - 1, x, True)

    # O(U*logN) expected -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        return self._findIn(0, self.size() - 1, x, False)

    # O(U*logN) expected -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs
    # 0 <= l <= r < size(), else IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._findIn(l, r, x, True)

    # O(U*logN) expected -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs
    # 0 <= l <= r < size(), else IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._findIn(l, r, x, False)

    # O(U*logN) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeSum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        lo = self.valLo
        return self._fold(self.root, l, r, None, 0, self._sumWhole, lambda v: v + lo)

    # O(U*log(N) expected) -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        n = self.size()
        if n < 1:
            raise IndexError("pop: needs size() >= 1")
        v = self.pointGet(n - 1)
        self.cut(n - 1, n - 1)
        return v

    # O(U*log(N) expected) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        v = self.pointGet(0)
        self.cut(0, 0)
        return v

    # O(U*log(N) expected) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.size() < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.size() - 1)

    # ---- internals ----

    def _off(self, v):  # v's index into a map
        o = v - self.valLo
        if not 0 <= o < self.U:
            raise ValueError(f"value {v} is outside [valLo, valHi]")
        return o

    def _new(self, o):  # a node holding offset o
        x = len(self.val)
        self.val.append(o)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        self.mp.append(None)
        c = [0] * self.U
        c[o] = 1
        self.cnt.append(c)
        self.sm.append(o + self.valLo)
        return x
        self.cnt.append(self.cnt[x][:])

    def _build(self, offs):  # a treap of new nodes holding offs in order: a Cartesian tree in one pass, O(len)
        pri, L, R = self.pri, self.L, self.R
        stack = []
        for o in offs:
            x, last = self._new(o), 0
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
        c = [0] * self.U
        for y in (l, r):
            if y:
                c = [p + q for p, q in zip(c, self.cnt[y])]
        c[self.val[x]] += 1
        self.cnt[x] = c
        self.sm[x] = self.sm[l] + self.sm[r] + self.val[x] + self.valLo

    def _applyMap(self, x, g):  # x's subtree goes through map g (newer than anything already in it)
        if not x:
            return
        self.val[x] = g[self.val[x]]
        m = self.mp[x]
        self.mp[x] = g[:] if m is None else [g[v] for v in m]
        c, new = self.cnt[x], [0] * self.U
        for v in range(self.U):
            if c[v]:
                new[g[v]] += c[v]
        self.cnt[x] = new
        lo = self.valLo
        self.sm[x] = sum((v + lo) * w for v, w in enumerate(new) if w)

    def _applyRep(self, x, a, b):  # every a in x's subtree becomes b
        if not x:
            return
        if self.val[x] == a:
            self.val[x] = b
        m = self.mp[x]
        self.mp[x] = [b if v == a else v for v in (m if m is not None else range(self.U))]
        c = self.cnt[x]
        self.sm[x] += (b - a) * c[a]
        c[b] += c[a]
        c[a] = 0

    def _push(self, x):  # hand x's pending tags to its children
        g = self.mp[x]
        if g is None:
            return
        if g is not None:
            self._applyMap(self.L[x], g)
            self._applyMap(self.R[x], g)
            self.mp[x] = None

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

    def _cut(self, l, r):  # (a[0..l-1], a[l..r], a[r+1..])
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    def _join(self, a, b, c):
        self.root = self._merge(self._merge(a, b), c)

    def _compose(self, g, m):  # the map "m, then g" (None: no map)
        if m is None:
            return g
        return m if g is None else [g[v] for v in m]

    def _countWhole(self, t, a, g):  # how many values in t's subtree are a once map g (None: none) is applied
        c = self.cnt[t]
        return c[a] if g is None else sum(c[v] for v in range(self.U) if g[v] == a)

    def _sumWhole(self, t, g):  # the sum of t's subtree once map g (None: none) is applied
        if g is None:
            return self.sm[t]
        c, lo = self.cnt[t], self.valLo
        return sum((g[v] + lo) * c[v] for v in range(self.U) if c[v])

    # whole(subtree, map) summed over the subtrees inside a[l..r] of t's, plus one(value) for each node only partly
    # inside; g: the maps above t not yet handed down, f: a reverse above t not yet handed down (changes nothing)
    def _fold(self, t, l, r, g, f, whole, one):
        sz = self.sz
        if not t or r < 0 or l >= sz[t]:
            return 0
        if l <= 0 and sz[t] - 1 <= r:
            return whole(t, g)
        lt, rt = (self.R[t], self.L[t]) if f else (self.L[t], self.R[t])
        h, ls, v = self._compose(g, self.mp[t]), sz[lt], self.val[t]
        res = self._fold(lt, l, r, h, f, whole, one) + self._fold(rt, l - ls - 1, r - ls - 1, h, f, whole, one)
        return res + one(g[v] if g is not None else v) if l <= ls <= r else res

    def _findIn(self, l, r, x, left):
        a = x - self.valLo
        return self._find(self.root, l, r, a, None, 0, left) if 0 <= a < self.U else -1

    def _find(self, t, l, r, a, g, f, left):  # the first (left) / last index in [l, r] of t's subtree holding a, or -1
        sz = self.sz
        if not t or r < 0 or l >= sz[t] or l <= 0 and sz[t] - 1 <= r and not self._countWhole(t, a, g):
            return -1
        lt, rt = (self.R[t], self.L[t]) if f else (self.L[t], self.R[t])
        h, ls, v = self._compose(g, self.mp[t]), sz[lt], self.val[t]
        parts = ((lt, 0), (-1, ls), (rt, ls + 1))
        for c, off in (parts if left else parts[::-1]):
            if c == -1:
                if l <= ls <= r and (g[v] if g is not None else v) == a:
                    return ls
                continue
            res = self._find(c, l - off, r - off, a, h, f, left)
            if res != -1:
                return res + off
        return -1
