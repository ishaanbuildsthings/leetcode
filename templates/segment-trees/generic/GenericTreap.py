# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericTreap.py

import random


# one raw array element: int, str, tuple, ...
RawVal = int
# e.g. (tot, mn); any value, tuples are fastest
Node = tuple


def leaf(v: RawVal) -> Node:
    # return (v, v)
    pass


# combine two nodes
def combine(left: Node, right: Node) -> Node:
    # return (left[0] + right[0], min(left[1], right[1]))
    pass


# the node of the same segment read backwards (only rangeReverse uses it; for sums / mins it's node itself)
def reverse(node: Node) -> Node:
    # return (node[0], node[2], node[1])  # e.g. swap pre and suf
    return node


class Treap:
    # one pool shared by every Treap, so cut / paste move nodes between them (item 0 = the empty tree)
    _self, _agg, _L, _R, _sz, _pr, _rev = [None], [None], [0], [0], [0], [0], [False]

    # reverse is only needed for rangeReverse
    def __init__(self, a, leaf, combine, reverse=lambda node: node):
        self.leaf, self.combine, self.reverse = leaf, combine, reverse
        L, R, pr = Treap._L, Treap._R, Treap._pr
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
        Treap._self.append(node)
        Treap._agg.append(node)
        Treap._L.append(0)
        Treap._R.append(0)
        Treap._sz.append(1)
        Treap._pr.append(random.random())
        Treap._rev.append(False)
        return len(Treap._L) - 1

    def _pull(self, t):
        L, R, agg = Treap._L[t], Treap._R[t], Treap._agg
        Treap._sz[t] = 1 + Treap._sz[L] + Treap._sz[R]
        x = Treap._self[t]
        if L:
            x = self.combine(agg[L], x)
        if R:
            x = self.combine(x, agg[R])
        agg[t] = x

    def _flip(self, t):
        if t:
            Treap._L[t], Treap._R[t] = Treap._R[t], Treap._L[t]
            Treap._agg[t] = self.reverse(Treap._agg[t])
            Treap._rev[t] = not Treap._rev[t]

    def _push(self, t):
        if Treap._rev[t]:
            self._flip(Treap._L[t])
            self._flip(Treap._R[t])
            Treap._rev[t] = False

    # (first k items of t, the rest)
    def _split(self, t, k):
        if not t:
            return 0, 0
        self._push(t)
        L, R, sz = Treap._L, Treap._R, Treap._sz
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
        if Treap._pr[a] > Treap._pr[b]:
            self._push(a)
            Treap._R[a] = self._merge(Treap._R[a], b)
            self._pull(a)
            return a
        self._push(b)
        Treap._L[b] = self._merge(a, Treap._L[b])
        self._pull(b)
        return b

    def _three(self, l, r):
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    # how many elements
    def size(self):
        return Treap._sz[self.root]

    # the node of a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError("pointGet: needs 0 <= i < size()")
        L, R, sz = Treap._L, Treap._R, Treap._sz
        t = self.root
        while True:
            self._push(t)
            ls = sz[L[t]]
            if i < ls:
                t = L[t]
            elif i == ls:
                return Treap._self[t]
            else:
                i -= ls + 1
                t = R[t]

    # a[i] = val; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.size():
            raise IndexError("pointAssign: needs 0 <= i < size()")
        a, b, c = self._three(i, i)
        Treap._self[b] = self.leaf(val)
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
        res = Treap._agg[b]
        self.root = self._merge(self._merge(a, b), c)
        return res

    # the node of the whole array; needs size() >= 1, else IndexError
    def rangeQueryAll(self):
        if not self.root:
            raise IndexError("rangeQueryAll: needs size() >= 1")
        return Treap._agg[self.root]

    # reverse a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeReverse(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError("rangeReverse: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        self._flip(b)
        self.root = self._merge(self._merge(a, b), c)

    # remove a[l..r] and get it back as a Treap of its own; needs 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError("cut: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        self.root = self._merge(a, c)
        piece = Treap((), self.leaf, self.combine, self.reverse)
        piece.root = b
        return piece

    # insert all of other so it starts at a[i] (other ends up empty); needs 0 <= i <= size(), else IndexError
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError("paste: needs 0 <= i <= size()")
        a, b = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), b)
        other.root = 0
