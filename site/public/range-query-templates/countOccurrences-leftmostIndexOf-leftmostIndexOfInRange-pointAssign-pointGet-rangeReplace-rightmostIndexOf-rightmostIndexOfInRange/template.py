# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange/template.py
# @operations: countOccurrences getAll leftmostIndexOf leftmostIndexOfInRange pointAssign pointGet rangeReplace rightmostIndexOf rightmostIndexOfInRange
# @data-structure-type: position-trees
# @letters: same
# @complexities:
#   countOccurrences: log(N)
#   getAll: N*log(N)
#   leftmostIndexOf: log(N)
#   leftmostIndexOfInRange: log(N)
#   pointAssign: log(N) amortized
#   pointGet: log(N)
#   rangeReplace: log(N) amortized
#   rightmostIndexOf: log(N)
#   rightmostIndexOfInRange: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: L[1*N*log(N)] R[1*N*log(N)] C[1*N*log(N)] P[1*N*log(N)] W[1*N*log(N)]
#   tags: none
#   other: roots[1*N] vals[1*N] leaf[1*N]
#   note: one dynamic seg tree over the positions per distinct value; at most about N log N nodes live at once (freed nodes are reused); values are hashed, so any values work

# One seg tree over the positions per value (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r]
# into y in O(log N) amortized, for any values. Each distinct value keeps a seg tree over 0..n-1 holding the positions
# where it is; a change splits x's tree at [l, r] (O(log N) new nodes) and merges the cut part into y's tree (each
# step of a merge frees a node, so merges cost O(log N) amortized over the whole run). Also: where x first / last
# appears (in a range), how many times x appears in a range, a[i] and a[i] = v. All indices 0-based, ranges inclusive
# [l, r]; searches return -1 when nothing qualifies.

from random import getrandbits


class PositionTrees:
    # node 0 = the empty tree; L / R: children, C: how many positions below, P: parent, W: which value (at roots)
    __slots__ = ("n", "L", "R", "C", "P", "W", "leaf", "ids", "vals", "roots", "free")
    salt = getrandbits(62)  # ids' int keys are salted with this, so no fixed input can make them collide

    # O(N log N) -- arr: the initial array (a list)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.L, self.R = [0], [0]
        self.C = [0]
        self.P, self.W, self.leaf = [0], [0], [0] * n
        self.ids, self.vals, self.roots, self.free = {}, [], [], []
        for i, v in enumerate(arr):
            k = self._id(v)
            self.roots[k] = self._insert(self.roots[k], i)
        for k, t in enumerate(self.roots):
            self.W[t] = k

    # O(1) -- the length of the array
    def size(self):
        return self.n

    # O(logN) amortized -- every a[i] == x with l <= i <= r becomes y; needs 0 <= l <= r < size(), else IndexError
    def rangeReplace(self, l, r, x, y):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeReplace: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        if k is not None and x != y:
            self._move(k, l, r, y)

    # O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        return self._count(self.roots[k], 0, self.n - 1, l, r) if k is not None else 0

    # O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        t = self.roots[k] if k is not None else 0
        if not t:
            return -1
        L, R, lo, hi = self.L, self.R, 0, self.n - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            if L[t]:
                t, hi = L[t], mid
            else:
                t, lo = R[t], mid + 1
        return lo

    # O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        t = self.roots[k] if k is not None else 0
        if not t:
            return -1
        L, R, lo, hi = self.L, self.R, 0, self.n - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            if R[t]:
                t, lo = R[t], mid + 1
            else:
                t, hi = L[t], mid
        return lo

    # O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        return self._first(self.roots[k], 0, self.n - 1, l, r, True) if k is not None else -1

    # O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        return self._first(self.roots[k], 0, self.n - 1, l, r, False) if k is not None else -1

    # O(logN) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        return self.vals[self._owner(i)]

    # O(logN) amortized -- a[i] = v; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        k = self._owner(i)
        if self.vals[k] != v:
            self._move(k, i, i, v)

    # O(N log N) -- the whole current array
    def getAll(self):
        out, L, R = [None] * self.n, self.L, self.R
        for k, t in enumerate(self.roots):
            if not t:
                continue
            v, stack = self.vals[k], [(t, 0, self.n - 1)]
            while stack:
                t, lo, hi = stack.pop()
                if lo == hi:
                    out[lo] = v
                    continue
                mid = (lo + hi) >> 1
                if L[t]:
                    stack.append((L[t], lo, mid))
                if R[t]:
                    stack.append((R[t], mid + 1, hi))
        return out

    # ---- internals ----

    def _id(self, v):  # v's index into vals / roots (a new one, with an empty tree, the first time v is seen)
        key = v ^ self.salt if type(v) is int else v
        k = self.ids.get(key)
        if k is None:
            k = self.ids[key] = len(self.vals)
            self.vals.append(v)
            self.roots.append(0)
        return k

    def _new(self):  # an empty node (a freed one if there is one)
        if self.free:
            x = self.free.pop()
            self.L[x] = self.R[x] = 0
            return x
        self.L.append(0)
        self.R.append(0)
        self.C.append(0)
        self.P.append(0)
        self.W.append(0)
        return len(self.L) - 1

    def _pull(self, x):  # recompute x from its children
        l, r = self.L[x], self.R[x]
        self.C[x] = self.C[l] + self.C[r]
        self.P[l] = self.P[r] = x
        return x

    def _insert(self, t, i):  # t's tree with position i (not in it) added; returns the root
        root = t = t or self._new()
        L, R, lo, hi = self.L, self.R, 0, self.n - 1
        while True:
            self.C[t] += 1
            if lo == hi:
                self.leaf[i] = t
                return root
            mid = (lo + hi) >> 1
            if i <= mid:
                if not L[t]:
                    c = self._new()
                    L[t] = c
                    self.P[c] = t
                t, hi = L[t], mid
            else:
                if not R[t]:
                    c = self._new()
                    R[t] = c
                    self.P[c] = t
                t, lo = R[t], mid + 1

    def _split(self, t, lo, hi, l, r):  # (t without the positions in [l, r], a tree of just those); no empty nodes left
        if not t or r < lo or hi < l:
            return t, 0
        if l <= lo and hi <= r:
            return 0, t
        L, R, mid = self.L, self.R, (lo + hi) >> 1
        a1, b1 = self._split(L[t], lo, mid, l, r)
        a2, b2 = self._split(R[t], mid + 1, hi, l, r)
        cut = 0
        if b1 or b2:
            cut = self._new()
            L[cut], R[cut] = b1, b2
            self._pull(cut)
        if a1 or a2:
            L[t], R[t] = a1, a2
            return self._pull(t), cut
        self.free.append(t)
        return 0, cut

    def _merge(self, a, b):  # the union of two trees over disjoint positions; b's nodes that overlap a's are freed
        if not a or not b:
            return a or b
        L, R = self.L, self.R
        L[a] = self._merge(L[a], L[b])
        R[a] = self._merge(R[a], R[b])
        self.free.append(b)
        return self._pull(a)

    def _move(self, k, l, r, y):  # the positions in [l, r] of vals[k]'s tree go to y's
        keep, cut = self._split(self.roots[k], 0, self.n - 1, l, r)
        self.roots[k] = keep
        if cut:
            ky = self._id(y)
            t = self.roots[ky] = self._merge(self.roots[ky], cut)
            self.P[t], self.W[t] = 0, ky

    def _count(self, t, lo, hi, l, r):
        if not t or r < lo or hi < l:
            return 0
        if l <= lo and hi <= r:
            return self.C[t]
        mid = (lo + hi) >> 1
        return self._count(self.L[t], lo, mid, l, r) + self._count(self.R[t], mid + 1, hi, l, r)

    def _first(self, t, lo, hi, l, r, left):  # the first (left) / last position of t's tree in [l, r], or -1
        if not t or r < lo or hi < l:
            return -1
        if lo == hi:
            return lo
        mid = (lo + hi) >> 1
        a, b = (self.L[t], self.R[t]) if left else (self.R[t], self.L[t])
        alo, ahi, blo, bhi = (lo, mid, mid + 1, hi) if left else (mid + 1, hi, lo, mid)
        res = self._first(a, alo, ahi, l, r, left)
        return res if res != -1 else self._first(b, blo, bhi, l, r, left)

    def _owner(self, i):  # the index into vals of a[i]'s value: up from i's leaf to its tree's root
        P, t = self.P, self.leaf[i]
        while P[t]:
            t = P[t]
        return self.W[t]
