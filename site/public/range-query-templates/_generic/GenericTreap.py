# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericTreap.py

import random


# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


def leaf(v: RawVal) -> Node:
    # return (v, v, v)  # (tot, the best prefix sum, the best suffix sum)
    pass


def combine(left: Node, right: Node) -> Node:
    # return (left[0] + right[0], max(left[1], left[0] + right[1]), max(right[2], right[0] + left[2]))
    pass


# the node of the same segment read backwards
def reverse(node: Node) -> Node:
    # return (node[0], node[2], node[1])  # (read backwards, the best prefix is the best suffix)
    pass


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

    # the node of items l..r of t: walks down and combines the pieces that cover them (no split / merge)
    def _rq(self, t, l, r):
        P = Treap
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
        P = Treap
        self._push(t)
        ls = P._sz[P._L[t]]
        if i < ls:
            self._setAt(P._L[t], i, val)
        elif i > ls:
            self._setAt(P._R[t], i - ls - 1, val)
        else:
            P._self[t] = self.leaf(val)
        self._pull(t)

    def _three(self, l, r):
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    # the items of t as a Treap of its own
    def _wrap(self, t):
        res = Treap((), self.leaf, self.combine, self.reverse)
        res.root = t
        return res

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

    # (a[0..k-1], a[k..]) as two Treaps (this one ends up empty); needs 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError("split: needs 0 <= k <= size()")
        a, b = self._split(self.root, k)
        self.root = 0
        return self._wrap(a), self._wrap(b)

    # (a[0..l-1], a[l..r], a[r+1..]) as three Treaps (this one ends up empty); needs 0 <= l <= r < size(), else
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
