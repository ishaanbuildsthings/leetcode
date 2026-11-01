# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sorted-runs-sum-xor-min-or-hash/template.py
# @operations: getAll isPalindrome pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeHash rangeHashReversed rangeMin rangeOrQuery rangeSortAsc rangeSortDesc rangeSum rangeXorQuery rangesEqual
# @data-structure-type: sorted-runs
# @complexities:
#   getAll: N*log(U)
#   isPalindrome: log(N)+log(U) amortized
#   pointAdd: log(N)+log(U) amortized
#   pointAssign: log(N)+log(U) amortized
#   pointChmax: log(N)+log(U) amortized
#   pointChmin: log(N)+log(U) amortized
#   pointGet: log(N)+log(U)
#   rangeAssign: log(N)+log(U) amortized
#   rangeHash: log(N)+log(U) amortized
#   rangeHashReversed: log(N)+log(U) amortized
#   rangeMin: log(N)+log(U) amortized
#   rangeOrQuery: log(N)+log(U) amortized
#   rangeSortAsc: log(N)+log(U) amortized
#   rangeSortDesc: log(N)+log(U) amortized
#   rangeSum: log(N)+log(U) amortized
#   rangeXorQuery: log(N)+log(U) amortized
#   rangesEqual: log(N)+log(U) amortized
#   build: N*log(U)
# @memory:
#   layout: none
#   node: Lc[1*N*log(U)] Rc[1*N*log(U)] cnt[1*N*log(U)] sm[1*N*log(U)] xr[1*N*log(U)] ov[1*N*log(U)] fh[1*N*log(U)] bh[1*N*log(U)]
#   tags: none
#   other: root[1*N] len[1*N] desc[1*N] bc[1*N] qs[4*N] qx[4*N] qn[4*N] qo[4*N] qf[4*N] qb[4*N] ql[4*N] pw[1*N] gs[1*N]
#   note: value nodes: N log U to start, plus O(log U) per cut (merges free nodes, which are reused); a seg tree over positions holds each run's sum / xor / min / or / hashes at its start; U = valHi - valLo + 1

# An array whose ranges you can sort in place (ascending or descending), amortized O(log N + log U) a sort, with point
# reads / writes, rangeAssign, range sums, range xors, range mins, range ors, range hashes both ways (isPalindrome,
# rangesEqual) and the whole array. It is kept as a sequence of sorted runs: each run is a dynamic value seg tree over
# [valLo, valHi] (copies per node) and an up / down flag, and a Fenwick tree over positions marks where runs start,
# and a seg tree over positions holds each run's sum / xor / min / or / hashes at its start. Sorting [l, r] cuts the
# runs at l and r + 1 and merges every run inside into one; a[i] is the k-th value of the run holding it; a query cuts
# at l and r + 1 too, then reads whole runs. Merges cost about as many nodes as they free and every run is merged away
# at most once, hence the amortized bounds. Indices 0-based, ranges inclusive, every index is a position in the
# current array. Hashes are polynomial, mod the prime 2^61 - 1, with a base and a value offset random per run:
# hash(x1..xk) = x1 B^(k-1) + ... + xk; a value tree keeps the hash of its values in sorted order both ways.

import random
INF = float("inf")
_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


class SortedRunsSumXorMinOrHash:
    # O(N log U) -- arr: the initial array; every value a[i] ever holds must lie in [valLo, valHi] (U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        n = self.n = len(arr)
        self.vlo, self.vhi = valLo, valHi
        self.Lc, self.Rc, self.cnt = [0], [0], [0]  # value node 0 = the empty tree
        self.sm = [0]
        self.xr = [0]
        self.ov = [0]
        self.fh = [0]
        self.bh = [0]
        self.free = []  # value nodes freed by merges, reused first
        self.pw, self.gs = [1], [0]
        self._grow(n)
        self.root = [self._leaf(v) for v in arr]  # per run start: its value tree (every element starts as its own run)
        self.len = [1] * n  # per run start: its length
        self.desc = [False] * n  # per run start: sorted descending?
        self.bc = [0] + [1] * n  # Fenwick: 1 at each run start
        self.top = 1 << (n.bit_length() - 1) if n else 0
        for i in range(1, n + 1):  # O(N) Fenwick builds
            j = i + (i & -i)
            if j <= n:
                self.bc[j] += self.bc[i]
        size = self.size = 1 << max(0, (n - 1).bit_length())  # seg tree over positions: each run's aggregates at its start
        self.qs = [0] * (2 * size)
        self.qx = [0] * (2 * size)
        self.qn = [INF] * (2 * size)
        self.qo = [0] * (2 * size)
        self.qf = [0] * (2 * size)
        self.qb = [0] * (2 * size)
        self.ql = [0] * (2 * size)
        for s in range(n):
            self._set(s + size, s)
        for p in range(size - 1, 0, -1):
            self._up(p)

    # O(log N + log U) -- a[i]
    def pointGet(self, i):
        s = self._startOf(i)
        k = i - s
        return self._kth(self.root[s], self.len[s] - k if self.desc[s] else k + 1)

    # O(log N + log U) amortized -- a[i] = v
    def pointAssign(self, i, v):
        self._cutAt(i)
        self._cutAt(i + 1)
        self._io(i, -1)
        self._freeTree(self.root[i])
        self.root[i] = self._leaf(v)
        self._io(i, 1)

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
        self._sort(l, r, False, None)

    # O(log N + log U) amortized -- sort a[l..r] descending
    def rangeSortDesc(self, l, r):
        self._sort(l, r, True, None)

    # O(log N + log U) amortized -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        self._sort(l, r, False, v)

    # O(log N + log U) amortized -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        self._cutAt(l)
        self._cutAt(r + 1)
        return self._ask(l, r)[0]

    # O(log N + log U) amortized -- a[l] ^ ... ^ a[r]
    def rangeXorQuery(self, l, r):
        self._cutAt(l)
        self._cutAt(r + 1)
        return self._ask(l, r)[1]

    # O(log N + log U) amortized -- min of a[l..r]
    def rangeMin(self, l, r):
        self._cutAt(l)
        self._cutAt(r + 1)
        return self._ask(l, r)[2]

    # O(log N + log U) amortized -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r):
        self._cutAt(l)
        self._cutAt(r + 1)
        return self._ask(l, r)[3]

    # O(log N + log U) amortized -- is a[l..r] a palindrome?
    def isPalindrome(self, l, r):
        self._cutAt(l)
        self._cutAt(r + 1)
        res = self._ask(l, r)
        return res[4] == res[5]

    # O(log N + log U) amortized -- hash of a[l..r] read left to right (a[l] B^(len-1) + ... + a[r], mod 2^61 - 1; B random per run): equal ranges hash equal
    def rangeHash(self, l, r):
        self._cutAt(l)
        self._cutAt(r + 1)
        return self._ask(l, r)[4]

    # O(log N + log U) amortized -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    def rangeHashReversed(self, l, r):
        self._cutAt(l)
        self._cutAt(r + 1)
        return self._ask(l, r)[5]

    # O(log N + log U) amortized -- a[l1..r1] == a[l2..r2]? (equal lengths and equal hashes)
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(N log U) -- the whole current array
    def getAll(self):
        out, s = [], 0
        while s < self.n:
            out += self._values(self.root[s], self.desc[s])
            s += self.len[s]
        return out

    # ---- internals: runs ----

    # cut at l and r + 1, then turn a[l..r] into one run: every run inside merged (v is None) or thrown away for a run
    # of r - l + 1 copies of v
    def _sort(self, l, r, desc, v):
        self._cutAt(l)
        self._cutAt(r + 1)
        self._io(l, -1)
        t, s = self.root[l], l + self.len[l]
        if v is not None:
            self._freeTree(t)
        while s <= r:  # every run inside goes
            b, nxt = self.root[s], s + self.len[s]
            self._io(s, -1)
            self._fen(self.bc, s, -1)
            if v is None:
                t = self._merge(t, b, self.vlo, self.vhi)
            else:
                self._freeTree(b)
            s = nxt
        self.root[l] = t if v is None else self._leaf(v, r - l + 1)
        self.len[l], self.desc[l] = r - l + 1, desc
        self._io(l, 1)

    # make a run start at p (0 < p < n): split the run holding it by count
    def _cutAt(self, p):
        if p <= 0 or p >= self.n:
            return
        s = self._startOf(p)
        if s == p:
            return
        self._io(s, -1)
        t, k, ln = self.root[s], p - s, self.len[s]
        if self.desc[s]:  # the first k are the k largest
            b, a = self._split(t, ln - k, self.vlo, self.vhi)
        else:
            a, b = self._split(t, k, self.vlo, self.vhi)
        self.root[s], self.len[s] = a, k
        self.root[p], self.len[p], self.desc[p] = b, ln - k, self.desc[s]
        self._fen(self.bc, p, 1)
        self._io(s, 1)
        self._io(p, 1)

    # the start of the run holding i: the (# of starts <= i)-th start, by binary lifting
    def _startOf(self, i):
        k, bc, pos, step = self._pre(self.bc, i + 1), self.bc, 0, self.top
        while step:
            nxt = pos + step
            if nxt <= self.n and bc[nxt] < k:
                pos = nxt
                k -= bc[nxt]
            step >>= 1
        return pos

    def _fen(self, f, i, v):
        n = self.n
        i += 1
        while i <= n:
            f[i] += v
            i += i & -i

    @staticmethod
    def _pre(f, i):  # f's total over positions 0..i-1
        s = 0
        while i > 0:
            s += f[i]
            i &= i - 1
        return s

    # leaf p of the position tree <- the aggregates of the run starting at s
    def _set(self, p, s):
        t = self.root[s]
        self.qs[p] = self.sm[t]
        self.qx[p] = self.xr[t]
        self.qn[p] = self._kth(t, 1)
        self.qo[p] = self.ov[t]
        if self.desc[s]:
            self.qf[p], self.qb[p] = self.bh[t], self.fh[t]
        else:
            self.qf[p], self.qb[p] = self.fh[t], self.bh[t]
        self.ql[p] = self.len[s]

    def _up(self, p):
        l, r = 2 * p, 2 * p + 1
        self.qs[p] = self.qs[l] + self.qs[r]
        self.qx[p] = self.qx[l] ^ self.qx[r]
        a, b = self.qn[l], self.qn[r]
        self.qn[p] = a if a < b else b
        self.qo[p] = self.qo[l] | self.qo[r]
        qf, qb, ql, pw = self.qf, self.qb, self.ql, self.pw
        qf[p] = (qf[l] * pw[ql[r]] + qf[r]) % _HP
        qb[p] = (qb[r] * pw[ql[l]] + qb[l]) % _HP
        ql[p] = ql[l] + ql[r]

    # add (sgn = 1) or take out (sgn = -1) the run starting at s from the position tree
    def _io(self, s, sgn):
        p = s + self.size
        if sgn > 0:
            self._set(p, s)
        else:
            self.qs[p] = 0
            self.qx[p] = 0
            self.qn[p] = INF
            self.qo[p] = 0
            self.qf[p] = 0
            self.qb[p] = 0
            self.ql[p] = 0
        p >>= 1
        while p:
            self._up(p)
            p >>= 1

    # the aggregates of positions l..r (s, x, mn, o, (lf * pw[rl] + rf) % _HP, (rb * pw[ll] + lb) % _HP)
    def _ask(self, l, r):
        qs, qx, qn, qo, qf, qb, ql = self.qs, self.qx, self.qn, self.qo, self.qf, self.qb, self.ql
        pw = self.pw
        s = 0
        x = 0
        mn = INF
        o = 0
        lf = lb = ll = rf = rb = rl = 0  # hashes of the left part and of the right part
        l += self.size
        r += self.size + 1
        while l < r:
            if l & 1:
                s += qs[l]
                x ^= qx[l]
                if qn[l] < mn:
                    mn = qn[l]
                o |= qo[l]
                lf = (lf * pw[ql[l]] + qf[l]) % _HP
                lb = (qb[l] * pw[ll] + lb) % _HP
                ll += ql[l]
                l += 1
            if r & 1:
                r -= 1
                s += qs[r]
                x ^= qx[r]
                if qn[r] < mn:
                    mn = qn[r]
                o |= qo[r]
                rf = (qf[r] * pw[rl] + rf) % _HP
                rb = (rb * pw[ql[r]] + qb[r]) % _HP
                rl += ql[r]
            l >>= 1
            r >>= 1
        return s, x, mn, o, (lf * pw[rl] + rf) % _HP, (rb * pw[ll] + lb) % _HP

    # ---- internals: value trees (node 0 = the empty tree) ----

    def _node(self):
        if self.free:
            t = self.free.pop()
            self.Lc[t] = self.Rc[t] = self.cnt[t] = 0
            return t
        self.Lc.append(0)
        self.Rc.append(0)
        self.cnt.append(0)
        self.sm.append(0)
        self.xr.append(0)
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
        self.sm[x] = c * v
        self.xr[x] = v if c & 1 else 0
        self.ov[x] = v
        self.fh[x] = self.bh[x] = (v + _HO) % _HP * self.gs[c] % _HP

    def _pull(self, x):
        l, r = self.Lc[x], self.Rc[x]
        cnt = self.cnt
        cnt[x] = cnt[l] + cnt[r]
        self.sm[x] = self.sm[l] + self.sm[r]
        self.xr[x] = self.xr[l] ^ self.xr[r]
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
