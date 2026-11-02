# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-beats-chmin-extra/template.py
# @operations: append appendLeft eraseRange getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostLtX leftmostLteX moveRange pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAssign rangeChmin rangeMax rangeMin rangeRotateLeft rangeRotateRight rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
# @data-structure-type: treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   eraseRange: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   leftmostGtX: log(N) expected
#   leftmostGteX: log(N) expected
#   leftmostLtX: log(N) expected
#   leftmostLteX: log(N) expected
#   moveRange: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   pop: log(N) expected
#   popLeft: log(N) expected
#   rangeAssign: log(N) expected
#   rangeChmin: log(N) amortized ?
#   rangeMax: log(N) expected
#   rangeMin: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangeSum: log(N) expected
#   rightmostGtX: log(N) expected
#   rightmostGteX: log(N) expected
#   rightmostLtX: log(N) expected
#   rightmostLteX: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mx[1*N] mx2[1*N] cmx[1*N] mn[1*N]
#   tags: none
#   other: none
#   note: N = every value ever inserted; no chmin / chmax / assign tags: a node's own max / min are its pending clamp, and a node whose values are all equal pushes that value as an assign

# Implicit treap with segment tree beats: range chmin (a[i] = min(a[i], x)) and range assign with range sums, the
# range max, the range min, on an array you can insert into / erase from anywhere, rotate, move. Each node keeps its
# max, strict second max and copies of the max over its subtree (its own value included), plus the sum. A chmin x
# stops at a node with second max < x: only the copies of the max move (the sum drops by (max - x) * copies). A node's
# own max / min double as its pending clamp: push clamps each child to them, so there are no chmin / chmax tags; and
# when all of a node's values are equal, push hands that value to both children as an assign, so there is no assign
# tag. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches
# return -1 when nothing qualifies.
import random


INF, NEG = float("inf"), float("-inf")


class ImplicitTreap:
    __slots__ = ('root', 'val', 'pri', 'L', 'R', 'sz', 'sm', 'mx', 'mx2', 'cmx', 'mn')

    # O(N) -- arr: the initial array (may be empty)
    def __init__(self, arr):
        self.val, self.pri, self.L, self.R, self.sz = [0], [0], [0], [0], [0]  # node 0 = the empty tree
        self.sm = [0]
        self.mx = [0]
        self.mx2 = [NEG]
        self.cmx = [0]
        self.mn = [0]
        self.root = self._build(list(arr))

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN) expected -- append v to the end
    def append(self, v):
        self.root = self._merge(self.root, self._newNode(v))

    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- remove a[l..r]
    def eraseRange(self, l, r):
        a, _, c = self._cut(l, r)
        self.root = self._merge(a, c)

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

    # O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    def moveRange(self, l, r, i):
        a, b, c = self._cut(l, r)
        x, y = self._split(self._merge(a, c), i)
        self.root = self._merge(self._merge(x, b), y)

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

    # O(logN) expected -- remove a[i] and return it; everything after it shifts left by one
    def pop(self, i):
        v = self.pointGet(i)
        self.eraseRange(i, i)
        return v

    # O(logN) expected -- remove a[0] and return it
    def popLeft(self):
        return self.pop(0)

    # O(logN) expected -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        a, b, c = self._cut(l, r)
        self._applyAssign(b, v)
        self._join(a, b, c)

    # amortized O(logN) expected -- a[i] = min(a[i], v) for i in [l, r]
    def rangeChmin(self, l, r, v):
        a, b, c = self._cut(l, r)
        self._chmin(b, v)
        self._join(a, b, c)

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

    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any k, negative shifts right
    def rangeRotateLeft(self, l, r, k):
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)

    # O(logN) expected -- cyclic shift a[l..r] right by k; any integer k, negative shifts left
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)

    # O(logN) expected -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.sm[b]
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

    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        self.sm.append(v)
        self.mx.append(v)
        self.mn.append(v)
        self.mx2.append(NEG)
        self.cmx.append(1)
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

    def _pull(self, x):  # recompute x from its children (its own value is one more value of the subtree)
        l, r = self.L[x], self.R[x]
        self.sz[x] = self.sz[l] + self.sz[r] + 1
        v = self.val[x]
        self.sm[x] = self.sm[l] + v + self.sm[r]
        m, m2, k = v, NEG, 1
        for y in (l, r):
            if y:
                a, a2 = self.mx[y], self.mx2[y]
                if a > m:
                    m, m2, k = a, (a2 if a2 > m else m), self.cmx[y]
                elif a == m:
                    k += self.cmx[y]
                    if a2 > m2:
                        m2 = a2
                elif a > m2:
                    m2 = a
        self.mx[x], self.mx2[x], self.cmx[x] = m, m2, k
        m = v
        if l and self.mn[l] < m:
            m = self.mn[l]
        if r and self.mn[r] < m:
            m = self.mn[r]
        self.mn[x] = m

    def _applyAssign(self, t, v):  # every value of t's subtree becomes v
        if t:
            n = self.sz[t]
            self.val[t] = v
            self.sm[t] = v * n
            self.mx[t] = v
            self.mn[t] = v
            self.mx2[t], self.cmx[t] = NEG, n

    def _applyChmin(self, t, v):  # chmin by v on t, with mx2 < v < mx: only the copies of the max move
        if self.mx2[t] == NEG:  # (all equal)
            self._applyAssign(t, v)
            return
        if self.val[t] == self.mx[t]:
            self.val[t] = v
        self.sm[t] -= (self.mx[t] - v) * self.cmx[t]
        self.mx[t] = v

    def _chmin(self, t, x):  # a[i] = min(a[i], x) over t's subtree, walking down only where x <= the second max
        if not t or self.mx[t] <= x:
            return
        if self.mx2[t] < x:
            self._applyChmin(t, x)
            return
        self._push(t)
        if self.val[t] > x:
            self.val[t] = x
        self._chmin(self.L[t], x)
        self._chmin(self.R[t], x)
        self._pull(t)

    def _push(self, t):  # hand t's pending changes to its children: all one value (an assign), else the add, then its clamp
        l, r = self.L[t], self.R[t]
        if self.mx2[t] == NEG:
            v = self.mx[t]
            self._applyAssign(l, v)
            self._applyAssign(r, v)
            return
        for y in (l, r):
            if y and self.mx[y] > self.mx[t]:
                self._applyChmin(y, self.mx[t])

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
