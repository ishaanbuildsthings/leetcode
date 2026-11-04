# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericSeg.py
#
# Generic segment tree: pass combine, then build it from leaves you make yourself.
# Build O(n) combines; query / set / maxRight / minLeft O(log n) combines; memory up to 4n nodes.
#
# - A leaf is any value you build: it can carry whatever combine needs (the value, its index, a flag, ...).
#   Tuples are the fastest; a class with __slots__ reads better.
# - combine(left, right) gets two neighbouring segments, left first, and needn't be commutative. Never mutate its
#   arguments: return a new node.
# - No identity node is needed: combine is only ever called on real, non-empty segments.
# - Need a node's index range? Put lo / hi in the node: a leaf gets lo = hi = i, combine takes left's lo, right's hi.
#
# Example, max subarray sum (non-empty), a node is (sum, pre, suf, best):
#   def combine(a, b):
#       return (a[0] + b[0], max(a[1], a[0] + b[1]), max(b[2], b[0] + a[2]), max(a[3], b[3], a[2] + b[1]))
#   seg = Seg([(x, x, x, x) for x in a], combine)
#   seg.query(l, r)[3]
#   seg.set(i, (x, x, x, x))
#   # first r >= l where the sum of l..r reaches k: seg.maxRight(l, lambda s: s[0] < k) + 1


# TODO: the node for the segment left + right (left ends just before right starts)
def combine(left, right):
    pass


class Seg:
    # leaves: a[0..n-1] as nodes; combine(left, right) -> node
    def __init__(self, leaves, combine):
        self.n = n = len(leaves)
        self.cap = cap = 1 << max(0, (n - 1).bit_length())
        self.combine = combine
        # None marks a node over padding only (the padding past n); a node partly over padding is its real part
        self.t = t = [None] * cap + list(leaves) + [None] * (cap - n)
        for k in range(cap - 1, 0, -1):
            t[k] = t[2 * k] if t[2 * k + 1] is None else combine(t[2 * k], t[2 * k + 1])

    # how many leaves
    def size(self):
        return self.n

    # the leaf at i; needs 0 <= i < n, else IndexError
    def get(self, i):
        if not 0 <= i < self.n:
            raise IndexError("get: needs 0 <= i < n")
        return self.t[self.cap + i]

    # replaces the leaf at i; needs 0 <= i < n, else IndexError
    def set(self, i, leaf):
        if not 0 <= i < self.n:
            raise IndexError("set: needs 0 <= i < n")
        t, combine = self.t, self.combine
        k = self.cap + i
        t[k] = leaf
        k >>= 1
        while k:
            t[k] = t[2 * k] if t[2 * k + 1] is None else combine(t[2 * k], t[2 * k + 1])
            k >>= 1

    # combine of the leaves l..r; needs 0 <= l <= r < n, else IndexError
    def query(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError("query: needs 0 <= l <= r < n")
        t, combine = self.t, self.combine
        sl = sr = None
        l += self.cap
        r += self.cap + 1
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

    # The largest r in [l, n - 1] with ok(query(l, r)) true, or l - 1 if ok(query(l, l)) is false.
    # ok must be monotone: true for l..r means true for every shorter l..r'. Needs 0 <= l < n, else IndexError.
    def maxRight(self, l, ok):
        if not 0 <= l < self.n:
            raise IndexError("maxRight: needs 0 <= l < n")
        t, combine, cap = self.t, self.combine, self.cap
        k = l + cap
        sm = None
        while True:
            while k % 2 == 0:
                k >>= 1
            if t[k] is None:
                return self.n - 1  # only padding left: every real leaf fit
            nx = t[k] if sm is None else combine(sm, t[k])
            if not ok(nx):
                while k < cap:
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
        sm = None
        while True:
            k -= 1
            while k > 1 and k % 2:
                k >>= 1
            nx = t[k] if sm is None else combine(t[k], sm)
            if not ok(nx):
                while k < cap:
                    k = 2 * k + 1
                    nr = t[k] if sm is None else combine(t[k], sm)
                    if ok(nr):
                        sm = nr
                        k -= 1
                return k + 1 - cap
            sm = nx
            if k & -k == k:
                return 0
