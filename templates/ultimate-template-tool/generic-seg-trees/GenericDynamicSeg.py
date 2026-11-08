# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericDynamicSeg.py


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


# the node of lo..hi where nothing was ever set (every element the starting value, e.g. 0)
def blank(lo: int, hi: int) -> Node:
    # return (0, 0)
    pass


class DynamicSeg:
    # indices lo..hi (e.g. 0..10**18, negative is fine), every element starting as blank says; needs lo <= hi
    def __init__(self, lo, hi, leaf, combine, blank):
        if lo > hi:
            raise IndexError("DynamicSeg: needs lo <= hi")
        self.lo, self.hi = lo, hi
        self.leaf, self.combine, self.blank = leaf, combine, blank
        # children; 0 = never touched, every element there still the starting value
        self.t, self.L, self.R = [None, blank(lo, hi)], [0, 0], [0, 0]

    def _make(self, nl, nr):
        self.t.append(self.blank(nl, nr))
        self.L.append(0)
        self.R.append(0)
        return len(self.t) - 1

    def _at(self, k, nl, nr):
        return self.t[k] if k else self.blank(nl, nr)

    # a[i] = val; needs lo <= i <= hi, else IndexError
    def pointAssign(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError("pointAssign: needs lo <= i <= hi")
        L, R, t = self.L, self.R, self.t
        path = []
        k, nl, nr = 1, self.lo, self.hi
        while nl < nr:
            path.append((k, nl, nr))
            m = (nl + nr) // 2
            if i <= m:
                if not L[k]:
                    L[k] = self._make(nl, m)
                k, nr = L[k], m
            else:
                if not R[k]:
                    R[k] = self._make(m + 1, nr)
                k, nl = R[k], m + 1
        t[k] = self.leaf(val, i)
        for k, nl, nr in reversed(path):
            m = (nl + nr) // 2
            t[k] = self.combine(self._at(L[k], nl, m), self._at(R[k], m + 1, nr))

    def _query(self, k, nl, nr, l, r):
        if l <= nl and nr <= r:
            return self._at(k, nl, nr)
        if not k:
            return self.blank(max(l, nl), min(r, nr))
        m = (nl + nr) // 2
        if r <= m:
            return self._query(self.L[k], nl, m, l, r)
        if l > m:
            return self._query(self.R[k], m + 1, nr, l, r)
        return self.combine(self._query(self.L[k], nl, m, l, r), self._query(self.R[k], m + 1, nr, l, r))

    # the node of a[i]; needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.lo <= i <= self.hi:
            raise IndexError("pointGet: needs lo <= i <= hi")
        return self._query(1, self.lo, self.hi, i, i)

    # the node of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeQuery(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError("rangeQuery: needs lo <= l <= r <= hi")
        return self._query(1, self.lo, self.hi, l, r)

    # the node of the whole array
    def rangeQueryAll(self):
        return self.t[1]
