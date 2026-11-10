# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeSortAsc-rangeSortDesc-rangeSum-rangeXorQuery/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeSortAsc rangeSortDesc rangeSum rangeXorQuery sumAll xorAll
# @data-structure-type: sorted-runs
# @complexities:
#   getAll: N*log(U)
#   pointAdd: log(N)+log(U) amortized
#   pointAssign: log(N)+log(U) amortized
#   pointChmax: log(N)+log(U) amortized
#   pointChmin: log(N)+log(U) amortized
#   pointGet: log(N)+log(U)
#   rangeAssign: log(N)+log(U) amortized
#   rangeSortAsc: log(N)+log(U) amortized
#   rangeSortDesc: log(N)+log(U) amortized
#   rangeSum: log(N)+log(U) amortized
#   rangeXorQuery: log(N)+log(U) amortized
#   sumAll: log(N)+log(U) amortized
#   xorAll: log(N)+log(U) amortized
#   build: N*log(U)
# @memory:
#   layout: none
#   node: Lc[1*N*log(U)] Rc[1*N*log(U)] cnt[1*N*log(U)] sm[1*N*log(U)] xr[1*N*log(U)]
#   tags: none
#   other: root[1*N] len[1*N] desc[1*N] bc[1*N] bs[1*N] bx[1*N]
#   note: value nodes: N log U to start, plus O(log U) per cut (merges free nodes, which are reused); Fenwick trees over positions mark run starts and hold each run's sum / xor; U = valHi - valLo + 1

# An array whose ranges you can sort in place (ascending or descending), amortized O(log N + log U) a sort, with point
# reads / writes, rangeAssign, range sums, range xors and the whole array. It is kept as a sequence of sorted runs:
# each run is a dynamic value seg tree over [valLo, valHi] (copies per node) and an up / down flag, and a Fenwick tree
# over positions marks where runs start, others hold each run's sum / xor at its start. Sorting [l, r] cuts the runs
# at l and r + 1 and merges every run inside into one; a[i] is the k-th value of the run holding it; a query cuts at l
# and r + 1 too, then reads whole runs. Merges cost about as many nodes as they free and every run is merged away at
# most once, hence the amortized bounds. Indices 0-based, ranges inclusive, every index is a position in the current
# array.



class SortedRunsSumXor:
    # O(N log U) -- arr: the initial array; every value a[i] ever holds must lie in [valLo, valHi] (U = valHi - valLo
    # + 1)
    def __init__(self, arr, valLo, valHi):
        n = self.n = len(arr)
        self.vlo, self.vhi = valLo, valHi
        self.Lc, self.Rc, self.cnt = [0], [0], [0]  # value node 0 = the empty tree
        self.sm = [0]
        self.xr = [0]
        self.free = []  # value nodes freed by merges, reused first
        self.root = [self._leaf(v) for v in arr]  # per run start: its value tree (every element starts as its own run)
        self.len = [1] * n  # per run start: its length
        self.desc = [False] * n  # per run start: sorted descending?
        self.bc = [0] + [1] * n  # Fenwick: 1 at each run start
        self.top = 1 << (n.bit_length() - 1) if n else 0
        self.bs = [0] + list(arr)  # Fenwick: each run's sum, at its start
        self.bx = [0] + list(arr)  # Fenwick (of xors): each run's xor, at its start
        for i in range(1, n + 1):  # O(N) Fenwick builds
            j = i + (i & -i)
            if j <= n:
                self.bc[j] += self.bc[i]
                self.bs[j] += self.bs[i]
                self.bx[j] ^= self.bx[i]

    # O(log N + log U) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        s = self._startOf(i)
        k = i - s
        return self._kth(self.root[s], self.len[s] - k if self.desc[s] else k + 1)

    # O(log N + log U) amortized -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self._cutAt(i)
        self._cutAt(i + 1)
        self._io(i, -1)
        self._freeTree(self.root[i])
        self.root[i] = self._leaf(v)
        self._io(i, 1)

    # O(log N + log U) amortized -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + v)

    # O(log N + log U) amortized -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if v > self.pointGet(i):
            self.pointAssign(i, v)

    # O(log N + log U) amortized -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if v < self.pointGet(i):
            self.pointAssign(i, v)

    # O(log N + log U) amortized -- sort a[l..r] ascending; needs 0 <= l <= r < n, else IndexError
    def rangeSortAsc(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSortAsc: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._sort(l, r, False, None)

    # O(log N + log U) amortized -- sort a[l..r] descending; needs 0 <= l <= r < n, else IndexError
    def rangeSortDesc(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSortDesc: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._sort(l, r, True, None)

    # O(log N + log U) amortized -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._sort(l, r, False, v)

    # O(log N + log U) amortized -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._cutAt(l)
        self._cutAt(r + 1)
        return self._pre(self.bs, r + 1) - self._pre(self.bs, l)

    # O(log N + log U) amortized -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeXorQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeXorQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._cutAt(l)
        self._cutAt(r + 1)
        return self._prex(r + 1) ^ self._prex(l)

    # O(N log U) -- the whole current array
    def getAll(self):
        out, s = [], 0
        while s < self.n:
            out += self._values(self.root[s], self.desc[s])
            s += self.len[s]
        return out

    # O(log(N)+log(U) amortized) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises
    # IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)

    # O(log(N)+log(U) amortized) -- xor of the whole array a[0..n-1] (rangeXorQuery(0, n - 1)); needs n >= 1, else
    # raises IndexError
    def xorAll(self):
        if self.n < 1:
            raise IndexError("xorAll: needs n >= 1")
        return self.rangeXorQuery(0, self.n - 1)

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

    def _prex(self, i):  # xor of positions 0..i-1
        f, s = self.bx, 0
        while i > 0:
            s ^= f[i]
            i &= i - 1
        return s

    # add (sgn = 1) or take out (sgn = -1) the run starting at s from the run aggregates
    def _io(self, s, sgn):
        t = self.root[s]
        self._fen(self.bs, s, sgn * self.sm[t])
        self._fenx(s, self.xr[t])

    def _fenx(self, i, v):  # xor v in at i
        f, n = self.bx, self.n
        i += 1
        while i <= n:
            f[i] ^= v
            i += i & -i

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

    def _pull(self, x):
        l, r = self.Lc[x], self.Rc[x]
        cnt = self.cnt
        cnt[x] = cnt[l] + cnt[r]
        self.sm[x] = self.sm[l] + self.sm[r]
        self.xr[x] = self.xr[l] ^ self.xr[r]

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
