# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-prefix-sum/template.py
# @operations: stridedSum
# @data-structure-type: sqrt
# @complexities:
#   stridedSum: sqrt(N)
#   build: 1*N*sqrt(N)
# @memory:
#   layout: none
#   node: sumPre[1*N*sqrt(N)]
#   tags: none
#   other: A[1*N]
#   note: O(1) for a step up to the cutoff, sqrt(N) only for a bigger one. The default cutoff is about 90 million values at N = 2e5, so pass a lower one when memory is tight

# Static strided queries, every small stride's prefix array built up front: each query covers a[l], a[l + step],
# a[l + 2 * step], ... up to at most r (the last position used may be below r). All indices 0-based, ranges inclusive.
from itertools import accumulate
from math import sqrt


class StridedQueries:
    # O(build) -- arr: the initial array. cutoff: prefix arrays are kept for steps up to it; leave it out for sqrt(n),
    # and lower it when memory is tight (each kept step costs n values)
    def __init__(self, arr, cutoff=None):
        self.A = A = list(arr)
        self.n = n = len(A)
        self.strides = cutoff if cutoff is not None else min(n, max(1, int(sqrt(n))))
        if not 0 <= self.strides <= n:
            raise IndexError(f"StridedQueries: needs 0 <= cutoff <= n, got cutoff={cutoff}, n={n}")
        self.sumPre = [None] * (self.strides + 1)
        for step in range(1, self.strides + 1):
            pre = list(A)
            for residue in range(step):
                pre[residue::step] = list(accumulate(pre[residue::step]))
            self.sumPre[step] = pre

    # a[l] + a[l + step] + ..., up to at most r. O(1) for a kept step; needs 0 <= l <= r < n and step >= 1, else raises
    # IndexError
    def stridedSum(self, l, r, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedSum: needs step >= 1, got step = {step}")
        last = l + (r - l) // step * step
        if step > self.strides:
            return sum(self.A[l:last + 1:step])
        pre = self.sumPre[step]
        return pre[last] - pre[l - step] if l >= step else pre[last]
