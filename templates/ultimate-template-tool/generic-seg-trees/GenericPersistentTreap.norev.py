# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericPersistentTreap.norev.py

import random


# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


def leaf(v: RawVal) -> Node:
    # return (v, v)  # (tot, mn)
    pass


def combine(left: Node, right: Node) -> Node:
    # return (left[0] + right[0], min(left[1], right[1]))
    pass


# Every op copies the nodes it changes instead of changing them, so a copy and its original never affect each other.
# copy(l, r) is O(log N) however long a[l..r] is, so lengths can get huge (Python ints never overflow).
class PersistentTreap:
    # one pool shared by every PersistentTreap (item 0 = the empty tree); nodes are never freed
    _self, _agg, _L, _R, _sz = [None], [None], [0], [0], [0]

    def __init__(self, a, leaf, combine):
        self.leaf, self.combine = leaf, combine
        self.root = self._build(list(a), 0, len(a))

    def _new(self, v):
        node = self.leaf(v)
        P = PersistentTreap
        P._self.append(node)
        P._agg.append(node)
        P._L.append(0)
        P._R.append(0)
        P._sz.append(1)
        return len(P._L) - 1

    def _clone(self, t):
        P = PersistentTreap
        P._self.append(P._self[t])
        P._agg.append(P._agg[t])
        P._L.append(P._L[t])
        P._R.append(P._R[t])
        P._sz.append(P._sz[t])
        return len(P._L) - 1

    def _pull(self, t):
        P = PersistentTreap
        L, R, agg = P._L[t], P._R[t], P._agg
        P._sz[t] = 1 + P._sz[L] + P._sz[R]
        x = P._self[t]
        if L:
            x = self.combine(agg[L], x)
        if R:
            x = self.combine(x, agg[R])
        agg[t] = x

    # (first k items of t, the rest); t itself unchanged
    def _split(self, t, k):
        if not t:
            return 0, 0
        t = self._clone(t)
        P = PersistentTreap
        ls = P._sz[P._L[t]]
        if ls < k:
            a, b = self._split(P._R[t], k - ls - 1)
            P._R[t] = a
            self._pull(t)
            return t, b
        a, b = self._split(P._L[t], k)
        P._L[t] = b
        self._pull(t)
        return a, t

    # a's items, then b's; the root is a's with probability |a| / (|a| + |b|) (no priorities: a copy can hold the same
    # node many times)
    def _merge(self, a, b):
        if not a or not b:
            return a or b
        P = PersistentTreap
        if random.randrange(P._sz[a] + P._sz[b]) < P._sz[a]:
            a = self._clone(a)
            P._R[a] = self._merge(P._R[a], b)
            self._pull(a)
            return a
        b = self._clone(b)
        P._L[b] = self._merge(a, P._L[b])
        self._pull(b)
        return b

    def _build(self, a, lo, hi):
        if lo >= hi:
            return 0
        mid = (lo + hi) // 2
        t = self._new(a[mid])
        P = PersistentTreap
        P._L[t] = self._build(a, lo, mid)
        P._R[t] = self._build(a, mid + 1, hi)
        self._pull(t)
        return t

    # the node of items l..r of t (makes no copies)
    def _rq(self, t, l, r):
        P = PersistentTreap
        if l <= 0 and r >= P._sz[t] - 1:
            return P._agg[t]
        ls = P._sz[P._L[t]]
        res = None
        if l < ls:
            res = self._rq(P._L[t], l, min(r, ls - 1))
        if l <= ls <= r:
            res = P._self[t] if res is None else self.combine(res, P._self[t])
        if r > ls:
            s = self._rq(P._R[t], max(l - ls - 1, 0), r - ls - 1)
            res = s if res is None else self.combine(res, s)
        return res

    def _setAt(self, t, i, v):
        t = self._clone(t)
        P = PersistentTreap
        ls = P._sz[P._L[t]]
        if i < ls:
            P._L[t] = self._setAt(P._L[t], i, v)
        elif i > ls:
            P._R[t] = self._setAt(P._R[t], i - ls - 1, v)
        else:
            P._self[t] = self.leaf(v)
        self._pull(t)
        return t

    def _three(self, l, r):
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    # the items of t as a PersistentTreap of its own
    def _wrap(self, t):
        res = PersistentTreap((), self.leaf, self.combine)
        res.root = t
        return res

    # how many elements
    def size(self):
        return PersistentTreap._sz[self.root]

    # the node of a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError("pointGet: needs 0 <= i < size()")
        return self._rq(self.root, i, i)

    # a[i] = val; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.size():
            raise IndexError("pointAssign: needs 0 <= i < size()")
        self.root = self._setAt(self.root, i, val)

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
        return PersistentTreap._agg[self.root]

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

    # copy(): the whole array as a PersistentTreap of its own, O(1); copy(l, r): a[l..r] as one, O(log N) however
    # long. This one is unchanged either way. copy(l, r) needs 0 <= l <= r < size(), else IndexError
    def copy(self, l=None, r=None):
        if l is None and r is None:
            return self._wrap(self.root)
        if l is None or r is None or not 0 <= l <= r < self.size():
            raise IndexError("copy: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        return self._wrap(b)

    # remove a[l..r] and get it back as a PersistentTreap of its own; needs 0 <= l <= r < size(), else IndexError
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

    # (a[0..k-1], a[k..]) as two PersistentTreaps (this one ends up empty); needs 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError("split: needs 0 <= k <= size()")
        a, b = self._split(self.root, k)
        self.root = 0
        return self._wrap(a), self._wrap(b)

    # (a[0..l-1], a[l..r], a[r+1..]) as three PersistentTreaps (this one ends up empty); needs 0 <= l <= r < size(),
    # else IndexError
    def trisect(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError("trisect: needs 0 <= l <= r < size()")
        a, b, c = self._three(l, r)
        self.root = 0
        return self._wrap(a), self._wrap(b), self._wrap(c)
