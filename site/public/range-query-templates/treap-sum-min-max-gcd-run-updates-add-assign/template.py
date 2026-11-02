# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-min-max-gcd-run-updates-add-assign/template.py
# @operations: append appendLeft cut getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostLtX leftmostLteX longestEqualRun merge moveRange paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeGcd rangeMax rangeMin rangeRotateLeft rangeRotateRight rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX split trisect
# @data-structure-type: treap
# @complexities:
#   append: log(N)*log(U) expected ?
#   appendLeft: log(N)*log(U) expected ?
#   cut: log(N)*log(U) expected ?
#   getAll: N
#   insertAt: log(N)*log(U) expected ?
#   insertCopiesAt: log(N)*log(U) expected ?
#   leftmostGtX: log(N)*log(U) expected ?
#   leftmostGteX: log(N)*log(U) expected ?
#   leftmostLtX: log(N)*log(U) expected ?
#   leftmostLteX: log(N)*log(U) expected ?
#   longestEqualRun: log(N)*log(U) expected ?
#   merge: log(N)*log(U) expected ?
#   moveRange: log(N)*log(U) expected ?
#   paste: log(N)*log(U) expected ?
#   pointAdd: log(N)*log(U) expected ?
#   pointAssign: log(N)*log(U) expected ?
#   pointChmax: log(N)*log(U) expected ?
#   pointChmin: log(N)*log(U) expected ?
#   pointGet: log(N) expected
#   rangeAdd: log(N)*log(U) expected ?
#   rangeAssign: log(N)*log(U) expected ?
#   rangeGcd: log(N)*log(U) expected ?
#   rangeMax: log(N)*log(U) expected ?
#   rangeMin: log(N)*log(U) expected ?
#   rangeRotateLeft: log(N)*log(U) expected ?
#   rangeRotateRight: log(N)*log(U) expected ?
#   rangeSum: log(N)*log(U) expected ?
#   rightmostGtX: log(N)*log(U) expected ?
#   rightmostGteX: log(N)*log(U) expected ?
#   rightmostLtX: log(N)*log(U) expected ?
#   rightmostLteX: log(N)*log(U) expected ?
#   split: log(N)*log(U) expected ?
#   trisect: log(N)*log(U) expected ?
#   build: N*log(U) ?
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] mx[1*N] g[1*N] fv[1*N] lv[1*N] pr[1*N] sr[1*N] br[1*N]
#   tags: asg[1*N] hasAsg[1*N] add[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

# Implicit treap with composable aggregates: an array you can insert into anywhere, rotate, move, cut pieces out of
# (that is how to erase) and paste them back in O(logN) expected each, with rangeAdd, rangeAssign; each node keeps its
# sum, its min, its max, its gcd, its first / last value and the equal runs at its ends and inside over its subtree.
# All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1
# when nothing qualifies. Lazy tags mean "already applied to this node, not yet to its children"; a pending assign
# comes before a pending add.
import random
from math import gcd


class ImplicitTreap:
    # one node pool shared by every ImplicitTreap: cut / paste move nodes between them, so a piece from one can go
    # into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    # whole run), so there is nothing to reset between test cases
    val = [0]
    pri = [0]
    L = [0]
    R = [0]
    sz = [0]
    sm = [0]
    mn = [0]
    mx = [0]
    g = [0]
    fv = [0]
    lv = [0]
    pr = [0]
    sr = [0]
    br = [0]
    asg = [0]
    hasAsg = [0]
    add = [0]
    __slots__ = ("root",)

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr))

    def _empty(self):  # a new, empty ImplicitTreap (on the same pool, like every one)
        return ImplicitTreap()

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN * logU) expected -- append v to the end
    def append(self, v):
        self.root = self._merge(self.root, self._newNode(v))

    # O(logN * logU) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN * logU) expected -- remove a[l..r] and return it as a treap of its own (indices from 0; drop it to erase)
    def cut(self, l, r):
        a, b, c = self._cut(l, r)
        self.root = self._merge(a, c)
        piece = self._empty()
        piece.root = b
        return piece

    # O(N) -- the whole current array, every pending tag applied on the way
    def getAll(self):
        L, R, val = self.L, self.R, self.val
        out, stack, t = [], [], self.root
        while stack or t:
            while t:
                self._push(t)
                stack.append(t)
                t = L[t]
            t = stack.pop()
            out.append(val[t])
            t = R[t]
        return out

    # O(logN * logU) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._newNode(v)), c)

    # O(k + logN * logU) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    def insertCopiesAt(self, i, v, k):
        if k > 0:
            a, c = self._split(self.root, i)
            self.root = self._merge(self._merge(a, self._build([v] * k)), c)

    # O(logN * logU) expected -- the first i in [l, r] with a[i] > x, or -1 (pruned by the subtree max)
    def leftmostGtX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        t, i, res = b, 0, -1
        if t and F[t] > x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if L[t] and F[L[t]] > x:
                    t = L[t]
                elif val[t] > x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    i += sz[L[t]] + 1
                    t = R[t]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- the first i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max)
    def leftmostGteX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        t, i, res = b, 0, -1
        if t and F[t] >= x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if L[t] and F[L[t]] >= x:
                    t = L[t]
                elif val[t] >= x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    i += sz[L[t]] + 1
                    t = R[t]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- the first i in [l, r] with a[i] < x, or -1 (pruned by the subtree min)
    def leftmostLtX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mn
        t, i, res = b, 0, -1
        if t and F[t] < x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if L[t] and F[L[t]] < x:
                    t = L[t]
                elif val[t] < x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    i += sz[L[t]] + 1
                    t = R[t]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- the first i in [l, r] with a[i] <= x, or -1 (pruned by the subtree min)
    def leftmostLteX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mn
        t, i, res = b, 0, -1
        if t and F[t] <= x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if L[t] and F[L[t]] <= x:
                    t = L[t]
                elif val[t] <= x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    i += sz[L[t]] + 1
                    t = R[t]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- the longest run of equal adjacent values in a[l..r]
    def longestEqualRun(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.br[b]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(logN * logU) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    def moveRange(self, l, r, i):
        a, b, c = self._cut(l, r)
        x, y = self._split(self._merge(a, c), i)
        self.root = self._merge(self._merge(x, b), y)

    # O(logN * logU) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i]
    # (0 <= i <= size()); other is left empty
    def paste(self, i, other):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), c)
        other.root = 0

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

    # O(logN * logU) expected -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        a, b, c = self._cut(l, r)
        self._applyAdd(b, v)
        self._join(a, b, c)

    # O(logN * logU) expected -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        a, b, c = self._cut(l, r)
        self._applyAssign(b, v)
        self._join(a, b, c)

    # O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|
    def rangeGcd(self, l, r):
        a, b, c = self._cut(l, r)
        res = gcd(self.fv[b], self.g[b])
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- max of a[l..r]
    def rangeMax(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.mx[b]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- min of a[l..r]
    def rangeMin(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.mn[b]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    # it is taken mod the length (negative shifts right)
    def rangeRotateLeft(self, l, r, k):
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)

    # O(logN * logU) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left)
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)

    # O(logN * logU) expected -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.sm[b]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- the last i in [l, r] with a[i] > x, or -1 (pruned by the subtree max)
    def rightmostGtX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        t, i, res = b, 0, -1
        if t and F[t] > x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if R[t] and F[R[t]] > x:
                    i += sz[L[t]] + 1
                    t = R[t]
                elif val[t] > x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    t = L[t]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- the last i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max)
    def rightmostGteX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        t, i, res = b, 0, -1
        if t and F[t] >= x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if R[t] and F[R[t]] >= x:
                    i += sz[L[t]] + 1
                    t = R[t]
                elif val[t] >= x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    t = L[t]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- the last i in [l, r] with a[i] < x, or -1 (pruned by the subtree min)
    def rightmostLtX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mn
        t, i, res = b, 0, -1
        if t and F[t] < x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if R[t] and F[R[t]] < x:
                    i += sz[L[t]] + 1
                    t = R[t]
                elif val[t] < x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    t = L[t]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- the last i in [l, r] with a[i] <= x, or -1 (pruned by the subtree min)
    def rightmostLteX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mn
        t, i, res = b, 0, -1
        if t and F[t] <= x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if R[t] and F[R[t]] <= x:
                    i += sz[L[t]] + 1
                    t = R[t]
                elif val[t] <= x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    t = L[t]
        self._join(a, b, c)
        return res

    # O(logN * logU) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    def split(self, k):
        left, right = self._empty(), self._empty()
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(logN * logU) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.root, mid.root, right.root = self._cut(l, r)
        self.root = 0
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
        self.mn.append(v)
        self.mx.append(v)
        self.g.append(0)
        self.fv.append(v)
        self.lv.append(v)
        self.pr.append(1)
        self.sr.append(1)
        self.br.append(1)
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
        m = v
        if l and self.mx[l] > m:
            m = self.mx[l]
        if r and self.mx[r] > m:
            m = self.mx[r]
        self.mx[x] = m
        g = gcd(self.g[l], self.g[r])
        if l:
            g = gcd(g, v - self.lv[l])
        if r:
            g = gcd(g, self.fv[r] - v)
        self.g[x] = g
        pr = sr = br = 1
        if l:
            j = self.lv[l] == v
            pr = self.pr[l] + (1 if j and self.pr[l] == self.sz[l] else 0)
            sr = self.sr[l] + 1 if j else 1
            br = max(self.br[l], sr)
        if r:
            j = v == self.fv[r]
            rp, rs = self.pr[r], self.sr[r]
            br = max(br, self.br[r], sr + rp if j else 0)
            if j and pr == self.sz[l] + 1:
                pr += rp
            sr = rs + sr if j and rs == self.sz[r] else rs
        self.pr[x], self.sr[x], self.br[x] = pr, sr, br
        self.fv[x] = self.fv[l] if l else v
        self.lv[x] = self.lv[r] if r else v

    def _applyAssign(self, x, v):  # every value of x's subtree becomes v
        if x:
            n = self.sz[x]
            self.val[x] = v
            self.sm[x] = v * n
            self.mn[x] = v
            self.mx[x] = v
            self.g[x] = 0
            self.fv[x] = self.lv[x] = v
            self.pr[x] = self.sr[x] = self.br[x] = n
            self.asg[x], self.hasAsg[x] = v, 1
            self.add[x] = 0  # (an add pending below the assign is gone)

    def _applyAdd(self, x, v):  # every value of x's subtree gains v
        if x:
            self.val[x] += v
            self.sm[x] += v * self.sz[x]
            self.mn[x] += v
            self.mx[x] += v
            self.fv[x] += v
            self.lv[x] += v
            self.add[x] += v

    def _push(self, x):  # hand x's pending tags to its children
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

    def _cut(self, l, r):  # (a[0..l-1], a[l..r], a[r+1..])
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    def _join(self, a, b, c):
        self.root = self._merge(self._merge(a, b), c)

    def _find(self, i):  # (node holding a[i], the nodes above it), every tag on the way pushed
        L, sz, t, path = self.L, self.sz, self.root, []
        while True:
            self._push(t)
            ls = sz[L[t]]
            if i == ls:
                return t, path
            path.append(t)
            if i < ls:
                t = L[t]
            else:
                i -= ls + 1
                t = self.R[t]
