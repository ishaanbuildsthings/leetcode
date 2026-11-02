# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-min-max-hash-pre-suf-and/template.py
# @operations: append appendLeft concat cut getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX maxPrefixSum maxSuffixSum moveRange paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeHash rangeHashReversed rangeMax rangeMin rangeRotateLeft rangeRotateRight rangeSum rangesEqual rightmostGtX rightmostGteX rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX split trisect
# @data-structure-type: treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   concat: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   isPalindrome: log(N) expected
#   leftmostGtX: log(N) expected
#   leftmostGteX: log(N) expected
#   leftmostLtX: log(N) expected
#   leftmostLteX: log(N) expected
#   leftmostPrefixSumGtX: log(N) expected
#   leftmostPrefixSumGteX: log(N) expected
#   maxPrefixSum: log(N) expected
#   maxSuffixSum: log(N) expected
#   moveRange: log(N) expected
#   paste: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   rangeAndQuery: log(N) expected
#   rangeHash: log(N) expected
#   rangeHashReversed: log(N) expected
#   rangeMax: log(N) expected
#   rangeMin: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangeSum: log(N) expected
#   rangesEqual: log(N) expected
#   rightmostGtX: log(N) expected
#   rightmostGteX: log(N) expected
#   rightmostLtX: log(N) expected
#   rightmostLteX: log(N) expected
#   rightmostSuffixSumGtX: log(N) expected
#   rightmostSuffixSumGteX: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] pre[1*N] suf[1*N] an[1*N]
#   tags: none
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); a treap and the pieces cut from it share their nodes (freed with the last of them: no reset needed)

# Implicit treap with composable aggregates: an array you can insert into anywhere, rotate, move, cut pieces out of
# (that is how to erase) and paste them back in O(logN) expected each; each node keeps its sum, its min, its max, its
# forward / backward hash (and B^size), its best prefix sum, its best suffix sum, its AND over its subtree. All
# indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when
# nothing qualifies.
import random


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


class ImplicitTreap:
    __slots__ = ('root', 'val', 'pri', 'L', 'R', 'sz', 'sm', 'mn', 'mx', 'fh', 'bh', 'pw', 'pre', 'suf', 'an')

    # O(N) -- arr: the initial array (may be empty); like: an ImplicitTreap whose nodes this one shares, so pieces
    # can move between the two (pieces cut from a treap share its nodes already). No reset between test cases
    def __init__(self, arr=(), like=None):
        if like is None:
            self.val, self.pri, self.L, self.R, self.sz = [0], [0], [0], [0], [0]  # node 0 = the empty tree
            self.sm = [0]
            self.mn = [0]
            self.mx = [0]
            self.fh = [0]
            self.bh = [0]
            self.pw = [1]
            self.pre = [0]
            self.suf = [0]
            self.an = [-1]
        else:
            self.val, self.pri, self.L, self.R, self.sz = like.val, like.pri, like.L, like.R, like.sz
            self.sm = like.sm
            self.mn = like.mn
            self.mx = like.mx
            self.fh = like.fh
            self.bh = like.bh
            self.pw = like.pw
            self.pre = like.pre
            self.suf = like.suf
            self.an = like.an
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

    # O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums)
    def leftmostPrefixSumGtX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.pre
        t, i, acc, res = b, 0, 0, -1
        if t and P[t] > x:
            while True:
                lt = L[t]
                if lt and acc + P[lt] > x:
                    t = lt
                    continue
                acc += sm[lt]
                if acc + val[t] > x:
                    res = l + i + sz[lt]
                    break
                acc += val[t]
                i += sz[lt] + 1
                t = R[t]
        self._join(a, b, c)
        return res

    # O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (a walk pruned by best prefix sums)
    def leftmostPrefixSumGteX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.pre
        t, i, acc, res = b, 0, 0, -1
        if t and P[t] >= x:
            while True:
                lt = L[t]
                if lt and acc + P[lt] >= x:
                    t = lt
                    continue
                acc += sm[lt]
                if acc + val[t] >= x:
                    res = l + i + sz[lt]
                    break
                acc += val[t]
                i += sz[lt] + 1
                t = R[t]
        self._join(a, b, c)
        return res

    # O(logN) expected -- max of a[l] + ... + a[i] over i in [l, r]
    def maxPrefixSum(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.pre[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- max of a[i] + ... + a[r] over i in [l, r]
    def maxSuffixSum(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.suf[b]
        self._join(a, b, c)
        return res

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

    # O(logN) expected -- a[l] & ... & a[r]
    def rangeAndQuery(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.an[b]
        self._join(a, b, c)
        return res

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

    # O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums)
    def rightmostSuffixSumGtX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.suf
        t, i, acc, res = b, 0, 0, -1
        if t and P[t] > x:
            while True:
                rt = R[t]
                if rt and acc + P[rt] > x:
                    i += sz[L[t]] + 1
                    t = rt
                    continue
                acc += sm[rt]
                if acc + val[t] > x:
                    res = l + i + sz[L[t]]
                    break
                acc += val[t]
                t = L[t]
        self._join(a, b, c)
        return res

    # O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (a walk pruned by best suffix sums)
    def rightmostSuffixSumGteX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.suf
        t, i, acc, res = b, 0, 0, -1
        if t and P[t] >= x:
            while True:
                rt = R[t]
                if rt and acc + P[rt] >= x:
                    i += sz[L[t]] + 1
                    t = rt
                    continue
                acc += sm[rt]
                if acc + val[t] >= x:
                    res = l + i + sz[L[t]]
                    break
                acc += val[t]
                t = L[t]
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
        self.sm.append(v)
        self.mn.append(v)
        self.mx.append(v)
        self.fh.append((v + _HO) % _HP)
        self.bh.append((v + _HO) % _HP)
        self.pw.append(_HB)
        self.pre.append(v)
        self.suf.append(v)
        self.an.append(v)
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
        s, p, q = v, v, v  # the node alone, then with its left / right parts
        if l:
            ls, lp, lq = self.sm[l], self.pre[l], self.suf[l]
            s, p, q = ls + s, max(lp, ls + p), max(q, s + lq)
        if r:
            rs, rp, rq = self.sm[r], self.pre[r], self.suf[r]
            s, p, q = s + rs, max(p, s + rp), max(rq, rs + q)
        self.sm[x], self.pre[x], self.suf[x] = s, p, q
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
        B, P, pw, fh, bh = _HB, _HP, self.pw, self.fh, self.bh
        hv = (v + _HO) % P
        pw[x] = pw[l] * B % P * pw[r] % P
        fh[x] = ((fh[l] * B + hv) * pw[r] + fh[r]) % P
        bh[x] = ((bh[r] * B + hv) * pw[l] + bh[l]) % P
        self.an[x] = self.an[l] & v & self.an[r]  # (node 0: the AND of nothing, -1)

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

    def _cut(self, l, r):  # (a[0..l-1], a[l..r], a[r+1..])
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    def _join(self, a, b, c):
        self.root = self._merge(self._merge(a, b), c)

    def _find(self, i):  # (node holding a[i], the nodes above it), every tag on the way pushed
        L, sz, t, path = self.L, self.sz, self.root, []
        while True:
            ls = sz[L[t]]
            if i == ls:
                return t, path
            path.append(t)
            if i < ls:
                t = L[t]
            else:
                i -= ls + 1
                t = self.R[t]
