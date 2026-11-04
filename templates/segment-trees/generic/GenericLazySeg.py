# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericLazySeg.py
#
# Generic lazy segment tree: pass combine, apply and compose, then build it from leaves you make yourself.
# Build O(n) combines; query / update / set / get / maxRight / minLeft O(log n); memory up to 4n nodes and 2n tags.
#
# - A leaf is any value you build: it can carry whatever combine and apply need (the value, its index, a flag, ...).
#   Tuples are the fastest; a class with __slots__ reads better.
# - combine(left, right) gets two neighbouring segments, left first, and needn't be commutative.
# - A tag is a pending update to every element of a segment (any value but None). apply sees only the node, so a node
#   that needs its segment's length (adding to a sum, assigning) stores it: a leaf gets len = 1, combine adds them.
# - Never mutate a node or tag passed in: return a new one.
# - No identity node or tag is needed: the tree tracks which nodes are empty and which tags are pending itself.
# - Need a node's index range? Put lo / hi in the node: a leaf gets lo = hi = i, combine takes left's lo, right's hi.
#
# Example, range add + range assign, range sum + max; a node is (sum, mx, len), a tag is (assign, v):
#   def combine(a, b):
#       return (a[0] + b[0], max(a[1], b[1]), a[2] + b[2])
#   def apply(x, g):
#       return (g[1] * x[2], g[1], x[2]) if g[0] else (x[0] + g[1] * x[2], x[1] + g[1], x[2])
#   def compose(old, g):
#       return g if g[0] else (old[0], old[1] + g[1])
#   seg = LazySeg([(x, x, 1) for x in a], combine, apply, compose)
#   seg.update(l, r, (False, 5))  # add 5 to l..r
#   seg.update(l, r, (True, 7))   # assign 7 to l..r
#   seg.query(l, r)[0]
#   # first r >= l where max(l..r) reaches k: seg.maxRight(l, lambda s: s[1] < k) + 1


# TODO: the node for the segment left + right (left ends just before right starts)
def combine(left, right):
    pass


# TODO: the node's segment after tag is applied to every element of it
def apply(node, tag):
    pass


# TODO: the single tag that does old first, then newer
def compose(old, newer):
    pass


class LazySeg:
    # leaves: a[0..n-1] as nodes; combine(left, right) -> node; apply(node, tag) -> node; compose(old, newer) -> tag
    def __init__(self, leaves, combine, apply, compose):
        self.n = n = len(leaves)
        self.cap = cap = 1 << max(0, (n - 1).bit_length())
        self.lg = cap.bit_length() - 1
        self.combine, self.apply, self.compose = combine, apply, compose
        # None marks a node over padding only (the padding past n); a node partly over padding is its real part
        self.t = t = [None] * cap + list(leaves) + [None] * (cap - n)
        # lz[k]: the tag pending for node k's children, None if there is none
        self.lz = [None] * cap
        for k in range(cap - 1, 0, -1):
            t[k] = t[2 * k] if t[2 * k + 1] is None else combine(t[2 * k], t[2 * k + 1])

    def _applyAt(self, k, tag):
        t = self.t
        if t[k] is None:
            return
        t[k] = self.apply(t[k], tag)
        if k < self.cap:
            lz = self.lz
            lz[k] = tag if lz[k] is None else self.compose(lz[k], tag)

    def _push(self, k):
        tag = self.lz[k]
        if tag is not None:
            self._applyAt(2 * k, tag)
            self._applyAt(2 * k + 1, tag)
            self.lz[k] = None

    def _pull(self, k):
        t = self.t
        t[k] = t[2 * k] if t[2 * k + 1] is None else self.combine(t[2 * k], t[2 * k + 1])

    # pushes the tags above the leaf range [l, r) (l and r already offset by cap)
    def _pushAbove(self, l, r):
        for i in range(self.lg, 0, -1):
            if (l >> i) << i != l:
                self._push(l >> i)
            if (r >> i) << i != r:
                self._push((r - 1) >> i)

    # how many leaves
    def size(self):
        return self.n

    # the leaf at i, every update applied; needs 0 <= i < n, else IndexError
    def get(self, i):
        if not 0 <= i < self.n:
            raise IndexError("get: needs 0 <= i < n")
        k = self.cap + i
        for j in range(self.lg, 0, -1):
            self._push(k >> j)
        return self.t[k]

    # replaces the leaf at i (earlier updates don't apply to the new leaf); needs 0 <= i < n, else IndexError
    def set(self, i, leaf):
        if not 0 <= i < self.n:
            raise IndexError("set: needs 0 <= i < n")
        k = self.cap + i
        for j in range(self.lg, 0, -1):
            self._push(k >> j)
        self.t[k] = leaf
        for j in range(1, self.lg + 1):
            self._pull(k >> j)

    # combine of the leaves l..r; needs 0 <= l <= r < n, else IndexError
    def query(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError("query: needs 0 <= l <= r < n")
        l += self.cap
        r += self.cap + 1
        self._pushAbove(l, r)
        t, combine = self.t, self.combine
        sl = sr = None
        while l < r:
            if l & 1:
                sl = t[l] if sl is None else combine(sl, t[l])
                l += 1
            if r & 1:
                r -= 1
                sr = t[r] if sr is None else combine(t[r], sr)
            l >>= 1
            r >>= 1
        if sl is None:
            return sr
        if sr is None:
            return sl
        return combine(sl, sr)

    # combine of every leaf; needs n >= 1, else IndexError
    def all(self):
        if self.n == 0:
            raise IndexError("all: needs n >= 1")
        return self.t[1]

    # applies tag to every element of l..r; needs 0 <= l <= r < n, else IndexError
    def update(self, l, r, tag):
        if not 0 <= l <= r < self.n:
            raise IndexError("update: needs 0 <= l <= r < n")
        l += self.cap
        r += self.cap + 1
        self._pushAbove(l, r)
        a, b = l, r
        while a < b:
            if a & 1:
                self._applyAt(a, tag)
                a += 1
            if b & 1:
                b -= 1
                self._applyAt(b, tag)
            a >>= 1
            b >>= 1
        for i in range(1, self.lg + 1):
            if (l >> i) << i != l:
                self._pull(l >> i)
            if (r >> i) << i != r:
                self._pull((r - 1) >> i)

    # The largest r in [l, n - 1] with ok(query(l, r)) true, or l - 1 if ok(query(l, l)) is false.
    # ok must be monotone: true for l..r means true for every shorter l..r'. Needs 0 <= l < n, else IndexError.
    def maxRight(self, l, ok):
        if not 0 <= l < self.n:
            raise IndexError("maxRight: needs 0 <= l < n")
        t, combine, cap = self.t, self.combine, self.cap
        k = l + cap
        for i in range(self.lg, 0, -1):
            self._push(k >> i)
        sm = None
        while True:
            while k % 2 == 0:
                k >>= 1
            if t[k] is None:
                return self.n - 1  # only padding left: every real leaf fit
            nx = t[k] if sm is None else combine(sm, t[k])
            if not ok(nx):
                while k < cap:
                    self._push(k)
                    k *= 2
                    nl = t[k] if sm is None else combine(sm, t[k])
                    if ok(nl):
                        sm = nl
                        k += 1
                return k - cap - 1
            sm = nx
            k += 1
            if k & -k == k:
                return self.n - 1

    # The smallest l in [0, r] with ok(query(l, r)) true, or r + 1 if ok(query(r, r)) is false.
    # ok must be monotone: true for l..r means true for every shorter l'..r. Needs 0 <= r < n, else IndexError.
    def minLeft(self, r, ok):
        if not 0 <= r < self.n:
            raise IndexError("minLeft: needs 0 <= r < n")
        t, combine, cap = self.t, self.combine, self.cap
        k = r + 1 + cap
        for i in range(self.lg, 0, -1):
            self._push((k - 1) >> i)
        sm = None
        while True:
            k -= 1
            while k > 1 and k % 2:
                k >>= 1
            nx = t[k] if sm is None else combine(t[k], sm)
            if not ok(nx):
                while k < cap:
                    self._push(k)
                    k = 2 * k + 1
                    nr = t[k] if sm is None else combine(t[k], sm)
                    if ok(nr):
                        sm = nr
                        k -= 1
                return k + 1 - cap
            sm = nx
            if k & -k == k:
                return 0
