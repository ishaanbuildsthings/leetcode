# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sorted-runs-min-or-hash-seq/template.py
# @operations: append appendLeft eraseRange getAll insertAt insertCopiesAt isPalindrome moveRange pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAssign rangeHash rangeHashReversed rangeMin rangeOrQuery rangeReverse rangeRotateLeft rangeRotateRight rangeSortAsc rangeSortDesc rangesEqual
# @data-structure-type: sorted-runs
# @complexities:
#   append: log(N)+log(U) amortized
#   appendLeft: log(N)+log(U) amortized
#   eraseRange: log(N)+log(U) amortized
#   getAll: N*log(U)
#   insertAt: log(N)+log(U) amortized
#   insertCopiesAt: log(N)+log(U) amortized
#   isPalindrome: log(N)+log(U) amortized
#   moveRange: log(N)+log(U) amortized
#   pointAdd: log(N)+log(U) amortized
#   pointAssign: log(N)+log(U) amortized
#   pointChmax: log(N)+log(U) amortized
#   pointChmin: log(N)+log(U) amortized
#   pointGet: log(N)+log(U) expected
#   pop: log(N)+log(U) amortized
#   popLeft: log(N)+log(U) amortized
#   rangeAssign: log(N)+log(U) amortized
#   rangeHash: log(N)+log(U) amortized
#   rangeHashReversed: log(N)+log(U) amortized
#   rangeMin: log(N)+log(U) amortized
#   rangeOrQuery: log(N)+log(U) amortized
#   rangeReverse: log(N)+log(U) amortized
#   rangeRotateLeft: log(N)+log(U) amortized
#   rangeRotateRight: log(N)+log(U) amortized
#   rangeSortAsc: log(N)+log(U) amortized
#   rangeSortDesc: log(N)+log(U) amortized
#   rangesEqual: log(N)+log(U) amortized
#   build: N*log(U)
# @memory:
#   layout: none
#   node: Lc[1*N*log(U)] Rc[1*N*log(U)] cnt[1*N*log(U)] ov[1*N*log(U)] fh[1*N*log(U)] bh[1*N*log(U)]
#   tags: none
#   other: TL[1*N] TR[1*N] TP[1*N] TV[1*N] TN[1*N] TD[1*N] TS[1*N] TF[1*N] Omn[1*N] Smn[1*N] Sov[1*N] Sfh[1*N] Sbh[1*N] pw[1*N] gs[1*N]
#   note: value nodes: N log U to start, plus O(log U) per cut (merges free nodes, which are reused); the runs are the nodes of an implicit treap (expected depth log N); U = valHi - valLo + 1

# An array whose ranges you can sort in place (ascending or descending), amortized O(log N + log U) a sort, with point
# reads / writes, rangeAssign, range mins, range ors, range hashes both ways (isPalindrome, rangesEqual), insert /
# erase / reverse / rotate / move anywhere and the whole array. It is kept as a sequence of sorted runs: each run is a
# dynamic value seg tree over [valLo, valHi] (copies per node) and an up / down flag, and the runs, in order, are the
# nodes of an implicit treap (random priorities, expected depth log N), each also keeping its subtree's length and min
# / or / hashes; a reverse flips the order of the runs and each run's up / down flag. Sorting [l, r] cuts the runs at
# l and r + 1 and merges every run inside into one; a[i] is the k-th value of the run holding it; a query cuts at l
# and r + 1 too, then reads whole runs. Merges cost about as many nodes as they free and every run is merged away at
# most once, hence the amortized bounds (the treap's are expected as well). Indices 0-based, ranges inclusive, every
# index is a position in the current array. Hashes are polynomial, mod the prime 2^61 - 1, with a base and a value
# offset random per run: hash(x1..xk) = x1 B^(k-1) + ... + xk; a value tree keeps the hash of its values in sorted
# order both ways.

import random
INF = float("inf")
_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


class SortedRunsMinOrHashSeq:
    # O(N log U) -- arr: the initial array (may be empty); every value a[i] ever holds must lie in [valLo, valHi]
    # (U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        n = self.n = len(arr)
        self.vlo, self.vhi = valLo, valHi
        self.Lc, self.Rc, self.cnt = [0], [0], [0]  # value node 0 = the empty tree
        self.ov = [0]
        self.fh = [0]
        self.bh = [0]
        self.free = []  # value nodes freed by merges, reused first
        self.pw, self.gs = [1], [0]
        self._grow(n)
        # treap of runs (node 0 = empty): children TL / TR, priority TP, value tree TV, length TN, descending TD,
        # subtree length TS, pending reverse TF, subtree min / or / hashes (O: the run's own min / max)
        self.TL = [0]
        self.TR = [0]
        self.TP = [0]
        self.TV = [0]
        self.TN = [0]
        self.TD = [False]
        self.TS = [0]
        self.TF = [False]
        self.Omn = [INF]
        self.Smn = [INF]
        self.Sov = [0]
        self.Sfh = [0]
        self.Sbh = [0]
        self.tfree = []
        stack = []  # O(N) build: the treap's right spine
        for v in arr:
            x, last = self._run(self._leaf(v), 1, False), 0
            while stack and self.TP[stack[-1]] < self.TP[x]:
                last = stack.pop()
                self._tpull(last)
            self.TL[x] = last
            if stack:
                self.TR[stack[-1]] = x
            stack.append(x)
        for x in reversed(stack):
            self._tpull(x)
        self.top = stack[0] if stack else 0

    # O(1) -- the current length
    def size(self):
        return self.n

    # O(log N + log U) expected -- a[i]
    def pointGet(self, i):
        x = self.top
        while True:
            self._push(x)
            ls = self.TS[self.TL[x]]
            if i < ls:
                x = self.TL[x]
            elif i < ls + self.TN[x]:
                k = i - ls
                return self._kth(self.TV[x], self.TN[x] - k if self.TD[x] else k + 1)
            else:
                i -= ls + self.TN[x]
                x = self.TR[x]

    # O(log N + log U) amortized -- a[i] = v
    def pointAssign(self, i, v):
        self.rangeAssign(i, i, v)

    # O(log N + log U) amortized -- a[i] += v
    def pointAdd(self, i, v):
        self.pointAssign(i, self.pointGet(i) + v)

    # O(log N + log U) amortized -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        if v > self.pointGet(i):
            self.pointAssign(i, v)

    # O(log N + log U) amortized -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        if v < self.pointGet(i):
            self.pointAssign(i, v)

    # O(log N + log U) amortized -- sort a[l..r] ascending
    def rangeSortAsc(self, l, r):
        self._sort(l, r, False)

    # O(log N + log U) amortized -- sort a[l..r] descending
    def rangeSortDesc(self, l, r):
        self._sort(l, r, True)

    # O(log N + log U) amortized -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        A, B, C = self._extract(l, r)
        self._drop(B)
        self._join(A, self._run(self._leaf(v, r - l + 1), r - l + 1, False), C)

    # O(log N + log U) amortized -- reverse a[l..r]
    def rangeReverse(self, l, r):
        A, B, C = self._extract(l, r)
        self._rev(B)
        self._join(A, B, C)

    # O(log N + log U) amortized -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        self.insertCopiesAt(i, v, 1)

    # O(log N + log U) amortized -- insert k copies of v starting at index i (0 <= i <= size(); k <= 0 does nothing)
    def insertCopiesAt(self, i, v, k):
        if k <= 0:
            return
        self.n += k
        self._grow(self.n)
        A, C = self._tsplit(self.top, i)
        self.top = self._tmerge(self._tmerge(A, self._run(self._leaf(v, k), k, False)), C)

    # O(log N + log U) amortized -- append v
    def append(self, v):
        self.insertCopiesAt(self.n, v, 1)

    # O(log N + log U) amortized -- insert v at the front (it becomes a[0])
    def appendLeft(self, v):
        self.insertCopiesAt(0, v, 1)

    # O(log N + log U) amortized -- remove a[i] and return it
    def pop(self, i):
        v = self.pointGet(i)
        self.eraseRange(i, i)
        return v

    # O(log N + log U) amortized -- remove a[0] and return it
    def popLeft(self):
        return self.pop(0)

    # O(log N + log U) amortized -- remove a[l..r]
    def eraseRange(self, l, r):
        A, B, C = self._extract(l, r)
        self._drop(B)
        self.n -= r - l + 1
        self.top = self._tmerge(A, C)

    # O(log N + log U) amortized -- rotate a[l..r] left by k (a[l + k] comes first; any k, negative = right)
    def rangeRotateLeft(self, l, r, k):
        k %= r - l + 1
        if k:
            A, B, C = self._extract(l, r)
            X, Y = self._tsplit(B, k)
            self._join(A, self._tmerge(Y, X), C)

    # O(log N + log U) amortized -- rotate a[l..r] right by k (any k, negative = left)
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)

    # O(log N + log U) amortized -- cut a[l..r] out and paste it so it starts at index i of what is left
    # (0 <= i <= size() - (r - l + 1))
    def moveRange(self, l, r, i):
        A, B, C = self._extract(l, r)
        X, Y = self._tsplit(self._tmerge(A, C), i)
        self.top = self._tmerge(self._tmerge(X, B), Y)

    # O(log N + log U) amortized -- min of a[l..r]
    def rangeMin(self, l, r):
        A, B, C = self._extract(l, r)
        res = self.Smn[B]
        self._join(A, B, C)
        return res

    # O(log N + log U) amortized -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r):
        A, B, C = self._extract(l, r)
        res = self.Sov[B]
        self._join(A, B, C)
        return res

    # O(log N + log U) amortized -- is a[l..r] a palindrome?
    def isPalindrome(self, l, r):
        A, B, C = self._extract(l, r)
        res = self.Sfh[B] == self.Sbh[B]
        self._join(A, B, C)
        return res

    # O(log N + log U) amortized -- hash of a[l..r] read left to right (a[l] B^(len-1) + ... + a[r], mod 2^61 - 1; B random per run): equal ranges hash equal
    def rangeHash(self, l, r):
        A, B, C = self._extract(l, r)
        res = self.Sfh[B]
        self._join(A, B, C)
        return res

    # O(log N + log U) amortized -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    def rangeHashReversed(self, l, r):
        A, B, C = self._extract(l, r)
        res = self.Sbh[B]
        self._join(A, B, C)
        return res

    # O(log N + log U) amortized -- a[l1..r1] == a[l2..r2]? (equal lengths and equal hashes)
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(N log U) -- the whole current array
    def getAll(self):
        out, stack, x = [], [], self.top
        while stack or x:
            while x:
                self._push(x)
                stack.append(x)
                x = self.TL[x]
            x = stack.pop()
            out += self._values(self.TV[x], self.TD[x])
            x = self.TR[x]
        return out

    # ---- internals: the treap of runs ----

    # a new run node: value tree t, length ln, descending?
    def _run(self, t, ln, desc):
        if self.tfree:
            x = self.tfree.pop()
            self.TL[x] = self.TR[x] = 0
            self.TF[x] = False
        else:
            x = len(self.TS)
            self.TL.append(0)
            self.TR.append(0)
            self.TP.append(0)
            self.TV.append(0)
            self.TN.append(0)
            self.TD.append(False)
            self.TS.append(0)
            self.TF.append(False)
            self.Omn.append(INF)
            self.Smn.append(INF)
            self.Sov.append(0)
            self.Sfh.append(0)
            self.Sbh.append(0)
        self.TP[x] = random.getrandbits(62)
        self.TV[x], self.TN[x], self.TD[x] = t, ln, desc
        self.Omn[x] = self._kth(t, 1)
        self._tpull(x)
        return x

    def _tpull(self, x):
        L, R = self.TL[x], self.TR[x]
        t = self.TV[x]
        TS = self.TS
        TS[x] = TS[L] + self.TN[x] + TS[R]
        m = self.Omn[x]
        if self.Smn[L] < m:
            m = self.Smn[L]
        if self.Smn[R] < m:
            m = self.Smn[R]
        self.Smn[x] = m
        self.Sov[x] = self.Sov[L] | self.ov[t] | self.Sov[R]
        pw, Sfh, Sbh = self.pw, self.Sfh, self.Sbh
        f, b = (self.bh[t], self.fh[t]) if self.TD[x] else (self.fh[t], self.bh[t])  # the run, read left to right / right to left
        m = self.TN[x]
        Sfh[x] = ((Sfh[L] * pw[m] + f) * pw[TS[R]] + Sfh[R]) % _HP
        Sbh[x] = ((Sbh[R] * pw[m] + b) * pw[TS[L]] + Sbh[L]) % _HP

    def _rev(self, x):  # reverse x's subtree: swap its children (and below, lazily), flip its run
        if not x:
            return
        self.TL[x], self.TR[x] = self.TR[x], self.TL[x]
        self.TD[x] = not self.TD[x]
        self.Sfh[x], self.Sbh[x] = self.Sbh[x], self.Sfh[x]
        self.TF[x] = not self.TF[x]

    def _push(self, x):
        if self.TF[x]:
            self._rev(self.TL[x])
            self._rev(self.TR[x])
            self.TF[x] = False

    # (the first k elements, the rest), cutting the run that straddles k
    def _tsplit(self, x, k):
        if not x or k <= 0:
            return 0, x
        if k >= self.TS[x]:
            return x, 0
        self._push(x)
        L = self.TL[x]
        ls = self.TS[L]
        if k <= ls:
            a, b = self._tsplit(L, k)
            self.TL[x] = b
            self._tpull(x)
            return a, x
        if k >= ls + self.TN[x]:
            a, b = self._tsplit(self.TR[x], k - ls - self.TN[x])
            self.TR[x] = a
            self._tpull(x)
            return x, b
        k -= ls  # cut this run: x keeps its first k elements, a new node the rest
        t, ln = self.TV[x], self.TN[x]
        if self.TD[x]:  # the first k are the k largest
            b, a = self._split(t, ln - k, self.vlo, self.vhi)
        else:
            a, b = self._split(t, k, self.vlo, self.vhi)
        self.TV[x], self.TN[x] = a, k
        self.Omn[x] = self._kth(a, 1)
        u = self._run(b, ln - k, self.TD[x])
        R = self.TR[x]
        self.TR[x] = 0
        self._tpull(x)
        return x, self._tmerge(u, R)

    def _tmerge(self, a, b):
        if not a or not b:
            return a or b
        if self.TP[a] > self.TP[b]:
            self._push(a)
            self.TR[a] = self._tmerge(self.TR[a], b)
            self._tpull(a)
            return a
        self._push(b)
        self.TL[b] = self._tmerge(a, self.TL[b])
        self._tpull(b)
        return b

    # (before l, a[l..r], after r) as three treaps
    def _extract(self, l, r):
        A, B = self._tsplit(self.top, l)
        B, C = self._tsplit(B, r - l + 1)
        return A, B, C

    def _join(self, A, B, C):
        self.top = self._tmerge(self._tmerge(A, B), C)

    def _nodes(self, x):  # every run node of x's treap
        out, stack = [], [x] if x else []
        while stack:
            x = stack.pop()
            out.append(x)
            for c in (self.TL[x], self.TR[x]):
                if c:
                    stack.append(c)
        return out

    def _drop(self, x):  # free every run of x (value trees and treap nodes)
        for y in self._nodes(x):
            self._freeTree(self.TV[y])
            self.tfree.append(y)

    # a[l..r] becomes one sorted run: every run inside merges into one
    def _sort(self, l, r, desc):
        A, B, C = self._extract(l, r)
        t = 0
        for y in self._nodes(B):
            t = self._merge(t, self.TV[y], self.vlo, self.vhi)
            self.tfree.append(y)
        self._join(A, self._run(t, r - l + 1, desc), C)

    # ---- internals: value trees (node 0 = the empty tree) ----

    def _node(self):
        if self.free:
            t = self.free.pop()
            self.Lc[t] = self.Rc[t] = self.cnt[t] = 0
            return t
        self.Lc.append(0)
        self.Rc.append(0)
        self.cnt.append(0)
        self.ov.append(0)
        self.fh.append(0)
        self.bh.append(0)
        return len(self.cnt) - 1

    def _freeTree(self, t):  # hand every node of t back
        stack = [t] if t else []
        while stack:
            t = stack.pop()
            self.free.append(t)
            for c in (self.Lc[t], self.Rc[t]):
                if c:
                    stack.append(c)

    # node x holds c copies of v (a leaf, or a node with one value under it)
    def _setLeaf(self, x, v, c):
        self.cnt[x] = c
        self.ov[x] = v
        self.fh[x] = self.bh[x] = (v + _HO) % _HP * self.gs[c] % _HP

    def _pull(self, x):
        l, r = self.Lc[x], self.Rc[x]
        cnt = self.cnt
        cnt[x] = cnt[l] + cnt[r]
        self.ov[x] = self.ov[l] | self.ov[r]
        fh, bh, pw = self.fh, self.bh, self.pw
        fh[x] = (fh[l] * pw[cnt[r]] + fh[r]) % _HP
        bh[x] = (bh[r] * pw[cnt[l]] + bh[l]) % _HP

    # hash tables up to length m: pw[k] = B^k, gs[k] = 1 + B + ... + B^(k-1)
    def _grow(self, m):
        pw, gs = self.pw, self.gs
        while len(pw) <= m:
            gs.append((gs[-1] + pw[-1]) % _HP)
            pw.append(pw[-1] * _HB % _HP)

    # a tree holding c copies of v: one node per level
    def _leaf(self, v, c=1):
        top = t = self._node()
        nl, nh = self.vlo, self.vhi
        while True:
            self._setLeaf(t, v, c)
            if nl == nh:
                return top
            mid = (nl + nh) >> 1
            u = self._node()
            if v <= mid:
                self.Lc[t], nh = u, mid
            else:
                self.Rc[t], nl = u, mid + 1
            t = u

    # (the k smallest of t, the rest), 0 <= k <= cnt[t]: t keeps the first part, new nodes (one path) the second
    def _split(self, t, k, nl, nh):
        cnt = self.cnt
        if k <= 0:
            return 0, t
        if k >= cnt[t]:
            return t, 0
        b = self._node()
        if nl == nh:  # one value: split its copies
            self._setLeaf(b, nl, cnt[t] - k)
            self._setLeaf(t, nl, k)
            return t, b
        mid = (nl + nh) >> 1
        cl = cnt[self.Lc[t]]
        if k <= cl:
            self.Lc[t], self.Lc[b] = self._split(self.Lc[t], k, nl, mid)
            self.Rc[b], self.Rc[t] = self.Rc[t], 0
        else:
            self.Rc[t], self.Rc[b] = self._split(self.Rc[t], k - cl, mid + 1, nh)
        self._pull(t)
        self._pull(b)
        return t, b

    # the union of a and b, overlaid node by node (b's nodes where both have one are freed)
    def _merge(self, a, b, nl, nh):
        if not a or not b:
            return a or b
        if nl == nh:
            self._setLeaf(a, nl, self.cnt[a] + self.cnt[b])
        else:
            mid = (nl + nh) >> 1
            self.Lc[a] = self._merge(self.Lc[a], self.Lc[b], nl, mid)
            self.Rc[a] = self._merge(self.Rc[a], self.Rc[b], mid + 1, nh)
            self._pull(a)
        self.free.append(b)
        return a

    # the k-th smallest value of t, 1 <= k <= cnt[t]
    def _kth(self, t, k):
        nl, nh, cnt, Lc, Rc = self.vlo, self.vhi, self.cnt, self.Lc, self.Rc
        while nl != nh:
            mid = (nl + nh) >> 1
            cl = cnt[Lc[t]]
            if k <= cl:
                t, nh = Lc[t], mid
            else:
                k -= cl
                t, nl = Rc[t], mid + 1
        return nl

    # t's values, ascending (or descending)
    def _values(self, t, desc):
        out = []
        stack = [(t, self.vlo, self.vhi)]
        while stack:  # in-order, pushed right first
            t, nl, nh = stack.pop()
            if not self.cnt[t]:
                continue
            if nl == nh:
                out += [nl] * self.cnt[t]
                continue
            mid = (nl + nh) >> 1
            stack.append((self.Rc[t], mid + 1, nh))
            stack.append((self.Lc[t], nl, mid))
        return out[::-1] if desc else out
