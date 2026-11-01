# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-hash-assign-rev-pointers/template.py
# @operations: append appendLeft concat cut eraseRange getAll insertAt insertCopiesAt isPalindrome moveRange paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAssign rangeHash rangeHashReversed rangeReverse rangeRotateLeft rangeRotateRight rangesEqual split trisect
# @data-structure-type: treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   concat: log(N) expected
#   cut: log(N) expected
#   eraseRange: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   isPalindrome: log(N) expected
#   moveRange: log(N) expected
#   paste: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   pop: log(N) expected
#   popLeft: log(N) expected
#   rangeAssign: log(N) expected
#   rangeHash: log(N) expected
#   rangeHashReversed: log(N) expected
#   rangeReverse: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangesEqual: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] fh[1*N] bh[1*N] pw[1*N] gs[1*N]
#   tags: rev[1*N] asg[1*N] hasAsg[1*N]
#   other: alloc[2*N]
#   note: N = the values in this treap; every node is allocated on its own (alloc: the allocator's per-node overhead), so cut / paste move nodes between treaps in O(log N) and erased nodes are freed; node objects

# Implicit treap: an array you can insert into / erase from anywhere, reverse, rotate, move ranges, and cut out into a
# treap of its own / paste a treap into, each in O(logN) expected, plus point ops, rangeAssign, range hashes /
# isPalindrome / rangesEqual (polynomial hashes mod 2^61 - 1 both ways, the base random per run; a reverse swaps
# them). All indices 0-based, ranges inclusive [l, r], and an index always means the position in the CURRENT array.
# Nodes keep their values in array order (an in-order walk); a node's position is the size of everything left of it.
# Lazy tags mean "already applied to this node, not yet to its children".
import random


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


class _Node:
    __slots__ = ('val', 'pri', 'l', 'r', 'sz', 'rev', 'fh', 'bh', 'pw', 'gs', 'asg', 'hasAsg')

    def __init__(self, v):
        self.val = v
        self.pri = random.getrandbits(62)
        self.l = self.r = None
        self.sz = 1
        self.rev = False
        self.fh = self.bh = (v + _HO) % _HP
        self.pw, self.gs = _HB, 1
        self.asg = 0
        self.hasAsg = False


def _pull(x):  # recompute x from its children
    l, r = x.l, x.r
    x.sz = 1 + (l.sz if l else 0) + (r.sz if r else 0)
    B, P = _HB, _HP
    lp, lg, lf, lb = (l.pw, l.gs, l.fh, l.bh) if l else (1, 0, 0, 0)
    rp, rg, rf, rb = (r.pw, r.gs, r.fh, r.bh) if r else (1, 0, 0, 0)
    hv = (x.val + _HO) % P
    x.pw = lp * B % P * rp % P
    x.gs = ((lg * B + 1) * rp + rg) % P
    x.fh = ((lf * B + hv) * rp + rf) % P
    x.bh = ((rb * B + hv) * lp + lb) % P


def _applyRev(x):
    if x:
        x.l, x.r = x.r, x.l
        x.rev = not x.rev
        x.fh, x.bh = x.bh, x.fh  # reversed: the hashes trade places


def _applyAssign(x, v):
    if not x:
        return
    x.val = v
    x.fh = x.bh = (v + _HO) % _HP * x.gs % _HP
    x.hasAsg = True
    x.asg = v


def _push(x):  # hand x's pending tags to its children
    if x.rev:
        _applyRev(x.l)
        _applyRev(x.r)
        x.rev = False
    if x.hasAsg:
        _applyAssign(x.l, x.asg)
        _applyAssign(x.r, x.asg)
        x.hasAsg = False


def _split(t, k):  # (first k elements of t, the rest)
    if not t:
        return None, None
    _push(t)
    ls = t.l.sz if t.l else 0
    if ls >= k:
        a, t.l = _split(t.l, k)
        _pull(t)
        return a, t
    t.r, b = _split(t.r, k - ls - 1)
    _pull(t)
    return t, b


def _merge(a, b):  # a's elements, then b's
    if not a or not b:
        return a or b
    if a.pri > b.pri:
        _push(a)
        a.r = _merge(a.r, b)
        _pull(a)
        return a
    _push(b)
    b.l = _merge(a, b.l)
    _pull(b)
    return b


class ImplicitTreap:
    __slots__ = ("root",)

    # O(N) -- arr: the initial array (may be empty)
    def __init__(self, arr=()):
        stack = []  # Cartesian tree on (position, priority) in one pass: the stack is the current right spine
        for v in arr:
            x, last = _Node(v), None
            while stack and stack[-1].pri < x.pri:
                last = stack.pop()
            x.l = last
            if stack:
                stack[-1].r = x
            stack.append(x)
        self.root = stack[0] if stack else None
        order, todo = [], ([self.root] if self.root else [])
        while todo:  # pre-order; pulled in reverse, so children before parents
            x = todo.pop()
            order.append(x)
            if x.l:
                todo.append(x.l)
            if x.r:
                todo.append(x.r)
        for x in reversed(order):
            _pull(x)

    # O(1) -- the current length of the array
    def size(self):
        return self.root.sz if self.root else 0

    # O(logN) expected -- append v to the end (it becomes a[size()])
    def append(self, v):
        self.root = _merge(self.root, _Node(v))

    # O(logN) expected -- append all of other at the end; other is left empty
    def concat(self, other):
        self.root = _merge(self.root, other.root)
        other.root = None

    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0 again); everything after
    # it shifts left by r - l + 1
    def cut(self, l, r):
        a, b, c = self._cut(l, r)
        self.root = _merge(a, c)
        piece = ImplicitTreap()
        piece.root = b
        return piece

    # O(logN) expected -- remove a[l..r]; everything after it shifts left by r - l + 1
    def eraseRange(self, l, r):
        a, _, c = self._cut(l, r)
        self.root = _merge(a, c)

    # O(N) -- the whole current array a[0..size()-1], every pending tag applied on the way
    def getAll(self):
        out, stack, t = [], [], self.root
        while stack or t:
            while t:
                _push(t)
                stack.append(t)
                t = t.l
            t = stack.pop()
            out.append(t.val)
            t = t.r
        return out

    # O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        a, c = _split(self.root, i)
        self.root = _merge(_merge(a, _Node(v)), c)

    # O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0): they are built as
    # one treap in O(k), then spliced in
    def insertCopiesAt(self, i, v, k):
        if k <= 0:
            return
        a, c = _split(self.root, i)
        self.root = _merge(_merge(a, _build([v] * k)), c)

    # O(logN) expected -- is a[l..r] a palindrome (its two hashes agree)
    def isPalindrome(self, l, r):
        a, b, c = self._cut(l, r)
        res = b.fh == b.bh
        self.root = _merge(_merge(a, b), c)
        return res

    # O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    # (0 <= i <= size() - (r - l + 1); i = 0 moves it to the front, the max moves it to the end)
    def moveRange(self, l, r, i):
        a, b, c = self._cut(l, r)
        x, y = _split(_merge(a, c), i)
        self.root = _merge(_merge(x, b), y)

    # O(logN) expected -- insert all of other so it starts at a[i] (0 <= i <= size(); i = size() appends); other is
    # left empty
    def paste(self, i, other):
        a, c = _split(self.root, i)
        self.root = _merge(_merge(a, other.root), c)
        other.root = None

    # O(logN) expected -- a[i] += v
    def pointAdd(self, i, v):
        t, path = self._find(i)
        t.val = t.val + v
        _pull(t)
        for x in reversed(path):
            _pull(x)

    # O(logN) expected -- a[i] = v
    def pointAssign(self, i, v):
        t, path = self._find(i)
        t.val = v
        _pull(t)
        for x in reversed(path):
            _pull(x)

    # O(logN) expected -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        t, path = self._find(i)
        t.val = max(t.val, v)
        _pull(t)
        for x in reversed(path):
            _pull(x)

    # O(logN) expected -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        t, path = self._find(i)
        t.val = min(t.val, v)
        _pull(t)
        for x in reversed(path):
            _pull(x)

    # O(logN) expected -- a[i]
    def pointGet(self, i):
        return self._find(i)[0].val

    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

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
        _applyAssign(b, v)
        self.root = _merge(_merge(a, b), c)

    # O(logN) expected -- hash of a[l..r] read left to right (a[l] B^(len-1) + ... + a[r], mod 2^61 - 1; B random per run): equal ranges hash equal
    def rangeHash(self, l, r):
        a, b, c = self._cut(l, r)
        res = b.fh
        self.root = _merge(_merge(a, b), c)
        return res

    # O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    def rangeHashReversed(self, l, r):
        a, b, c = self._cut(l, r)
        res = b.bh
        self.root = _merge(_merge(a, b), c)
        return res

    # O(logN) expected -- reverse a[l..r] in place
    def rangeReverse(self, l, r):
        a, b, c = self._cut(l, r)
        _applyRev(b)
        self.root = _merge(_merge(a, b), c)

    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
    def rangeRotateLeft(self, l, r, k):
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = _split(b, k)
            b = _merge(b2, b1)
        self.root = _merge(_merge(a, b), c)

    # O(logN) expected -- cyclic shift a[l..r] right by k (a[r - k + 1..r] move to the front); any integer k,
    # negative shifts left
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)

    # O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own (0 <= k <= size()); this one is left empty
    def split(self, k):
        left, right = ImplicitTreap(), ImplicitTreap()
        left.root, right.root = _split(self.root, k)
        self.root = None
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = ImplicitTreap(), ImplicitTreap(), ImplicitTreap()
        left.root, mid.root, right.root = self._cut(l, r)
        self.root = None
        return left, mid, right

    # ---- internals ----

    # (a[0..l-1], a[l..r], a[r+1..]) as three trees
    def _cut(self, l, r):
        a, b = _split(self.root, l)
        b, c = _split(b, r - l + 1)
        return a, b, c

    # (node holding a[i], the nodes above it), with every tag on the way pushed
    def _find(self, i):
        t, path = self.root, []
        while True:
            _push(t)
            ls = t.l.sz if t.l else 0
            if i == ls:
                return t, path
            path.append(t)
            if i < ls:
                t = t.l
            else:
                i -= ls + 1
                t = t.r


def _build(vals):  # a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    stack = []
    for v in vals:
        x, last = _Node(v), None
        while stack and stack[-1].pri < x.pri:
            last = stack.pop()
        x.l = last
        if stack:
            stack[-1].r = x
        stack.append(x)
    root = stack[0] if stack else None
    order, todo = [], ([root] if root else [])
    while todo:  # pre-order; pulled in reverse, so children before parents
        x = todo.pop()
        order.append(x)
        if x.l:
            todo.append(x.l)
        if x.r:
            todo.append(x.r)
    for x in reversed(order):
        _pull(x)
    return root
