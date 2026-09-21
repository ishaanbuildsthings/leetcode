# two numbers A, B have the same remainder mod M if they differ by a multiple of M
# so we make an array of diffs
# for many numbers A, B, C, D ... to have the same remainder mod M, all their diffs must be a multiple of M
# we can take their diffs and get the GCD of the diffs to find this

import sys

# TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant

class SparseTable:
    def __init__(self, nums, combineFn):
        n = len(nums)
        log = [0] * (n + 1)
        for i in range(2, n + 1):
            log[i] = log[i // 2] + 1
        BITS = log[n] + 1
        sparse = [[None] * n for _ in range(BITS)]
        sparse[0][:] = nums
        for p in range(1, BITS):
            span = 1 << p
            half = span >> 1
            prev = sparse[p - 1]
            curr = sparse[p]
            for i in range(n - span + 1):
                curr[i] = combineFn(prev[i], prev[i + half])
        self.sparse = sparse
        self.log = log
        self.combineFn = combineFn

    def query(self, l, r):
        width = r - l + 1
        p = self.log[width]
        span = 1 << p
        row = self.sparse[p]
        return self.combineFn(row[l], row[r - span + 1])

import math
data = list(map(int, sys.stdin.read().strip().split()))
ptr = 0
t = data[ptr]
ptr += 1
cases = []
for _ in range(t):
    n = data[ptr]; q = data[ptr+1]; ptr += 2
    arr = data[ptr:ptr+n]; ptr += n
    queries = []
    for __ in range(q):
        l = data[ptr]; r = data[ptr+1]; ptr += 2
        queries.append((l, r))
    diffs = [abs(arr[i] - arr[i + 1]) for i in range(len(arr) - 1)]
    sparse = SparseTable(diffs, math.gcd)
    res = []
    for l, r in queries:
        if l == r:
            res.append(0)
            continue
        res.append(sparse.query(l-1, r-2))
    print(*res)
 