# TEMPLATE BY https://github.com/agrawalishaan
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
    def updateAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
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

    # Inclusive range [l, r]. Requires l <= r. Returns 0 for an empty range.
    def query(self, l, r):
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