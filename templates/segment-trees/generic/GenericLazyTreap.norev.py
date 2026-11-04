# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericLazyTreap.norev.py

import random


# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple

# a pending update to every element of a segment, e.g. add
# We never need to worry about initializing empty tags or anything, these tags come in via rangeUpdate(l, r, tag) calls
# or when pushed down from parents
Tag = int


def leaf(v: RawVal) -> Node:
    # return (v, v, 1)  # (tot, mn, len)
    pass


def combine(left: Node, right: Node) -> Node:
    # return (left[0] + right[0], min(left[1], right[1]), left[2] + right[2])
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


class LazyTreap:
    _NO_TAG = object()  # a pending-tag slot with nothing pending (so any tag value works, None too)

    # one pool shared by every LazyTreap, so cut / paste move nodes between them (item 0 = the empty tree)
    _self, _agg, _L, _R, _sz, _pr, _lz = [None], [None], [0], [0], [0], [0], [_NO_TAG]

    def __init__(self, a, leaf, combine, apply, compose):
        self.leaf, self.combine, self.apply, self.compose = leaf, combine, apply, compose
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

    def _applyTag(self, t, tag):
        if t:
            LazyTreap._self[t] = self.apply(LazyTreap._self[t], tag)
            LazyTreap._agg[t] = self.apply(LazyTreap._agg[t], tag)
            lz = LazyTreap._lz
            lz[t] = tag if lz[t] is LazyTreap._NO_TAG else self.compose(lz[t], tag)

    def _push(self, t):
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

    # the node of items l..r of t: walks down and combines the pieces that cover them (no split / merge)
    def _rq(self, t, l, r):
        P = LazyTreap
        if l <= 0 and r >= P._sz[t] - 1:
            return P._agg[t]
        self._push(t)
        L, R = P._L[t], P._R[t]
        ls = P._sz[L]
        if r < ls:
            return self._rq(L, l, r)
        if l > ls:
            return self._rq(R, l - ls - 1, r - ls - 1)
        res = P._self[t]
        if l < ls:
            res = self.combine(self._rq(L, l, ls - 1), res)
        if r > ls:
            res = self.combine(res, self._rq(R, 0, r - ls - 1))
        return res

    # a[i] = val in t's subtree, recomputing the nodes on the way back up
    def _setAt(self, t, i, val):
        P = LazyTreap
        self._push(t)
        ls = P._sz[P._L[t]]
        if i < ls:
            self._setAt(P._L[t], i, val)
        elif i > ls:
            self._setAt(P._R[t], i - ls - 1, val)
        else:
            P._self[t] = self.leaf(val)
        self._pull(t)

    # tag applied to items l..r of t: tags the subtrees that cover them (no split / merge)
    def _updateRange(self, t, l, r, tag):
        P = LazyTreap
        if not t or r < 0 or l >= P._sz[t]:
            return
        if l <= 0 and r >= P._sz[t] - 1:
            self._applyTag(t, tag)
            return
        self._push(t)
        ls = P._sz[P._L[t]]
        self._updateRange(P._L[t], l, r, tag)
        if l <= ls <= r:
            P._self[t] = self.apply(P._self[t], tag)
        self._updateRange(P._R[t], l - ls - 1, r - ls - 1, tag)
        self._pull(t)

    def _three(self, l, r):
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    # the items of t as a LazyTreap of its own
    def _wrap(self, t):
        res = LazyTreap((), self.leaf, self.combine, self.apply, self.compose)
        res.root = t
        return res

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
        self._setAt(self.root, i, val)

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
        return self._rq(self.root, l, r)

    # the node of the whole array; needs size() >= 1, else IndexError
    def rangeQueryAll(self):
        if not self.root:
            raise IndexError("rangeQueryAll: needs size() >= 1")
        return LazyTreap._agg[self.root]

    # tag applied to every element of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeUpdate(self, l, r, tag):
        if not 0 <= l <= r < self.size():
            raise IndexError("rangeUpdate: needs 0 <= l <= r < size()")
        self._updateRange(self.root, l, r, tag)

    # remove a[l..r] and get it back as a LazyTreap of its own; needs 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError("cut: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        self.root = self._merge(a, c)
        return self._wrap(b)

    # insert all of other so it starts at a[i] (other ends up empty); needs 0 <= i <= size(), else IndexError
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError("paste: needs 0 <= i <= size()")
        a, b = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), b)
        other.root = 0

    # append all of other (other ends up empty)
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # (a[0..k-1], a[k..]) as two LazyTreaps (this one ends up empty); needs 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError("split: needs 0 <= k <= size()")
        a, b = self._split(self.root, k)
        self.root = 0
        return self._wrap(a), self._wrap(b)

    # (a[0..l-1], a[l..r], a[r+1..]) as three LazyTreaps (this one ends up empty); needs 0 <= l <= r < size(), else
    # IndexError
    def trisect(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError("trisect: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        self.root = 0
        return self._wrap(a), self._wrap(b), self._wrap(c)

    # cyclic shift a[l..r] left by k (a[l+k] moves to l; any k, taken mod r - l + 1); needs 0 <= l <= r < size(), else
    # IndexError
    def rangeRotateLeft(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError("rangeRotateLeft: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        b1, b2 = self._split(b, k % (r - l + 1))
        self.root = self._merge(self._merge(a, self._merge(b2, b1)), c)

    # cyclic shift a[l..r] right by k (a[r-k+1..r] move to the front; any k, taken mod r - l + 1); needs
    # 0 <= l <= r < size(), else IndexError
    def rangeRotateRight(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError("rangeRotateRight: needs 0 <= l <= r < size()")
        self.rangeRotateLeft(l, r, -k)
