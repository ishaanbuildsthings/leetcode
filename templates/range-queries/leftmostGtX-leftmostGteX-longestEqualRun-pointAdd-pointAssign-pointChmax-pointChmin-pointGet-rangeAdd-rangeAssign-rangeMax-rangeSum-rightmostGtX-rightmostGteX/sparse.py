# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-longestEqualRun-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeMax-rangeSum-rightmostGtX-rightmostGteX/sparse.py
# @operations: leftmostGtX leftmostGteX longestEqualRun pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeMax rangeSum rightmostGtX rightmostGteX
# @data-structure-type: lazy-seg-tree
# @complexities:
#   leftmostGtX: log(U)
#   leftmostGteX: log(U)
#   longestEqualRun: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeAdd: log(U)
#   rangeAssign: log(U)
#   rangeMax: log(U)
#   rangeSum: log(U)
#   rightmostGtX: log(U)
#   rightmostGteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[4*log(U)] mx[4*log(U)] fv[4*log(U)] lv[4*log(U)] pr[4*log(U)] sr[4*log(U)] br[4*log(U)]
#   tags: asg[4*log(U)] hasAsg[4*log(U)] add[4*log(U)]
#   other: children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

# Lazy segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
# position starting at 0; range updates (rangeAdd, rangeAssign) and range queries in O(logU), U = hi - lo + 1; each
# node keeps its sum, its max, its first / last value and the equal runs at its ends and inside over its range. Ranges
# inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U positions from lo (the
# ones past hi are zeros nobody reads), so a node of level s covers 2^s positions; children are created on demand as
# blocks of zeros, right before anything descends past a node, and a node's pending tags ("applied here, not yet to my
# children") go down as it is passed.

INF, NEG = float("inf"), float("-inf")


class SparseLazySegTree:
    __slots__ = ('first', 'last', 'D', 'L', 'R', 'sm', 'mx', 'fv', 'lv', 'pr', 'sr', 'br', 'asg', 'hasAsg', 'add')


    # O(1) -- all zeros over [lo, hi]; any range of integers works (lo <= hi)
    def __init__(self, lo, hi):
        self.first, self.last = lo, hi  # (the index range: lo / hi are the clamp tags' names)
        self.D = (hi - lo).bit_length()  # the root's level: 2^D >= hi - lo + 1
        self.L, self.R = [0], [0]  # node 0: none (node 1 is the root)
        self.sm = [0]
        self.mx = [0]
        self.fv = [0]
        self.lv = [0]
        self.pr = [0]
        self.sr = [0]
        self.br = [0]
        self.asg = [0]
        self.hasAsg = [0]
        self.add = [0]
        self._newZero(self.D)

    # O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max)
    def leftmostGtX(self, l, r, x):
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    self._push(t, s)
                    s -= 1
                    if F[L[t]] > x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

    # O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max)
    def leftmostGteX(self, l, r, x):
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] >= x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    self._push(t, s)
                    s -= 1
                    if F[L[t]] >= x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

    # O(logN) -- the longest run of equal adjacent values in a[l..r]
    def longestEqualRun(self, l, r):
        pr, sr, br, fv, lv = self.pr, self.sr, self.br, self.fv, self.lv
        ns = self._nodes(l, r)
        t, s = ns[0]
        p, q, res, k, last = pr[t], sr[t], br[t], 1 << s, lv[t]  # (prefix run, suffix run, best, length, last value)
        for t, s in ns[1:]:
            j = last == fv[t]
            if j and q + pr[t] > res:
                res = q + pr[t]
            if br[t] > res:
                res = br[t]
            if j and p == k:
                p += pr[t]
            q = q + sr[t] if j and sr[t] == 1 << s else sr[t]
            k += 1 << s
            last = lv[t]
        return res

    # O(logU) -- a[i] += v
    def pointAdd(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, self._leaf(x) + v)
        self._up(path)

    # O(logU) -- a[i] = v
    def pointAssign(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, v)
        self._up(path)

    # O(logU) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, max(self._leaf(x), v))
        self._up(path)

    # O(logU) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, min(self._leaf(x), v))
        self._up(path)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._leaf(self._leafOf(i)[0])

    # O(logU) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._applyAdd(t, s, v))

    # O(logU) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._applyAssign(t, s, v))

    # O(logU) -- max of a[l..r]
    def rangeMax(self, l, r):
        mx, res = self.mx, NEG
        for t, _ in self._nodes(l, r):
            if mx[t] > res:
                res = mx[t]
        return res

    # O(logU) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        sm, res = self.sm, 0
        for t, _ in self._nodes(l, r):
            res += sm[t]
        return res

    # O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max)
    def rightmostGtX(self, l, r, x):
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    self._push(t, s)
                    s -= 1
                    if F[R[t]] > x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]
                return tl
        return self.first - 1

    # O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max)
    def rightmostGteX(self, l, r, x):
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] >= x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    self._push(t, s)
                    s -= 1
                    if F[R[t]] >= x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]
                return tl
        return self.first - 1

    # ---- internals ----

    def _newZero(self, s):  # a new node: a block of 2^s zeros
        self.L.append(0)
        self.R.append(0)
        self.sm.append(0)
        self.mx.append(0)
        self.fv.append(0)
        self.lv.append(0)
        self.pr.append(1 << s)
        self.sr.append(1 << s)
        self.br.append(1 << s)
        self.asg.append(0)
        self.hasAsg.append(0)
        self.add.append(0)
        return len(self.L) - 1

    def _kids(self, x, s):  # create node x's children (blocks of zeros) if it has none yet
        if not self.L[x]:
            a = self._newZero(s - 1)
            self.L[x], self.R[x] = a, self._newZero(s - 1)

    def _cover(self, l, r):  # the nodes covering a[l..r], left to right, as (node, level, first index)
        out = []
        self._collect(1, self.D, self.first, l, r, out)
        return out

    def _collect(self, x, s, tl, l, r, out):
        if l <= tl and tl + (1 << s) - 1 <= r:
            out.append((x, s, tl))
            return
        self._kids(x, s)
        self._push(x, s)
        m = tl + (1 << (s - 1))
        if l < m:
            self._collect(self.L[x], s - 1, tl, l, r, out)
        if r >= m:
            self._collect(self.R[x], s - 1, m, l, r, out)

    def _nodes(self, l, r):  # the covering nodes left to right, each with its level
        return [(x, s) for x, s, _ in self._cover(l, r)]

    def _update(self, x, s, tl, l, r, f):  # f(node, level, first index) on every node covering a[l..r], then pull up
        if l <= tl and tl + (1 << s) - 1 <= r:
            f(x, s, tl)
            return
        self._kids(x, s)
        self._push(x, s)
        m = tl + (1 << (s - 1))
        if l < m:
            self._update(self.L[x], s - 1, tl, l, r, f)
        if r >= m:
            self._update(self.R[x], s - 1, m, l, r, f)
        self._pull(x, s)

    def _leafOf(self, i):  # (the leaf holding a[i], the nodes above it top-down), every tag on the way pushed
        x, s, tl, path = 1, self.D, self.first, []
        while s:
            self._kids(x, s)
            self._push(x, s)
            path.append(x)
            s -= 1
            if i >= tl + (1 << s):
                tl += 1 << s
                x = self.R[x]
            else:
                x = self.L[x]
        return x, path

    def _up(self, path):  # recompute the nodes of path, deepest first (path[k] has level D - k)
        for k in range(len(path) - 1, -1, -1):
            self._pull(path[k], self.D - k)

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.mx[p] = v
        self.fv[p] = v
        self.lv[p] = v
        self.pr[p] = 1
        self.sr[p] = 1
        self.br[p] = 1

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children
        a, b = self.L[x], self.R[x]
        self.sm[x] = self.sm[a] + self.sm[b]
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w
        h, j = 1 << (s - 1), self.lv[a] == self.fv[b]
        pa, sb = self.pr[a], self.sr[b]
        self.br[x] = max(self.br[a], self.br[b], self.sr[a] + self.pr[b] if j else 0)
        self.pr[x] = pa + self.pr[b] if j and pa == h else pa
        self.sr[x] = sb + self.sr[a] if j and sb == h else sb
        self.fv[x] = self.fv[a]
        self.lv[x] = self.lv[b]

    def _setAssign(self, x, s, v):  # every value under node x becomes v
        k = 1 << s
        self.sm[x] = v * k
        self.mx[x] = v
        self.fv[x] = self.lv[x] = v
        self.pr[x] = self.sr[x] = self.br[x] = k

    def _applyAssign(self, x, s, v):
        self._setAssign(x, s, v)
        self.asg[x], self.hasAsg[x] = v, 1
        self.add[x] = 0

    def _setAdd(self, x, s, v):  # every value under node x gains v
        self.sm[x] += v << s
        self.mx[x] += v
        self.fv[x] += v
        self.lv[x] += v

    def _applyAdd(self, x, s, v):
        self._setAdd(x, s, v)
        if self.hasAsg[x]:
            self.asg[x] += v  # (still an assign, of a shifted value)
        else:
            self.add[x] += v

    def _push(self, x, s):  # hand node x's pending tags to its children
        a, b = self.L[x], self.R[x]
        c = s - 1  # (their level)
        if self.hasAsg[x]:
            v = self.asg[x]
            self._applyAssign(a, c, v)
            self._applyAssign(b, c, v)
            self.hasAsg[x] = 0
        if self.add[x]:
            v = self.add[x]
            self._applyAdd(a, c, v)
            self._applyAdd(b, c, v)
            self.add[x] = 0
