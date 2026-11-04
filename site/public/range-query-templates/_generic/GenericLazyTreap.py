# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericLazyTreap.py

import random


# one raw array element: int, str, tuple, ...
RawVal = int
# e.g. (tot, mn, len): apply only sees the node, so keep the length; any value, tuples are fastest
Node = tuple
# a pending update to every element of a segment, e.g. add
Tag = int


def leaf(v: RawVal) -> Node:
    # return (v, v, 1)
    pass


# combine two nodes
def combine(left: Node, right: Node) -> Node:
    # return (left[0] + right[0], min(left[1], right[1]), left[2] + right[2])
    pass


# the node of the same segment read backwards (only rangeReverse uses it; for sums / mins it's node itself)
def reverse(node: Node) -> Node:
    # return (node[0], node[2], node[1])  # e.g. swap pre and suf
    return node


# return a new node: this node after tag is applied to it
# we must handle the case where the tag is a no-op (e.g. negate twice), and we can return the original node
def apply(node: Node, tag: Tag) -> Node:
    # return (node[0] + tag * node[2], node[1] + tag, node[2])
    pass


# a tag that is the old tag, then the new tag
def compose(old: Tag, newer: Tag) -> Tag:
    # return old + newer
    pass


class LazyTreap:
    _NO_TAG = object()  # a pending-tag slot with nothing pending (so any tag value works, None too)

    # one pool shared by every LazyTreap, so cut / paste move nodes between them (item 0 = the empty tree)
    _self, _agg, _L, _R, _sz, _pr, _rev, _lz = [None], [None], [0], [0], [0], [0], [False], [_NO_TAG]

    # reverse is only needed for rangeReverse
    def __init__(self, a, leaf, combine, apply, compose, reverse=lambda node: node):
        self.leaf, self.combine, self.apply, self.compose, self.reverse = leaf, combine, apply, compose, reverse
        L, R, pr = LazyTreap._L, LazyTreap._R, LazyTreap._pr
        st = []
        for v in a:
            x = self._new(v)
            last = 0
            while st and pr[st[-1]] < pr[x]:
                last = st.pop()
            L[x] = last
            if st:
                R[st[-1]] = x
            st.append(x)
        self.root = st[0] if st else 0
        # pull children before parents: the reverse of a preorder
        order = [self.root] if self.root else []
        for t in order:
            if L[t]:
                order.append(L[t])
            if R[t]:
                order.append(R[t])
        for t in reversed(order):
            self._pull(t)

    def _new(self, v):
        node = self.leaf(v)
        LazyTreap._self.append(node)
        LazyTreap._agg.append(node)
        LazyTreap._L.append(0)
        LazyTreap._R.append(0)
        LazyTreap._sz.append(1)
        LazyTreap._pr.append(random.random())
        LazyTreap._rev.append(False)
        LazyTreap._lz.append(LazyTreap._NO_TAG)
        return len(LazyTreap._L) - 1

    def _pull(self, t):
        L, R, agg = LazyTreap._L[t], LazyTreap._R[t], LazyTreap._agg
        LazyTreap._sz[t] = 1 + LazyTreap._sz[L] + LazyTreap._sz[R]
        x = LazyTreap._self[t]
        if L:
            x = self.combine(agg[L], x)
        if R:
            x = self.combine(x, agg[R])
        agg[t] = x

    def _flip(self, t):
        if t:
            LazyTreap._L[t], LazyTreap._R[t] = LazyTreap._R[t], LazyTreap._L[t]
            LazyTreap._agg[t] = self.reverse(LazyTreap._agg[t])
            LazyTreap._rev[t] = not LazyTreap._rev[t]

    def _applyTag(self, t, tag):
        if t:
            LazyTreap._self[t] = self.apply(LazyTreap._self[t], tag)
            LazyTreap._agg[t] = self.apply(LazyTreap._agg[t], tag)
            lz = LazyTreap._lz
            lz[t] = tag if lz[t] is LazyTreap._NO_TAG else self.compose(lz[t], tag)

    def _push(self, t):
        if LazyTreap._rev[t]:
            self._flip(LazyTreap._L[t])
            self._flip(LazyTreap._R[t])
            LazyTreap._rev[t] = False
        tag = LazyTreap._lz[t]
        if tag is not LazyTreap._NO_TAG:
            self._applyTag(LazyTreap._L[t], tag)
            self._applyTag(LazyTreap._R[t], tag)
            LazyTreap._lz[t] = LazyTreap._NO_TAG

    # (first k items of t, the rest)
    def _split(self, t, k):
        if not t:
            return 0, 0
        self._push(t)
        L, R, sz = LazyTreap._L, LazyTreap._R, LazyTreap._sz
        if sz[L[t]] < k:
            a, b = self._split(R[t], k - sz[L[t]] - 1)
            R[t] = a
            self._pull(t)
            return t, b
        a, b = self._split(L[t], k)
        L[t] = b
        self._pull(t)
        return a, t

    def _merge(self, a, b):
        if not a or not b:
            return a or b
        if LazyTreap._pr[a] > LazyTreap._pr[b]:
            self._push(a)
            LazyTreap._R[a] = self._merge(LazyTreap._R[a], b)
            self._pull(a)
            return a
        self._push(b)
        LazyTreap._L[b] = self._merge(a, LazyTreap._L[b])
        self._pull(b)
        return b

    def _three(self, l, r):
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    # how many elements
    def size(self):
        return LazyTreap._sz[self.root]

    # the node of a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError("pointGet: needs 0 <= i < size()")
        L, R, sz = LazyTreap._L, LazyTreap._R, LazyTreap._sz
        t = self.root
        while True:
            self._push(t)
            ls = sz[L[t]]
            if i < ls:
                t = L[t]
            elif i == ls:
                return LazyTreap._self[t]
            else:
                i -= ls + 1
                t = R[t]

    # a[i] = val; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.size():
            raise IndexError("pointAssign: needs 0 <= i < size()")
        a, b, c = self._three(i, i)
        LazyTreap._self[b] = self.leaf(val)
        self._pull(b)
        self.root = self._merge(self._merge(a, b), c)

    # insert val so it becomes a[i] (i = size() appends); needs 0 <= i <= size(), else IndexError
    def insertAt(self, i, val):
        if not 0 <= i <= self.size():
            raise IndexError("insertAt: needs 0 <= i <= size()")
        a, b = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._new(val)), b)

    def append(self, val):
        self.root = self._merge(self.root, self._new(val))

    # remove a[i]; needs 0 <= i < size(), else IndexError
    def eraseAt(self, i):
        if not 0 <= i < self.size():
            raise IndexError("eraseAt: needs 0 <= i < size()")
        a, b, c = self._three(i, i)
        self.root = self._merge(a, c)

    # the node of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeQuery(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError("rangeQuery: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        res = LazyTreap._agg[b]
        self.root = self._merge(self._merge(a, b), c)
        return res

    # the node of the whole array; needs size() >= 1, else IndexError
    def rangeQueryAll(self):
        if not self.root:
            raise IndexError("rangeQueryAll: needs size() >= 1")
        return LazyTreap._agg[self.root]

    # tag applied to every element of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeUpdate(self, l, r, tag):
        if not 0 <= l <= r < self.size():
            raise IndexError("rangeUpdate: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        self._applyTag(b, tag)
        self.root = self._merge(self._merge(a, b), c)

    # reverse a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeReverse(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError("rangeReverse: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        self._flip(b)
        self.root = self._merge(self._merge(a, b), c)

    # remove a[l..r] and get it back as a LazyTreap of its own; needs 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError("cut: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        self.root = self._merge(a, c)
        piece = LazyTreap((), self.leaf, self.combine, self.apply, self.compose, self.reverse)
        piece.root = b
        return piece

    # insert all of other so it starts at a[i] (other ends up empty); needs 0 <= i <= size(), else IndexError
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError("paste: needs 0 <= i <= size()")
        a, b = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), b)
        other.root = 0
