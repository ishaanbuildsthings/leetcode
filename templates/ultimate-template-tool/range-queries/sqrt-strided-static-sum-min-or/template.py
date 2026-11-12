# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-strided-static-sum-min-or/template.py
# @operations: stridedMin stridedOrQuery stridedSum
# @data-structure-type: sqrt
# @complexities:
#   stridedMin: N*log(N)
#   stridedOrQuery: N*log(N)
#   stridedSum: N
#   build: N
# @memory:
#   layout: none
#   node: sumPre[1*N] minTable[1*N*log(N)] orTable[1*N*log(N)]
#   tags: none
#   other: A[1*N]
#   note: the listed cost is a rebuild. Each op keeps one table, for the last step it saw; a repeat of that step is O(1) and a step above sqrt(N) walks, so sorting queries by step offline costs one rebuild per distinct step

# Static strided queries in linear memory: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
# (the last position used may be below r). Each op keeps a single table for the last step it saw, rebuilt when the
# step changes, so the expected use is offline: sort the queries by step, then ask them in that order. All indices
# 0-based, ranges inclusive.
from itertools import accumulate
from functools import reduce
from operator import or_


class StridedQueries:
    # O(build) -- arr: the initial array
    def __init__(self, arr):
        self.A = list(arr)
        self.n = len(self.A)
        self.sumStep = 0  # the step the sum prefixes were built for
        self.sumPre = None
        self.minStep = 0  # the step the min table was built for
        self.minTable = None
        self.orStep = 0  # the step the or table was built for
        self.orTable = None

    # a[l] + a[l + step] + ..., up to at most r. O(1) when step is the last step this op built for, so ask queries
    # grouped by step; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedSum(self, l, r, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedSum: needs step >= 1, got step = {step}")
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

    # min of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries
    # grouped by step; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedMin(self, l, r, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedMin: needs step >= 1, got step = {step}")
        last = l + (r - l) // step * step
        count = (r - l) // step + 1
        if step != self.minStep:
            if count <= 1024 or step * step > self.n:
                return min(self.A[l:last + 1:step])
            self.minStep = step
            self.minTable = table = [self.A]
            jump = step
            while jump < self.n:
                previous = table[-1]
                table.append(list(map(min, previous, previous[jump:])) + previous[self.n - jump:])
                jump *= 2
        level = count.bit_length() - 1
        row = self.minTable[level]
        a, b = row[l], row[last - ((1 << level) - 1) * step]
        return a if a < b else b

    # a[l] | a[l + step] | ..., up to at most r. O(1) when step is the last step this op built for, so ask queries
    # grouped by step; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedOrQuery(self, l, r, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedOrQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedOrQuery: needs step >= 1, got step = {step}")
        last = l + (r - l) // step * step
        count = (r - l) // step + 1
        if step != self.orStep:
            if count <= 1024 or step * step > self.n:
                return reduce(or_, self.A[l:last + 1:step])
            self.orStep = step
            self.orTable = table = [self.A]
            jump = step
            while jump < self.n:
                previous = table[-1]
                table.append(list(map(or_, previous, previous[jump:])) + previous[self.n - jump:])
                jump *= 2
        level = count.bit_length() - 1
        row = self.orTable[level]
        a, b = row[l], row[last - ((1 << level) - 1) * step]
        return a | b
