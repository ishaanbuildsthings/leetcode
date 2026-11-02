# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/append-appendLeft-concat-copyRange-cut-insertAt-paste-pointAssign-pointGet-rangeReverse-rangeSum-split-trisect/template.py
# @operations: append appendLeft concat copyRange cut getAll insertAt paste pointAssign pointGet rangeReverse rangeSum split trisect
# @data-structure-type: persistent-treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   concat: log(N) expected
#   copyRange: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   paste: log(N) expected
#   pointAssign: log(N) expected
#   pointGet: log(N) expected
#   rangeReverse: log(N) expected
#   rangeSum: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] sm[1*N*log(N)]
#   tags: rev[1*N*log(N)]
#   other: none
#   note: nodes are never changed or freed: each update copies O(log N) of them (N here counts updates too), and copies share every node they don't change

# Persistent implicit treap: an array you can insert into anywhere, cut pieces out of (that is how to erase) and paste
# them back, reverse, and copy ranges inside (copyRange: a copy of a[l..r] inserted at index i, O(logN) however long,
# since the copy shares the same nodes), each in O(logN) expected. No node changes after it is made: updates copy the
# nodes on their paths. Merge picks its root at random weighted by size, so shared nodes need no priorities. All
# indices 0-based, ranges inclusive, always positions in the CURRENT array.
import random


class PersistentTreap:
    __slots__ = ('root', 'val', 'sz', 'L', 'R', 'rev', 'sm')


    # O(N) -- arr: the initial array (may be empty); like: a PersistentTreap whose nodes this one shares, so pieces can
    # move between the two (pieces cut from it share them already). No reset between test cases
    def __init__(self, arr=(), like=None):
        if like is None:
            self.val, self.sz, self.L, self.R = [0], [0], [0], [0]  # node 0 = the empty tree
            self.rev = [0]
            self.sm = [0]
        else:
            self.val, self.sz, self.L, self.R = like.val, like.sz, like.L, like.R
            self.rev = like.rev
            self.sm = like.sm
        self.root = self._build(list(arr), 0, len(arr))

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN) expected -- insert a copy of a[l..r] so it starts at index i (0 <= i <= size(); i is in the array
    # before the copy goes in); the copy shares a[l..r]'s nodes
    def copyRange(self, l, r, i):
        _, b, _ = self._cut(self.root, l, r)
        x, y = self._split(self.root, i)
        self.root = self._merge(self._merge(x, b), y)

    # O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        x, y = self._split(self.root, i)
        self.root = self._merge(self._merge(x, self._new(v, 0, 0)), y)

    # O(logN) expected -- append v to the end
    def append(self, v):
        self.root = self._merge(self.root, self._new(v, 0, 0))

    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0; drop it to erase)
    def cut(self, l, r):
        a, b, c = self._cut(self.root, l, r)
        self.root = self._merge(a, c)
        piece = PersistentTreap(like=self)
        piece.root = b
        return piece

    # O(logN) expected -- insert other so it starts at a[i] (0 <= i <= size()), leaving it empty; it must share this
    # treap's nodes (a piece cut from it, or built with like=)
    def paste(self, i, other):
        x, y = self._split(self.root, i)
        self.root = self._merge(self._merge(x, other.root), y)
        other.root = 0

    # O(logN) expected -- append all of other at the end, leaving it empty (it must share this treap's nodes)
    def concat(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(logN) expected -- (a[0..k-1], a[k..]) as two PersistentTreaps of their own; this one is left empty
    def split(self, k):
        left, right = PersistentTreap(like=self), PersistentTreap(like=self)
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PersistentTreaps of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = PersistentTreap(like=self), PersistentTreap(like=self), PersistentTreap(like=self)
        left.root, mid.root, right.root = self._cut(self.root, l, r)
        self.root = 0
        return left, mid, right

    # O(logN) expected -- reverse a[l..r] in place
    def rangeReverse(self, l, r):
        a, b, c = self._cut(self.root, l, r)
        self.root = self._merge(self._merge(a, self._flip(b)), c)

    # O(logN) expected -- a[i] = v
    def pointAssign(self, i, v):
        a, b, c = self._cut(self.root, i, i)
        self.root = self._merge(self._merge(a, self._new(v, 0, 0)), c)

    # O(logN) expected -- a[i] (a read-only walk: pending reverses only swap which child is which)
    def pointGet(self, i):
        L, R, sz, rev, val = self.L, self.R, self.sz, self.rev, self.val
        t, flip = self.root, False
        while True:
            lt, rt = (R[t], L[t]) if flip else (L[t], R[t])
            flip ^= bool(rev[t])
            if i < sz[lt]:
                t = lt
            elif i == sz[lt]:
                return val[t]
            else:
                i -= sz[lt] + 1
                t = rt

    # O(logN) expected -- a[l] + ... + a[r] (the root doesn't change)
    def rangeSum(self, l, r):
        return self.sm[self._cut(self.root, l, r)[1]]

    # O(N) -- the whole current array
    def getAll(self):
        L, R, rev, val = self.L, self.R, self.rev, self.val
        out, stack, t, flip = [], [], self.root, False
        while stack or t:
            while t:  # (a subtree's flip: whether its children are swapped, from the reverses pending above it)
                stack.append((t, flip))
                lt = R[t] if flip else L[t]
                flip ^= bool(rev[t])
                t = lt
            t, flip = stack.pop()
            out.append(val[t])
            rt = L[t] if flip else R[t]
            flip ^= bool(rev[t])
            t = rt
        return out

    # ---- internals: every function returns new nodes and leaves its arguments as they were ----

    def _new(self, v, l, r, rv=0):
        self.val.append(v), self.L.append(l), self.R.append(r), self.rev.append(rv)
        self.sz.append(self.sz[l] + self.sz[r] + 1)
        self.sm.append(self.sm[l] + v + self.sm[r])
        return len(self.val) - 1

    def _flip(self, t):  # t reversed: a copy with its children swapped and a pending reverse for them
        return self._new(self.val[t], self.R[t], self.L[t], self.rev[t] ^ 1) if t else 0

    def _open(self, t):  # (value, left, right) of t with its pending reverse handed to (copies of) the children
        if self.rev[t]:
            return self.val[t], self._flip(self.L[t]), self._flip(self.R[t])
        return self.val[t], self.L[t], self.R[t]

    def _build(self, arr, lo, hi):  # a balanced tree of arr[lo:hi]
        if lo >= hi:
            return 0
        mid = (lo + hi) // 2
        return self._new(arr[mid], self._build(arr, lo, mid), self._build(arr, mid + 1, hi))

    def _split(self, t, k):  # (first k of t, the rest)
        if not t:
            return 0, 0
        v, l, r = self._open(t)
        if self.sz[l] >= k:
            a, b = self._split(l, k)
            return a, self._new(v, b, r)
        a, b = self._split(r, k - self.sz[l] - 1)
        return self._new(v, l, a), b

    def _merge(self, a, b):  # a's elements, then b's; the root is a with probability |a| / (|a| + |b|)
        if not a or not b:
            return a or b
        if random.randrange(self.sz[a] + self.sz[b]) < self.sz[a]:
            v, l, r = self._open(a)
            return self._new(v, l, self._merge(r, b))
        v, l, r = self._open(b)
        return self._new(v, self._merge(a, l), r)

    def _cut(self, t, l, r):  # (a[0..l-1], a[l..r], a[r+1..])
        a, b = self._split(t, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c
