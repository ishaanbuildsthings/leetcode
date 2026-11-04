# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericSeg.py

# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


def leaf(v: RawVal, i: int) -> Node:
    # return (v, v)
    pass


def combine(left: Node, right: Node) -> Node:
    # return (left[0] + right[0], min(left[1], right[1]))
    pass


class Seg:
    def __init__(self, a, leaf, combine):
        self.n = n = len(a)
        self.cap = cap = 1 << max(0, (n - 1).bit_length())
        self.leaf, self.combine = leaf, combine
        # None: a node over the padding past n only
        self.t = t = [None] * cap + [leaf(v, i) for i, v in enumerate(a)] + [None] * (cap - n)
        for k in range(cap - 1, 0, -1):
            t[k] = t[2 * k] if t[2 * k + 1] is None else combine(t[2 * k], t[2 * k + 1])

    # how many elements
    def size(self):
        return self.n

    # the node of a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError("pointGet: needs 0 <= i < n")
        return self.t[self.cap + i]

    # a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError("pointAssign: needs 0 <= i < n")
        t, combine = self.t, self.combine
        k = self.cap + i
        t[k] = self.leaf(val, i)
        k >>= 1
        while k:
            t[k] = t[2 * k] if t[2 * k + 1] is None else combine(t[2 * k], t[2 * k + 1])
            k >>= 1

    # the node of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError("rangeQuery: needs 0 <= l <= r < n")
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

    # the node of the whole array; needs n >= 1, else IndexError
    def rangeQueryAll(self):
        if self.n == 0:
            raise IndexError("rangeQueryAll: needs n >= 1")
        return self.t[1]
