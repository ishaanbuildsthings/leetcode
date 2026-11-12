# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-static-and/template.py
# @operations: stridedAndQuery
# @data-structure-type: sqrt
# @complexities:
#   stridedAndQuery: N*log(N)
#   build: N
# @memory:
#   layout: none
#   node: andTable[1*N*log(N)]
#   tags: none
#   other: A[1*N]
#   note: the listed cost is a rebuild. Each op keeps one table, for the last step it saw; a repeat of that step is O(1) and a step above sqrt(N) walks, so sorting queries by step offline costs one rebuild per distinct step

# Static strided queries in linear memory: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
# (the last position used may be below r). Each op keeps a single table for the last step it saw, rebuilt when the
# step changes, so the expected use is offline: sort the queries by step, then ask them in that order. All indices
# 0-based, ranges inclusive.
from functools import reduce
from operator import and_


class StridedQueries:
    # O(build) -- arr: the initial array
    def __init__(self, arr):
        self.A = list(arr)
        self.n = len(self.A)
        self.andStep = 0  # the step the and table was built for
        self.andTable = None

    # a[l] & a[l + step] & ..., up to at most r. O(1) when step is the last step this op built for, so ask queries
    # grouped by step; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedAndQuery(self, l, r, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedAndQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedAndQuery: needs step >= 1, got step = {step}")
        last = l + (r - l) // step * step
        count = (r - l) // step + 1
        if step != self.andStep:
            if count <= 1024 or step * step > self.n:
                return reduce(and_, self.A[l:last + 1:step])
            self.andStep = step
            self.andTable = table = [self.A]
            jump = step
            while jump < self.n:
                previous = table[-1]
                table.append(list(map(and_, previous, previous[jump:])) + previous[self.n - jump:])
                jump *= 2
        level = count.bit_length() - 1
        row = self.andTable[level]
        a, b = row[l], row[last - ((1 << level) - 1) * step]
        return a & b
