# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-xor-updates-assign-xor/template.py
# @operations: append appendLeft concat cut getAll insertAt insertCopiesAt moveRange paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeRotateLeft rangeRotateRight rangeXorApply rangeXorQuery split trisect
# @data-structure-type: treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   concat: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   moveRange: log(N) expected
#   paste: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   rangeAssign: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangeXorApply: log(N) expected
#   rangeXorQuery: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] xr[1*N]
#   tags: asg[1*N] hasAsg[1*N] tx[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); a treap and the pieces cut from it share their nodes (freed with the last of them: no reset needed)

# Implicit treap with composable aggregates: an array you can insert into anywhere, rotate, move, cut pieces out of
# (that is how to erase) and paste them back in O(logN) expected each, with rangeAssign, rangeXorApply; each node
# keeps its xor over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the
# CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet to
# its children"; a pending assign comes before a pending add.
import random


class ImplicitTreap:
    __slots__ = ('root', 'val', 'pri', 'L', 'R', 'sz', 'xr', 'asg', 'hasAsg', 'tx')

    # O(N) -- arr: the initial array (may be empty); like: an ImplicitTreap whose nodes this one shares, so pieces
    # can move between the two (pieces cut from a treap share its nodes already). No reset between test cases
    def __init__(self, arr=(), like=None):
        if like is None:
            self.val, self.pri, self.L, self.R, self.sz = [0], [0], [0], [0], [0]  # node 0 = the empty tree
            self.xr = [0]
            self.asg = [0]
            self.hasAsg = [0]
            self.tx = [0]
        else:
            self.val, self.pri, self.L, self.R, self.sz = like.val, like.pri, like.L, like.R, like.sz
            self.xr = like.xr
            self.asg = like.asg
            self.hasAsg = like.hasAsg
            self.tx = like.tx
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

    # O(logN) expected -- append all of other at the end; other is left empty
    def concat(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0; drop it to erase)
    def cut(self, l, r):
        a, b, c = self._cut(l, r)
        self.root = self._merge(a, c)
        piece = ImplicitTreap(like=self)
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

    # O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    def moveRange(self, l, r, i):
        a, b, c = self._cut(l, r)
        x, y = self._split(self._merge(a, c), i)
        self.root = self._merge(self._merge(x, b), y)

    # O(logN) expected -- insert other so it starts at a[i] (0 <= i <= size()), leaving it empty; it must
    # share this treap's nodes (a piece cut from it, or built with like=)
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

    # O(logN) expected -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        a, b, c = self._cut(l, r)
        self._applyAssign(b, v)
        self._join(a, b, c)

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

    # O(logN) expected -- a[i] ^= v for i in [l, r]
    def rangeXorApply(self, l, r, v):
        a, b, c = self._cut(l, r)
        self._applyXor(b, v)
        self._join(a, b, c)

    # O(logN) expected -- a[l] ^ ... ^ a[r]
    def rangeXorQuery(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.xr[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    def split(self, k):
        left, right = ImplicitTreap(like=self), ImplicitTreap(like=self)
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = ImplicitTreap(like=self), ImplicitTreap(like=self), ImplicitTreap(like=self)
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
        self.xr.append(v)
        self.asg.append(0)
        self.hasAsg.append(0)
        self.tx.append(0)
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
        self.xr[x] = self.xr[l] ^ v ^ self.xr[r]

    def _applyAssign(self, x, v):  # every value of x's subtree becomes v
        if x:
            n = self.sz[x]
            self.val[x] = v
            self.xr[x] = v if n & 1 else 0
            self.asg[x], self.hasAsg[x] = v, 1
            self.tx[x] = 0

    def _applyXor(self, x, v):  # every value of x's subtree is xored with v
        if x:
            self.val[x] ^= v
            if self.sz[x] & 1:
                self.xr[x] ^= v
            self.tx[x] ^= v

    def _push(self, x):  # hand x's pending tags to its children
        if self.hasAsg[x]:
            self._applyAssign(self.L[x], self.asg[x])
            self._applyAssign(self.R[x], self.asg[x])
            self.hasAsg[x] = 0
        if self.tx[x]:
            self._applyXor(self.L[x], self.tx[x])
            self._applyXor(self.R[x], self.tx[x])
            self.tx[x] = 0

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
