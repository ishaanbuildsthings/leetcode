# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-min-max-pre-suf-best-run-rev/template.py
# @operations: append appendLeft concat cut getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxPrefixSum maxSubarraySum maxSuffixSum moveRange paste pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX split trisect
# @data-structure-type: treap
# @letters: same
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   concat: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   leftmostGtX: log(N) expected
#   leftmostGteX: log(N) expected
#   leftmostLtX: log(N) expected
#   leftmostLteX: log(N) expected
#   leftmostPrefixSumGtX: log(N) expected
#   leftmostPrefixSumGteX: log(N) expected
#   longestEqualRun: log(N) expected
#   maxPrefixSum: log(N) expected
#   maxSubarraySum: log(N) expected
#   maxSuffixSum: log(N) expected
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
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] mx[1*N] pre[1*N] suf[1*N] best[1*N] fv[1*N] lv[1*N] pr[1*N] sr[1*N] br[1*N]
#   tags: rev[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); a treap and the pieces cut from it share their nodes (freed with the last of them: no reset needed)

# Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
# out of (that is how to erase) and paste them back in O(logN) expected each; each node keeps its sum, its min, its
# max, its best prefix sum, its best suffix sum, its best subarray sum, its first / last value and the equal runs at
# its ends and inside over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in
# the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet
# to its children".
import random


class ImplicitTreap:
    __slots__ = ('root', 'val', 'pri', 'L', 'R', 'sz', 'sm', 'mn', 'mx', 'pre', 'suf', 'best', 'fv', 'lv', 'pr', 'sr',
                 'br', 'rev')

    # O(N) -- arr: the initial array (may be empty); like: an ImplicitTreap whose nodes this one shares, so pieces
    # can move between the two (pieces cut from a treap share its nodes already). No reset between test cases
    def __init__(self, arr=(), like=None):
        if like is None:
            self.val, self.pri, self.L, self.R, self.sz = [0], [0], [0], [0], [0]  # node 0 = the empty tree
            self.sm = [0]
            self.mn = [0]
            self.mx = [0]
            self.pre = [0]
            self.suf = [0]
            self.best = [0]
            self.fv = [0]
            self.lv = [0]
            self.pr = [0]
            self.sr = [0]
            self.br = [0]
            self.rev = [0]
        else:
            self.val, self.pri, self.L, self.R, self.sz = like.val, like.pri, like.L, like.R, like.sz
            self.sm = like.sm
            self.mn = like.mn
            self.mx = like.mx
            self.pre = like.pre
            self.suf = like.suf
            self.best = like.best
            self.fv = like.fv
            self.lv = like.lv
            self.pr = like.pr
            self.sr = like.sr
            self.br = like.br
            self.rev = like.rev
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

    # O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums)
    def leftmostPrefixSumGtX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.pre
        t, i, acc, res = b, 0, 0, -1
        if t and P[t] > x:
            while True:
                self._push(t)
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
                self._push(t)
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

    # O(logN) expected -- the longest run of equal adjacent values in a[l..r]
    def longestEqualRun(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.br[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- max of a[l] + ... + a[i] over i in [l, r]
    def maxPrefixSum(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.pre[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- max sum of a non-empty contiguous subarray of a[l..r]
    def maxSubarraySum(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.best[b]
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

    # O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums)
    def rightmostSuffixSumGtX(self, l, r, x):
        a, b, c = self._cut(l, r)
        L, R, val, sz, sm, P = self.L, self.R, self.val, self.sz, self.sm, self.suf
        t, i, acc, res = b, 0, 0, -1
        if t and P[t] > x:
            while True:
                self._push(t)
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
                self._push(t)
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
        self.pre.append(v)
        self.suf.append(v)
        self.best.append(v)
        self.fv.append(v)
        self.lv.append(v)
        self.pr.append(1)
        self.sr.append(1)
        self.br.append(1)
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
        s, p, q, b = v, v, v, v  # the node alone, then with its left / right parts
        if l:
            ls, lp, lq, lb = self.sm[l], self.pre[l], self.suf[l], self.best[l]
            s, p, q, b = ls + s, max(lp, ls + p), max(q, s + lq), max(lb, b, lq + p)
        if r:
            rs, rp, rq, rb = self.sm[r], self.pre[r], self.suf[r], self.best[r]
            s, p, q, b = s + rs, max(p, s + rp), max(rq, rs + q), max(b, rb, q + rp)
        self.sm[x], self.pre[x], self.suf[x], self.best[x] = s, p, q, b
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

    def _applyRev(self, x):  # reverse x's subtree
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
            self.pre[x], self.suf[x] = self.suf[x], self.pre[x]
            self.fv[x], self.lv[x] = self.lv[x], self.fv[x]
            self.pr[x], self.sr[x] = self.sr[x], self.pr[x]

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
