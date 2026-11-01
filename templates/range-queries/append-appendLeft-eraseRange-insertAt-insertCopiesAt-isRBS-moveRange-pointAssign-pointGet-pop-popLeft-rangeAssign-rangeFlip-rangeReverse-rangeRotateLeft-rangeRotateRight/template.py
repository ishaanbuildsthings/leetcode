# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/append-appendLeft-eraseRange-insertAt-insertCopiesAt-isRBS-moveRange-pointAssign-pointGet-pop-popLeft-rangeAssign-rangeFlip-rangeReverse-rangeRotateLeft-rangeRotateRight/template.py
# @operations: append appendLeft eraseRange getAll insertAt insertCopiesAt isRBS moveRange pointAssign pointGet pop popLeft rangeAssign rangeFlip rangeReverse rangeRotateLeft rangeRotateRight
# @data-structure-type: treap
# @letters: same
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   eraseRange: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   isRBS: log(N) expected
#   moveRange: log(N) expected
#   pointAssign: log(N) expected
#   pointGet: log(N) expected
#   pop: log(N) expected
#   popLeft: log(N) expected
#   rangeAssign: log(N) expected
#   rangeFlip: log(N) expected
#   rangeReverse: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] mx[1*N] mnS[1*N] mxS[1*N]
#   tags: rev[1*N] asg[1*N] hasAsg[1*N] flp[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused)

# Implicit treap: an array you can insert into / erase from anywhere, reverse, rotate and move ranges, each in O(logN)
# expected; the values are characters, openChar = +1 and closeChar = -1, and a range is a regular bracket sequence iff
# its sum is 0 and no prefix sum is negative; each node keeps its subtree's sum and min prefix sum (over prefixes
# including the empty one), and its max prefix sum (a flip negates every value: min and max swap and change sign), and
# its min / max suffix sum (a reverse swaps prefixes and suffixes). All indices 0-based, ranges inclusive [l, r], an
# index always the position in the CURRENT array. Lazy tags mean "already applied to this node, not yet to its
# children".
import random


class ImplicitTreap:
    __slots__ = ('root', 'val', 'pri', 'L', 'R', 'sz', 'sm', 'mn', 'mx', 'mnS', 'mxS', 'rev', 'asg', 'hasAsg', 'flp',
                 'oc', 'cc')

    # O(N) -- brackets: the sequence, a list of characters like ["(", ")", "("] (a str like "()(" works too);
    # openChar: the character that opens ("(" unless you pass e.g. "[")
    # closeChar: the character that closes (every character must be one of the two)
    def __init__(self, brackets, openChar="(", closeChar=")"):
        self.val, self.pri, self.L, self.R, self.sz = [0], [0], [0], [0], [0]  # node 0 = the empty tree
        self.oc = openChar
        self.cc = closeChar
        self.sm = [0]
        self.mn = [0]
        self.mx = [0]
        self.mnS = [0]
        self.mxS = [0]
        self.rev = [0]
        self.asg = [0]
        self.hasAsg = [0]
        self.flp = [0]
        self.root = self._build(list(brackets))

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

    # O(logN) expected -- is a[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    def isRBS(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.sm[b] == 0 and self.mn[b] >= 0
        self._join(a, b, c)
        return res

    # O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    def moveRange(self, l, r, i):
        a, b, c = self._cut(l, r)
        x, y = self._split(self._merge(a, c), i)
        self.root = self._merge(self._merge(x, b), y)

    # O(logN) expected -- a[i] = v
    def pointAssign(self, i, v):
        t, path = self._find(i)
        self.val[t] = v
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

    # O(logN) expected -- every open in a[l..r] becomes closeChar and every other character openChar
    def rangeFlip(self, l, r):
        a, b, c = self._cut(l, r)
        self._applyFlip(b)
        self._join(a, b, c)

    # O(logN) expected -- reverse a[l..r] in place
    def rangeReverse(self, l, r):
        a, b, c = self._cut(l, r)
        self._applyRev(b)
        self._join(a, b, c)

    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
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

    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        w = 1 if v == self.oc else -1
        self.sm.append(w)
        self.mn.append(w if w < 0 else 0)
        self.mnS.append(w if w < 0 else 0)
        self.mx.append(w if w > 0 else 0)
        self.mxS.append(w if w > 0 else 0)
        self.rev.append(0)
        self.asg.append(0)
        self.hasAsg.append(0)
        self.flp.append(0)
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
        v = 1 if self.val[x] == self.oc else -1
        a = self.sm[l] + v  # the left part and the node
        self.mn[x] = min(self.mn[l], a, a + self.mn[r])
        self.mx[x] = max(self.mx[l], a, a + self.mx[r])
        b = v + self.sm[r]  # the node and the right part
        self.mnS[x] = min(self.mnS[r], b, b + self.mnS[l])
        self.mxS[x] = max(self.mxS[r], b, b + self.mxS[l])
        self.sm[x] = a + self.sm[r]

    def _applyRev(self, x):
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
            self.mn[x], self.mnS[x] = self.mnS[x], self.mn[x]
            self.mx[x], self.mxS[x] = self.mxS[x], self.mx[x]

    def _applyAssign(self, x, ch):  # every character of x's subtree becomes ch
        if x:
            v = self.sz[x] if ch == self.oc else -self.sz[x]
            self.val[x], self.sm[x] = ch, v
            self.mn[x] = self.mnS[x] = v if v < 0 else 0
            self.mx[x] = self.mxS[x] = v if v > 0 else 0
            self.asg[x], self.hasAsg[x] = ch, 1
            self.flp[x] = 0  # (the assign overrides a pending flip)

    def _applyFlip(self, x):  # every open of x's subtree becomes a close and vice versa
        if x:
            self.val[x] = self.cc if self.val[x] == self.oc else self.oc
            self.sm[x] = -self.sm[x]
            self.mn[x], self.mx[x] = -self.mx[x], -self.mn[x]
            self.mnS[x], self.mxS[x] = -self.mxS[x], -self.mnS[x]
            self.flp[x] ^= 1

    def _push(self, x):  # hand x's pending tags to its children
        if self.rev[x]:
            self._applyRev(self.L[x])
            self._applyRev(self.R[x])
            self.rev[x] = 0
        if self.hasAsg[x]:
            self._applyAssign(self.L[x], self.asg[x])
            self._applyAssign(self.R[x], self.asg[x])
            self.hasAsg[x] = 0
        if self.flp[x]:  # (after the assign: a pending assign and flip mean assign, then flip)
            self._applyFlip(self.L[x])
            self._applyFlip(self.R[x])
            self.flp[x] = 0

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
