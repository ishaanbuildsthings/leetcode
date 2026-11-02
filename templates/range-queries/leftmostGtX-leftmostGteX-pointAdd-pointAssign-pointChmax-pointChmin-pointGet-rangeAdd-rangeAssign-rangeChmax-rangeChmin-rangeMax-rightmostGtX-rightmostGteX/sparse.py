# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmax-rangeChmin-rangeMax-rightmostGtX-rightmostGteX/sparse.py
# @operations: leftmostGtX leftmostGteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeMax rightmostGtX rightmostGteX
# @data-structure-type: lazy-seg-tree
# @complexities:
#   leftmostGtX: log(U)
#   leftmostGteX: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeAdd: log(U)
#   rangeAssign: log(U)
#   rangeChmax: log(U)
#   rangeChmin: log(U)
#   rangeMax: log(U)
#   rightmostGtX: log(U)
#   rightmostGteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mx[4*log(U)]
#   tags: hi[4*log(U)] lo[4*log(U)] c[4*log(U)]
#   other: children[8*log(U)]
#   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

# Lazy segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
# position starting at 0; range updates (rangeAdd, rangeAssign, rangeChmax, rangeChmin) and range queries in O(logU),
# U = hi - lo + 1; each node keeps its max over its range. Ranges inclusive [l, r]; searches return lo - 1 when
# nothing qualifies. The root covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so a node
# of level s covers 2^s positions; children are created on demand as blocks of zeros, right before anything descends
# past a node, and a node's pending tags ("applied here, not yet to my children") go down as it is passed.

INF, NEG = float("inf"), float("-inf")


class SparseLazySegTree:
    __slots__ = ('first', 'last', 'D', 'L', 'R', 'mx', 'hi', 'lo', 'c')


    # O(1) -- all zeros over [lo, hi]; any range of integers works (lo <= hi)
    def __init__(self, lo, hi):
        self.first, self.last = lo, hi  # (the index range: lo / hi are the clamp tags' names)
        self.D = (hi - lo).bit_length()  # the root's level: 2^D >= hi - lo + 1
        self.L, self.R = [0], [0]  # node 0: none (node 1 is the root)
        self.mx = [0]
        self.hi = [INF]
        self.lo = [NEG]
        self.c = [0]
        self._newZero(self.D)

    # O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max)
    def leftmostGtX(self, l, r, x):
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in self._cover(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    self._push(t)
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
                    self._push(t)
                    s -= 1
                    if F[L[t]] >= x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)
                return tl
        return self.first - 1

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
        self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._applyClamp(t, INF, NEG, v))

    # O(logU) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._applyClamp(t, v, v, 0))

    # O(logU) -- a[i] = max(a[i], v) for i in [l, r]
    def rangeChmax(self, l, r, v):
        self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._applyClamp(t, INF, v, 0))

    # O(logU) -- a[i] = min(a[i], v) for i in [l, r]
    def rangeChmin(self, l, r, v):
        self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._applyClamp(t, v, NEG, 0))

    # O(logU) -- max of a[l..r]
    def rangeMax(self, l, r):
        mx, res = self.mx, NEG
        for t, _ in self._nodes(l, r):
            if mx[t] > res:
                res = mx[t]
        return res

    # O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max)
    def rightmostGtX(self, l, r, x):
        F, L, R = self.mx, self.L, self.R
        for t, s, tl in reversed(self._cover(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
                    self._push(t)
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
                    self._push(t)
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
        self.mx.append(0)
        self.hi.append(INF)
        self.lo.append(NEG)
        self.c.append(0)
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
        self._push(x)
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
        self._push(x)
        m = tl + (1 << (s - 1))
        if l < m:
            self._update(self.L[x], s - 1, tl, l, r, f)
        if r >= m:
            self._update(self.R[x], s - 1, m, l, r, f)
        self._pull(x)

    def _leafOf(self, i):  # (the leaf holding a[i], the nodes above it top-down), every tag on the way pushed
        x, s, tl, path = 1, self.D, self.first, []
        while s:
            self._kids(x, s)
            self._push(x)
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
            self._pull(path[k])

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.mx[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.mx[p]

    def _pull(self, x):  # recompute node x from its children
        a, b = self.L[x], self.R[x]
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w

    def _setClamp(self, x, H, Lo, C):  # every value v under node x becomes min(H, max(Lo, v + C))
        self.mx[x] = min(H, max(Lo, self.mx[x] + C))

    def _applyClamp(self, x, H, Lo, C):
        self._setClamp(x, H, Lo, C)
        h = min(H, max(Lo, self.hi[x] + C))
        self.lo[x] = min(max(Lo, self.lo[x] + C), h)
        self.hi[x] = h
        self.c[x] += C

    def _push(self, x):  # hand node x's pending tags to its children
        a, b = self.L[x], self.R[x]
        if self.hi[x] != INF or self.lo[x] != NEG or self.c[x]:
            self._applyClamp(a, self.hi[x], self.lo[x], self.c[x])
            self._applyClamp(b, self.hi[x], self.lo[x], self.c[x])
            self.hi[x], self.lo[x], self.c[x] = INF, NEG, 0
