# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-min-max-xor-alt-rev/template.py
# @operations: append appendLeft cut getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostLtX leftmostLteX maxAltSubseqSum merge moveRange paste pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum rangeXorQuery rightmostGtX rightmostGteX rightmostLtX rightmostLteX split trisect
# @data-structure-type: treap
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
#   maxAltSubseqSum: log(N) expected
#   merge: log(N) expected
#   moveRange: log(N) expected
#   paste: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   rangeMax: log(N) expected
#   rangeMin: log(N) expected
#   rangeReverse: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangeSum: log(N) expected
#   rangeXorQuery: log(N) expected
#   rightmostGtX: log(N) expected
#   rightmostGteX: log(N) expected
#   rightmostLtX: log(N) expected
#   rightmostLteX: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] mx[1*N] xr[1*N] a00[1*N] a01[1*N] a10[1*N] a11[1*N]
#   tags: rev[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

# Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
# out of (that is how to erase) and paste them back in O(logN) expected each; each node keeps its sum, its min, its
# max, its xor, its best alternating (+ - + ...) subsequence sum for each start / end sign over its subtree. All
# indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when
# nothing qualifies. Lazy tags mean "already applied to this node, not yet to its children".
import random


INF, NEG = float("inf"), float("-inf")


def _altJoin(A, B):  # A's part, then B's: (++, +-, -+, --) = best by (start sign, end sign)
    a0, a1, a2, a3 = A
    b0, b1, b2, b3 = B
    return (max(a0, b0, a0 + b2, a1 + b0), max(a1, b1, a0 + b3, a1 + b1),
            max(a2, b2, a2 + b2, a3 + b0), max(a3, b3, a2 + b3, a3 + b1))


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
    xr = [0]
    a00 = [0]
    a01 = [0]
    a10 = [0]
    a11 = [0]
    rev = [0]
    __slots__ = ("root",)

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr))

    def _empty(self):  # a new, empty ImplicitTreap (on the same pool, like every one)
        return ImplicitTreap()

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN) expected -- append v to the end
    def append(self, v):
        self.root = self._merge(self.root, self._newNode(v))

    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0; drop it to erase)
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

    # O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._newNode(v)), c)

    # O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    def insertCopiesAt(self, i, v, k):
        if k > 0:
            a, c = self._split(self.root, i)
            self.root = self._merge(self._merge(a, self._build([v] * k)), c)

    # O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max)
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

    # O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max)
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

    # O(logN) expected -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min)
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

    # O(logN) expected -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the subtree min)
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

    # O(logN) expected -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]
    def maxAltSubseqSum(self, l, r):
        a, b, c = self._cut(l, r)
        res = max(self.a00[b], self.a01[b])
        self._join(a, b, c)
        return res

    # O(logN) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    def moveRange(self, l, r, i):
        a, b, c = self._cut(l, r)
        x, y = self._split(self._merge(a, c), i)
        self.root = self._merge(self._merge(x, b), y)

    # O(logN) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i]
    # (0 <= i <= size()); other is left empty
    def paste(self, i, other):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), c)
        other.root = 0

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

    # O(logN) expected -- max of a[l..r]
    def rangeMax(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.mx[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- min of a[l..r]
    def rangeMin(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.mn[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- reverse a[l..r] in place
    def rangeReverse(self, l, r):
        a, b, c = self._cut(l, r)
        self._applyRev(b)
        self._join(a, b, c)

    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    # it is taken mod the length (negative shifts right)
    def rangeRotateLeft(self, l, r, k):
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)

    # O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left)
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)

    # O(logN) expected -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.sm[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- a[l] ^ ... ^ a[r]
    def rangeXorQuery(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.xr[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max)
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

    # O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max)
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

    # O(logN) expected -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min)
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

    # O(logN) expected -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the subtree min)
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

    # O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    def split(self, k):
        left, right = self._empty(), self._empty()
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
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
        self.xr.append(v)
        self.a00.append(v)
        self.a01.append(NEG)
        self.a10.append(NEG)
        self.a11.append(-v)
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
        self.xr[x] = self.xr[l] ^ v ^ self.xr[r]
        c = (v, NEG, NEG, -v)
        if l:
            c = _altJoin((self.a00[l], self.a01[l], self.a10[l], self.a11[l]), c)
        if r:
            c = _altJoin(c, (self.a00[r], self.a01[r], self.a10[r], self.a11[r]))
        self.a00[x], self.a01[x], self.a10[x], self.a11[x] = c

    def _applyRev(self, x):  # reverse x's subtree
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
            self.a01[x], self.a10[x] = self.a10[x], self.a01[x]

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
