# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/eraseAt-eraseRange-insertAt-moveRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-pushBack-rangeReverse-rangeRotateLeft-rangeRotateRight/template.py
# @operations: eraseAt eraseRange insertAt moveRange pointAdd pointAssign pointChmax pointChmin pointGet pushBack rangeReverse rangeRotateLeft rangeRotateRight
# @data-structure-type: treap
# @complexities:
#   eraseAt: log(N) expected
#   eraseRange: log(N) expected
#   insertAt: log(N) expected
#   moveRange: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   pushBack: log(N) expected
#   rangeReverse: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N]
#   tags: rev[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insertAt; erased nodes are not reused); split / merge recurse O(log N) deep in expectation

# Implicit treap: an array you can insert into / erase from anywhere, reverse, rotate and cut-and-paste, each in
# O(logN) expected, plus point ops. All indices 0-based, ranges inclusive [l, r], and an index always means the
# position in the CURRENT array. Nodes keep their values in array order (an in-order walk); a node's position is the
# size of everything left of it. Lazy tags mean "already applied to this node, not yet to its children".
import random


class ImplicitTreap:
    __slots__ = ('root', 'val', 'pri', 'L', 'R', 'sz', 'rev')

    # O(N) -- arr: the initial array (may be empty)
    def __init__(self, arr):
        n = len(arr)
        self.val = [0] + list(arr)  # node 0 is the empty tree
        self.pri = [0] + [random.getrandbits(62) for _ in range(n)]
        self.L = [0] * (n + 1)
        self.R = [0] * (n + 1)
        self.sz = [0] + [1] * n
        self.rev = [0] * (n + 1)
        # Cartesian tree on (position, priority) in one pass: the stack is the current right spine
        pri, L, R = self.pri, self.L, self.R
        stack = []
        for x in range(1, n + 1):
            last = 0
            while stack and pri[stack[-1]] < pri[x]:
                last = stack.pop()
            L[x] = last
            if stack:
                R[stack[-1]] = x
            stack.append(x)
        self.root = stack[0] if stack else 0
        order, todo = [], ([self.root] if n else [])
        while todo:  # pre-order; pulled in reverse, so children before parents
            x = todo.pop()
            order.append(x)
            if L[x]:
                todo.append(L[x])
            if R[x]:
                todo.append(R[x])
        for x in reversed(order):
            self._pull(x)

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN) expected -- remove a[i]; everything after it shifts left by one
    def eraseAt(self, i):
        a, _, c = self._cut(i, i)
        self.root = self._merge(a, c)

    # O(logN) expected -- remove a[l..r]; everything after it shifts left by r - l + 1
    def eraseRange(self, l, r):
        a, _, c = self._cut(l, r)
        self.root = self._merge(a, c)

    # O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._newNode(v)), c)

    # O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    # (0 <= i <= size() - (r - l + 1); i = 0 moves it to the front, the max moves it to the end)
    def moveRange(self, l, r, i):
        a, b, c = self._cut(l, r)
        x, y = self._split(self._merge(a, c), i)
        self.root = self._merge(self._merge(x, b), y)

    # O(logN) expected -- a[i] += v
    def pointAdd(self, i, v):
        t, path = self._find(i)
        self.val[t] = self.val[t] + v

    # O(logN) expected -- a[i] = v
    def pointAssign(self, i, v):
        t, path = self._find(i)
        self.val[t] = v

    # O(logN) expected -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        t, path = self._find(i)
        self.val[t] = max(self.val[t], v)

    # O(logN) expected -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        t, path = self._find(i)
        self.val[t] = min(self.val[t], v)

    # O(logN) expected -- a[i]
    def pointGet(self, i):
        L, sz, t = self.L, self.sz, self.root
        while True:
            self._push(t)
            ls = sz[L[t]]
            if i < ls:
                t = L[t]
            elif i == ls:
                return self.val[t]
            else:
                i -= ls + 1
                t = self.R[t]

    # O(logN) expected -- append v to the end (it becomes a[size()])
    def pushBack(self, v):
        self.root = self._merge(self.root, self._newNode(v))

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

    # O(logN) expected -- cyclic shift a[l..r] right by k (a[r - k + 1..r] move to the front); any integer k,
    # negative shifts left
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
        self.rev.append(0)
        return x

    # recompute x from its children
    def _pull(self, x):
        l, r = self.L[x], self.R[x]
        self.sz[x] = self.sz[l] + self.sz[r] + 1

    def _applyRev(self, x):
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1

    # hand x's pending tags to its children
    def _push(self, x):
        if self.rev[x]:
            self._applyRev(self.L[x])
            self._applyRev(self.R[x])
            self.rev[x] = 0

    # (first k elements of t, the rest)
    def _split(self, t, k):
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

    # a's elements, then b's
    def _merge(self, a, b):
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

    # (a[0..l-1], a[l..r], a[r+1..]) as three trees; put them back with _join
    def _cut(self, l, r):
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    def _join(self, a, b, c):
        self.root = self._merge(self._merge(a, b), c)

    # (node holding a[i], the nodes above it), with every tag on the way pushed
    def _find(self, i):
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
