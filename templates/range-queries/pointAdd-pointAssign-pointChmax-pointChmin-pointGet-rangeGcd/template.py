# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeGcd/template.py
# @operations: gcdAll getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd
# @data-structure-type: seg-tree
# @complexities:
#   getAll: N
#   pointAdd: log(N)*log(U) ?
#   pointAssign: log(N)*log(U) ?
#   pointChmax: log(N)*log(U) ?
#   pointChmin: log(N)*log(U) ?
#   pointGet: 1
#   rangeGcd: log(N)+log(U) ?
#   gcdAll: log(N)+log(U) ?
#   build: N*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: tree[2*N]
#   tags: none
#   other: none
#   note: tree holds each node's gcd; arr is a reference
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/GcdSegTree.py

# You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

# GCD segment tree, bottom-up iterative.
# Build: O(n log(maxVal))
# Space: O(2n)
# Query/Update: O(log N) gcd calls
# Uses 0 as the identity, so gcd(0, x) == x. A stored 0 means "contributes nothing".

from math import gcd

class GcdSegmentTree:
    def __init__(self, arr):
        self.n = n = len(arr)
        self.arr = arr
        tree = [0] * (2 * n)
        tree[n:2 * n] = arr
        for i in range(n - 1, 0, -1):
            tree[i] = gcd(tree[2 * i], tree[2 * i + 1])
        self.tree = tree

    ################ PUBLIC METHODS START HERE ################

    # Point OVERWRITE (not chmax/add): arr[index] becomes newVal. Point overwrite: a[index] = newVal. Only updates the
    # tree; the array you passed in is untouched.; needs 0 <= index < n, else IndexError
    def pointAssign(self, index, newVal):
        if not 0 <= index < self.n:
            raise IndexError(f"pointAssign: needs 0 <= index < n, got index = {index}, n = {self.n}")
        tree = self.tree
        i = index + self.n
        tree[i] = newVal
        i >>= 1
        while i:
            v = gcd(tree[2 * i], tree[2 * i + 1])
            if tree[i] == v:
                break
            tree[i] = v
            i >>= 1

    # Same as pointAssign, but also writes newVal into the array you passed in.
    def pointAssignAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        self.pointAssign(index, newVal)

    # Inclusive range [l, r]. Requires l <= r. Returns 0 for an empty range.; needs 0 <= l <= r < n, else IndexError
    def rangeGcd(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeGcd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        tree = self.tree
        res = 0
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                res = gcd(res, tree[l]); l += 1
            if r & 1:
                r -= 1; res = gcd(res, tree[r])
            l >>= 1; r >>= 1
        return res

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.tree[self.n + i]

    # O(N) -- the whole array (a copy of the leaves)
    def getAll(self):
        return self.tree[self.n:]

    # a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.tree[self.n + i]:
            self.pointAssign(i, val)

    # a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.tree[self.n + i]:
            self.pointAssign(i, val)

    # a[i] += delta; needs needs 0 <= i < n, else IndexError, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")

    # O(log(N)+log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else raises IndexError
    def gcdAll(self):
        if self.n < 1:
            raise IndexError("gcdAll: needs n >= 1")
        return self.rangeGcd(0, self.n - 1)
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.tree[self.n + i] + delta)