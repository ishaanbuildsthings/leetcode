# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-treap-sum-min-hash-pre-suf-xor/template.py
# @operations: append appendLeft copy cut getAll insertAt insertCopiesAt isPalindrome leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX maxPrefixSum maxSuffixSum merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeHash rangeHashReversed rangeMin rangeRotateLeft rangeRotateRight rangeSum rangeXorQuery rangesEqual rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX split trisect
# @data-structure-type: persistent-treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   copy: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   isPalindrome: log(N) expected
#   leftmostLtX: log(N) expected
#   leftmostLteX: log(N) expected
#   leftmostPrefixSumGtX: log(N) expected
#   leftmostPrefixSumGteX: log(N) expected
#   maxPrefixSum: log(N) expected
#   maxSuffixSum: log(N) expected
#   merge: log(N) expected
#   paste: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   rangeHash: log(N) expected
#   rangeHashReversed: log(N) expected
#   rangeMin: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangeSum: log(N) expected
#   rangeXorQuery: log(N) expected
#   rangesEqual: log(N) expected
#   rightmostLtX: log(N) expected
#   rightmostLteX: log(N) expected
#   rightmostSuffixSumGtX: log(N) expected
#   rightmostSuffixSumGteX: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] sm[1*N*log(N)] mn[1*N*log(N)] fh[1*N*log(N)] bh[1*N*log(N)] pw[1*N*log(N)] pre[1*N*log(N)] suf[1*N*log(N)] xr[1*N*log(N)]
#   tags: none
#   other: none
#   note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies share every node they don't change; log(N) is of the length, which can be huge (long long)

# Persistent implicit treap with composable aggregates: an array you can insert into anywhere, rotate, cut pieces out
# of (that is how to erase), paste them back and copy (copy(l, r): a[l..r] as a treap of its own in O(logN) however
# long, since the copy shares the same nodes; this one is unchanged); each node keeps its sum, its min, its forward /
# backward hash (and B^size), its best prefix sum, its best suffix sum, its xor over its subtree. No node changes once
# another tree can see it: an op copies the nodes on its paths, so a copy and its original never affect each other.
# Lengths and indices are long long. All indices 0-based, ranges inclusive [l, r], an index always the position in the
# CURRENT array; searches return -1 when nothing qualifies.
import random


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


class PersistentTreap:
    # one node pool shared by every PersistentTreap: cut / paste move nodes between them, so a piece from one can go
    # into any other (node 0 = the empty tree). Nodes are never freed (memory = O(log N) per op, over the whole run),
    # so there is nothing to reset between test cases
    val = [0]
    L = [0]
    R = [0]
    sz = [0]
    sm = [0]
    mn = [0]
    fh = [0]
    bh = [0]
    pw = [1]
    pre = [0]
    suf = [0]
    xr = [0]
    __slots__ = ("root",)

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr))

    def _empty(self):  # a new, empty PersistentTreap (on the same pool, like every one)
        return PersistentTreap()

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN) expected -- append v to the end
    def append(self, v):
        self.root = self._merge(self.root, self._newNode(v))

    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- a[l..r] (leave out l and r: the whole array, O(1)) as a PersistentTreap of its own; this one
    # is unchanged. The copy shares this one's nodes, so it costs O(logN) however long it is
    def copy(self, l=0, r=None):
        if r is None:
            r = self.size() - 1
        piece = self._empty()
        piece.root = self.root if l == 0 and r == self.size() - 1 else self._cut(l, r)[1]
        return piece

    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
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
        return res

    # O(logN) expected -- max of a[l] + ... + a[i] over i in [l, r]
    def maxPrefixSum(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.pre[b]
        return res

    # O(logN) expected -- max of a[i] + ... + a[r] over i in [l, r]
    def maxSuffixSum(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.suf[b]
        return res

    # O(logN) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(logN) expected -- insert all of other (any PersistentTreap, e.g. a cut piece) so it starts at a[i]
    # (0 <= i <= size()); other is left empty
    def paste(self, i, other):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), c)
        other.root = 0

    # O(logN) expected -- a[i] += v
    def pointAdd(self, i, v):
        a, b, c = self._cut(i, i)  # (b: a fresh copy of a[i]'s node, alone)
        self.val[b] = self.val[b] + v
        self._pull(b)
        self._join(a, b, c)

    # O(logN) expected -- a[i] = v
    def pointAssign(self, i, v):
        a, b, c = self._cut(i, i)  # (b: a fresh copy of a[i]'s node, alone)
        self.val[b] = v
        self._pull(b)
        self._join(a, b, c)

    # O(logN) expected -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        a, b, c = self._cut(i, i)  # (b: a fresh copy of a[i]'s node, alone)
        self.val[b] = max(self.val[b], v)
        self._pull(b)
        self._join(a, b, c)

    # O(logN) expected -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        a, b, c = self._cut(i, i)  # (b: a fresh copy of a[i]'s node, alone)
        self.val[b] = min(self.val[b], v)
        self._pull(b)
        self._join(a, b, c)

    # O(logN) expected -- a[i]
    def pointGet(self, i):
        return self.val[self._find(i)[0]]

    # O(logN) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    def rangeHash(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.fh[b]
        return res

    # O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    def rangeHashReversed(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.bh[b]
        return res

    # O(logN) expected -- min of a[l..r]
    def rangeMin(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.mn[b]
        return res

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
        return res

    # O(logN) expected -- a[l] ^ ... ^ a[r]
    def rangeXorQuery(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.xr[b]
        return res

    # O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

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
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        self.sm.append(v)
        self.mn.append(v)
        self.fh.append((v + _HO) % _HP)
        self.bh.append((v + _HO) % _HP)
        self.pw.append(_HB)
        self.pre.append(v)
        self.suf.append(v)
        self.xr.append(v)
        return x

    # a balanced tree of new nodes holding vals in order, O(len)
    def _build(self, vals, lo=0, hi=None):
        if hi is None:
            hi = len(vals)
        if lo >= hi:
            return 0
        mid = (lo + hi) // 2
        x = self._newNode(vals[mid])
        self.L[x] = self._build(vals, lo, mid)
        self.R[x] = self._build(vals, mid + 1, hi)
        self._pull(x)
        return x

    def _clone(self, x):  # a new copy of node x (sharing its children)
        y = len(self.val)
        for arr in (self.val, self.L, self.R, self.sz, self.sm, self.mn, self.fh, self.bh, self.pw, self.pre, self.suf, self.xr):
            arr.append(arr[x])
        return y

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
        B, P, pw, fh, bh = _HB, _HP, self.pw, self.fh, self.bh
        hv = (v + _HO) % P
        pw[x] = pw[l] * B % P * pw[r] % P
        fh[x] = ((fh[l] * B + hv) * pw[r] + fh[r]) % P
        bh[x] = ((bh[r] * B + hv) * pw[l] + bh[l]) % P
        self.xr[x] = self.xr[l] ^ v ^ self.xr[r]

    def _split(self, t, k):  # (first k of t, the rest), as new nodes (t's are left as they were)
        if not t:
            return 0, 0
        t = self._clone(t)
        L, R = self.L, self.R
        if self.sz[L[t]] >= k:
            a, L[t] = self._split(L[t], k)
            self._pull(t)
            return a, t
        R[t], b = self._split(R[t], k - self.sz[L[t]] - 1)
        self._pull(t)
        return t, b

    def _merge(self, a, b):  # a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
        if not a or not b:
            return a or b
        if random.randrange(self.sz[a] + self.sz[b]) < self.sz[a]:
            a = self._clone(a)
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        b = self._clone(b)
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


# Example (pieces move between treaps; merge appends and leaves its argument empty):
#     t = PersistentTreap([1, 2, 3, 4, 5])
#     left, mid, right = t.trisect(1, 3)  # left = [1], mid = [2, 3, 4], right = [5]; t is empty now
#     t.merge(right)                      # t = [5]
#     t.merge(mid)                        # t = [5, 2, 3, 4]
#     t.merge(left)                       # t = [5, 2, 3, 4, 1]
