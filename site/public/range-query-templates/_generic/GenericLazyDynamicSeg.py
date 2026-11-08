# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericLazyDynamicSeg.py


# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple

# a pending update to every element of a segment, e.g. add
# We never need to worry about initializing empty tags or anything, these tags come in via rangeUpdate(l, r, tag) calls
# or when pushed down from parents
Tag = int


def leaf(v: RawVal, i: int) -> Node:
    # return (v, v, 1)
    pass


def combine(left: Node, right: Node) -> Node:
    # return (left[0] + right[0], min(left[1], right[1]), left[2] + right[2])
    pass


# the node of lo..hi where nothing was ever set (every element the starting value, e.g. 0)
def blank(lo: int, hi: int) -> Node:
    # return (0, 0, hi - lo + 1)
    pass


# return a new node: this node after tag is applied to it
# this function is never called with a tag that never existed, but tags can have things like pending false values or
# pending no-ops (for instance two lazy bools canceling) and we still need to check for this and no-op (could just
# return original node)
def apply(node: Node, tag: Tag) -> Node:
    # return (node[0] + tag * node[2], node[1] + tag, node[2])
    pass


# a tag that is the old tag, then the new tag
def compose(old: Tag, newer: Tag) -> Tag:
    # return old + newer
    pass


class LazyDynamicSeg:
    _NO_TAG = object()  # a pending-tag slot with nothing pending (so any tag value works, None too)

    # indices lo..hi (e.g. 0..10**18, negative is fine), every element starting as blank says; needs lo <= hi
    def __init__(self, lo, hi, leaf, combine, blank, apply, compose):
        if lo > hi:
            raise IndexError("LazyDynamicSeg: needs lo <= hi")
        self.lo, self.hi = lo, hi
        self.leaf, self.combine, self.blank, self.apply, self.compose = leaf, combine, blank, apply, compose
        # children; 0 = never touched, every element there still the starting value
        self.t, self.L, self.R = [None, blank(lo, hi)], [0, 0], [0, 0]
        # lz[k]: the tag pending for node k's children
        self.lz = [LazyDynamicSeg._NO_TAG, LazyDynamicSeg._NO_TAG]

    def _make(self, nl, nr):
        self.t.append(self.blank(nl, nr))
        self.L.append(0)
        self.R.append(0)
        self.lz.append(LazyDynamicSeg._NO_TAG)
        return len(self.t) - 1

    def _applyAt(self, k, tag):
        self.t[k] = self.apply(self.t[k], tag)
        lz = self.lz
        lz[k] = tag if lz[k] is LazyDynamicSeg._NO_TAG else self.compose(lz[k], tag)

    # hands node k's pending tag to its children (making them if they were never touched)
    def _push(self, k, nl, nr):
        tag = self.lz[k]
        if tag is LazyDynamicSeg._NO_TAG:
            return
        m = (nl + nr) // 2
        if not self.L[k]:
            self.L[k] = self._make(nl, m)
        if not self.R[k]:
            self.R[k] = self._make(m + 1, nr)
        self._applyAt(self.L[k], tag)
        self._applyAt(self.R[k], tag)
        self.lz[k] = LazyDynamicSeg._NO_TAG

    def _pull(self, k, nl, nr):
        m = (nl + nr) // 2
        self.t[k] = self.combine(self._at(self.L[k], nl, m), self._at(self.R[k], m + 1, nr))

    def _update(self, k, nl, nr, l, r, tag):
        if l <= nl and nr <= r:
            self._applyAt(k, tag)
            return
        self._push(k, nl, nr)
        m = (nl + nr) // 2
        if l <= m:
            if not self.L[k]:
                self.L[k] = self._make(nl, m)
            self._update(self.L[k], nl, m, l, r, tag)
        if r > m:
            if not self.R[k]:
                self.R[k] = self._make(m + 1, nr)
            self._update(self.R[k], m + 1, nr, l, r, tag)
        self._pull(k, nl, nr)

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
            self._push(k, nl, nr)
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
            self._pull(k, nl, nr)

    def _query(self, k, nl, nr, l, r):
        if l <= nl and nr <= r:
            return self._at(k, nl, nr)
        if not k:
            return self.blank(max(l, nl), min(r, nr))
        self._push(k, nl, nr)
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

    # tag applied to every element of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeUpdate(self, l, r, tag):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError("rangeUpdate: needs lo <= l <= r <= hi")
        self._update(1, self.lo, self.hi, l, r, tag)
