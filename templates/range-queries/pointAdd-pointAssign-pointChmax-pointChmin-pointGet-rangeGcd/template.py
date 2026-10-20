# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeGcd/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(N)*log(U) ?
#   pointAssign: log(N)*log(U) ?
#   pointChmax: log(N)*log(U) ?
#   pointChmin: log(N)*log(U) ?
#   pointGet: 1
#   rangeGcd: log(N)+log(U) ?
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

    # Point OVERWRITE (not chmax/add): arr[index] becomes newVal.
    # Point overwrite: a[index] = newVal. Only updates the tree; the array you passed in is untouched.
    def pointAssign(self, index, newVal):
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

    # Inclusive range [l, r]. Requires l <= r. Returns 0 for an empty range.
    def rangeGcd(self, l, r):
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

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.tree[self.n + i]

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.tree[self.n + i]:
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.tree[self.n + i]:
            self.pointAssign(i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.tree[self.n + i] + delta)