# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-strided-static-sum/template.py
# @operations: stridedSum
# @data-structure-type: sqrt
# @complexities:
#   stridedSum: N
#   build: N
# @memory:
#   layout: none
#   node: sumPre[1*N]
#   tags: none
#   other: A[1*N]
#   note: the listed cost is a rebuild. Each op keeps one table, for the last step it saw; a repeat of that step is O(1) and a step above sqrt(N) walks, so sorting queries by step offline costs one rebuild per distinct step

# Static strided queries in linear memory: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
# (the last position used may be below r). Each op keeps a single table for the last step it saw, rebuilt when the
# step changes, so the expected use is offline: sort the queries by step, then ask them in that order. All indices
# 0-based, ranges inclusive.
from itertools import accumulate


class StridedQueries:
    # O(build) -- arr: the initial array
    def __init__(self, arr):
        self.A = list(arr)
        self.n = len(self.A)
        self.sumStep = 0  # the step the sum prefixes were built for
        self.sumPre = None

    # a[l] + a[l + step] + ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    # step; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedSum(self, l, r, step):
        if l < 0 or l > r or r >= self.n or step < 1:
            raise IndexError(f"stridedSum: needs 0 <= l <= r < n and step >= 1, got l={l}, r={r}, step={step}, n={self.n}")
        last = l + (r - l) // step * step
        count = (r - l) // step + 1
        if step != self.sumStep:
            if count <= 1024 or step * step > self.n:
                return sum(self.A[l:last + 1:step])
            self.sumStep = step
            self.sumPre = pre = list(self.A)
            for residue in range(min(step, self.n)):
                pre[residue::step] = list(accumulate(pre[residue::step]))
        pre = self.sumPre
        return pre[last] - pre[l - step] if l >= step else pre[last]
