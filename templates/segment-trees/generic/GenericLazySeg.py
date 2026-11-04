# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericLazySeg.py

# one raw array element: int, str, tuple, ...
RawVal = int
# e.g. (tot, mn, len): apply only sees the node, so keep the length; any value, tuples are fastest
Node = tuple
# a pending update to every element of a segment, e.g. add
Tag = int


def leaf(v: RawVal, i: int) -> Node:
    # return (v, v, 1)
    pass


# combine two nodes
def combine(left: Node, right: Node) -> Node:
    # return (left[0] + right[0], min(left[1], right[1]), left[2] + right[2])
    pass


# return a new node: this node after tag is applied to it
# we must handle the case where the tag is a no-op (e.g. negate twice), and we can return the original node
def apply(node: Node, tag: Tag) -> Node:
    # return (node[0] + tag * node[2], node[1] + tag, node[2])
    pass


# a tag that is the old tag, then the new tag
def compose(old: Tag, newer: Tag) -> Tag:
    # return old + newer
    pass


class LazySeg:
    _NO_TAG = object()  # a pending-tag slot with nothing pending (so any tag value works, None too)

    def __init__(self, a, leaf, combine, apply, compose):
        self.n = n = len(a)
        self.cap = cap = 1 << max(0, (n - 1).bit_length())
        self.lg = cap.bit_length() - 1
        self.leaf, self.combine, self.apply, self.compose = leaf, combine, apply, compose
        # None: a node over the padding past n only
        self.t = t = [None] * cap + [leaf(v, i) for i, v in enumerate(a)] + [None] * (cap - n)
        # lz[k]: the tag pending for node k's children
        self.lz = [LazySeg._NO_TAG] * cap
        for k in range(cap - 1, 0, -1):
            t[k] = t[2 * k] if t[2 * k + 1] is None else combine(t[2 * k], t[2 * k + 1])

    def _applyAt(self, k, tag):
        t = self.t
        if t[k] is None:
            return
        t[k] = self.apply(t[k], tag)
        if k < self.cap:
            lz = self.lz
            lz[k] = tag if lz[k] is LazySeg._NO_TAG else self.compose(lz[k], tag)

    def _push(self, k):
        tag = self.lz[k]
        if tag is not LazySeg._NO_TAG:
            self._applyAt(2 * k, tag)
            self._applyAt(2 * k + 1, tag)
            self.lz[k] = LazySeg._NO_TAG

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

    # how many elements
    def size(self):
        return self.n

    # the node of a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError("pointGet: needs 0 <= i < n")
        k = self.cap + i
        for j in range(self.lg, 0, -1):
            self._push(k >> j)
        return self.t[k]

    # a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError("pointAssign: needs 0 <= i < n")
        k = self.cap + i
        for j in range(self.lg, 0, -1):
            self._push(k >> j)
        self.t[k] = self.leaf(val, i)
        for j in range(1, self.lg + 1):
            self._pull(k >> j)

    # the node of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError("rangeQuery: needs 0 <= l <= r < n")
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

    # the node of the whole array; needs n >= 1, else IndexError
    def rangeQueryAll(self):
        if self.n == 0:
            raise IndexError("rangeQueryAll: needs n >= 1")
        return self.t[1]

    # tag applied to every element of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeUpdate(self, l, r, tag):
        if not 0 <= l <= r < self.n:
            raise IndexError("rangeUpdate: needs 0 <= l <= r < n")
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
