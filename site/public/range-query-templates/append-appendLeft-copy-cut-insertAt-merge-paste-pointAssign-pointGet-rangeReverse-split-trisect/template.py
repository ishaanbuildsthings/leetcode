# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/append-appendLeft-copy-cut-insertAt-merge-paste-pointAssign-pointGet-rangeReverse-split-trisect/template.py
# @operations: append appendLeft copy cut getAll insertAt merge paste pointAssign pointGet rangeReverse split trisect
# @data-structure-type: persistent-treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   copy: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   merge: log(N) expected
#   paste: log(N) expected
#   pointAssign: log(N) expected
#   pointGet: log(N) expected
#   rangeReverse: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   build: N
# @memory:
#   layout: none
#   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)]
#   tags: rev[1*N*log(N)]
#   other: none
#   note: nodes are never changed or freed: each update copies O(log N) of them (N here counts updates too), and copies share every node they don't change; log(N) is of the length, which can be huge (long long)

# Persistent implicit treap: an array you can insert into anywhere, cut pieces out of (that is how to erase) and paste
# them back, reverse, and copy (copy(l, r): a[l..r] as a treap of its own, O(logN) however long, since the copy shares
# the same nodes; this one is unchanged), each in O(logN) expected. No node changes after it is made: updates copy the
# nodes on their paths, so a copy and its original never affect each other. Merge picks its root at random weighted by
# size, so shared nodes need no priorities. Lengths and indices are long long (copies pasted into each other double).
# All indices 0-based, ranges inclusive, always positions in the CURRENT array.
import random


class PersistentTreap:
    # one node pool shared by every PersistentTreap: cut / paste move nodes between them, so a piece from one can go
    # into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    # whole run), so there is nothing to reset between test cases
    val = [0]
    sz = [0]
    L = [0]
    R = [0]
    rev = [0]
    __slots__ = ("root",)

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr), 0, len(arr))

    def _empty(self):  # a new, empty PersistentTreap (on the same pool, like every one)
        return PersistentTreap()

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN) expected -- a[l..r] (leave out l and r: the whole array, O(1)) as a PersistentTreap of its own; this one
    # is unchanged. The copy shares this one's nodes, so it costs O(logN) however long it is
    def copy(self, l=0, r=None):
        if r is None:
            r = self.size() - 1
        piece = self._empty()
        piece.root = self.root if l == 0 and r == self.size() - 1 else self._cut(self.root, l, r)[1]
        return piece

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

    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
    def cut(self, l, r):
        a, b, c = self._cut(self.root, l, r)
        self.root = self._merge(a, c)
        piece = self._empty()
        piece.root = b
        return piece

    # O(logN) expected -- insert all of other (any PersistentTreap, e.g. a cut piece) so it starts at a[i]
    # (0 <= i <= size()); other is left empty
    def paste(self, i, other):
        x, y = self._split(self.root, i)
        self.root = self._merge(self._merge(x, other.root), y)
        other.root = 0

    # O(logN) expected -- append all of other at the end, leaving it empty (it must share this treap's nodes)
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(logN) expected -- (a[0..k-1], a[k..]) as two PersistentTreaps of their own; this one is left empty
    def split(self, k):
        left, right = self._empty(), self._empty()
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PersistentTreaps of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = self._empty(), self._empty(), self._empty()
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


# Example (pieces move between treaps; merge appends and leaves its argument empty):
#     t = PersistentTreap([1, 2, 3, 4, 5])
#     left, mid, right = t.trisect(1, 3)  # left = [1], mid = [2, 3, 4], right = [5]; t is empty now
#     t.merge(right)                      # t = [5]
#     t.merge(mid)                        # t = [5, 2, 3, 4]
#     t.merge(left)                       # t = [5, 2, 3, 4, 1]
