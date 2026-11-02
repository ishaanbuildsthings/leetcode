# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-max-hash-alt-rev/template.py
# @operations: append appendLeft eraseRange getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX maxAltSubseqSum moveRange pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeHash rangeHashReversed rangeMax rangeReverse rangeRotateLeft rangeRotateRight rangesEqual rightmostGtX rightmostGteX
# @data-structure-type: treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   eraseRange: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   isPalindrome: log(N) expected
#   leftmostGtX: log(N) expected
#   leftmostGteX: log(N) expected
#   maxAltSubseqSum: log(N) expected
#   moveRange: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   pop: log(N) expected
#   popLeft: log(N) expected
#   rangeHash: log(N) expected
#   rangeHashReversed: log(N) expected
#   rangeMax: log(N) expected
#   rangeReverse: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangesEqual: log(N) expected
#   rightmostGtX: log(N) expected
#   rightmostGteX: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] a00[1*N] a01[1*N] a10[1*N] a11[1*N]
#   tags: rev[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused)

# Implicit treap with composable aggregates: an array you can insert into / erase from anywhere, reverse, rotate, move
# in O(logN) expected each; each node keeps its max, its forward / backward hash (and B^size), its best alternating (+
# - + ...) subsequence sum for each start / end sign over its subtree. All indices 0-based, ranges inclusive [l, r],
# an index always the position in the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean
# "already applied to this node, not yet to its children".
import random


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


INF, NEG = float("inf"), float("-inf")


def _altJoin(A, B):  # A's part, then B's: (++, +-, -+, --) = best by (start sign, end sign)
    a0, a1, a2, a3 = A
    b0, b1, b2, b3 = B
    return (max(a0, b0, a0 + b2, a1 + b0), max(a1, b1, a0 + b3, a1 + b1),
            max(a2, b2, a2 + b2, a3 + b0), max(a3, b3, a2 + b3, a3 + b1))


class ImplicitTreap:
    __slots__ = ('root', 'val', 'pri', 'L', 'R', 'sz', 'mx', 'fh', 'bh', 'pw', 'a00', 'a01', 'a10', 'a11', 'rev')

    # O(N) -- arr: the initial array (may be empty)
    def __init__(self, arr):
        self.val, self.pri, self.L, self.R, self.sz = [0], [0], [0], [0], [0]  # node 0 = the empty tree
        self.mx = [0]
        self.fh = [0]
        self.bh = [0]
        self.pw = [1]
        self.a00 = [0]
        self.a01 = [0]
        self.a10 = [0]
        self.a11 = [0]
        self.rev = [0]
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

    # O(logN) expected -- is a[l..r] a palindrome (its two hashes agree)
    def isPalindrome(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.fh[b] == self.bh[b]
        self._join(a, b, c)
        return res

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

    # O(logN) expected -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]
    def maxAltSubseqSum(self, l, r):
        a, b, c = self._cut(l, r)
        res = max(self.a00[b], self.a01[b])
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

    # O(logN) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    def rangeHash(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.fh[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    def rangeHashReversed(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.bh[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- max of a[l..r]
    def rangeMax(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.mx[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- reverse a[l..r] in place
    def rangeReverse(self, l, r):
        a, b, c = self._cut(l, r)
        self._applyRev(b)
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

    # O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

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

    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        self.mx.append(v)
        self.fh.append((v + _HO) % _HP)
        self.bh.append((v + _HO) % _HP)
        self.pw.append(_HB)
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
        m = v
        if l and self.mx[l] > m:
            m = self.mx[l]
        if r and self.mx[r] > m:
            m = self.mx[r]
        self.mx[x] = m
        B, P, pw, fh, bh = _HB, _HP, self.pw, self.fh, self.bh
        hv = (v + _HO) % P
        pw[x] = pw[l] * B % P * pw[r] % P
        fh[x] = ((fh[l] * B + hv) * pw[r] + fh[r]) % P
        bh[x] = ((bh[r] * B + hv) * pw[l] + bh[l]) % P
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
            self.fh[x], self.bh[x] = self.bh[x], self.fh[x]
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
