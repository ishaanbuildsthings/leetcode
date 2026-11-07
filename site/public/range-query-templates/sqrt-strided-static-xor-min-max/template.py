# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-strided-static-xor-min-max/template.py
# @operations: stridedMax stridedMin stridedXorQuery
# @data-structure-type: sqrt
# @complexities:
#   stridedMax: N*log(N)
#   stridedMin: N*log(N)
#   stridedXorQuery: N
#   build: N
# @memory:
#   layout: none
#   node: xorPre[1*N] minTable[1*N*log(N)] maxTable[1*N*log(N)]
#   tags: none
#   other: A[1*N]
#   note: the listed cost is a rebuild. Each op keeps one table, for the last step it saw; a repeat of that step is O(1) and a step above sqrt(N) walks, so sorting queries by step offline costs one rebuild per distinct step

# Static strided queries in linear memory: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
# (the last position used may be below r). Each op keeps a single table for the last step it saw, rebuilt when the
# step changes, so the expected use is offline: sort the queries by step, then ask them in that order. All indices
# 0-based, ranges inclusive.
from itertools import accumulate
from functools import reduce
from operator import xor


class StridedQueries:
    # O(build) -- arr: the initial array
    def __init__(self, arr):
        self.A = list(arr)
        self.n = len(self.A)
        self.xorStep = 0  # the step the xor prefixes were built for
        self.xorPre = None
        self.minStep = 0  # the step the min table was built for
        self.minTable = None
        self.maxStep = 0  # the step the max table was built for
        self.maxTable = None

    # a[l] ^ a[l + step] ^ ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    # step; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedXorQuery(self, l, r, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedXorQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedXorQuery: needs step >= 1, got step = {step}")
        last = l + (r - l) // step * step
        count = (r - l) // step + 1
        if step != self.xorStep:
            if count <= 1024 or step * step > self.n:
                return reduce(xor, self.A[l:last + 1:step])
            self.xorStep = step
            self.xorPre = pre = list(self.A)
            for residue in range(min(step, self.n)):
                pre[residue::step] = list(accumulate(pre[residue::step], xor))
        pre = self.xorPre
        return pre[last] ^ pre[l - step] if l >= step else pre[last]

    # min of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    # step; needs 0 <= l <= r < n and step >= 1, else raises IndexError
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

    # max of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    # step; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedMax(self, l, r, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"stridedMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if step < 1:
            raise IndexError(f"stridedMax: needs step >= 1, got step = {step}")
        last = l + (r - l) // step * step
        count = (r - l) // step + 1
        if step != self.maxStep:
            if count <= 1024 or step * step > self.n:
                return max(self.A[l:last + 1:step])
            self.maxStep = step
            self.maxTable = table = [self.A]
            jump = step
            while jump < self.n:
                previous = table[-1]
                table.append(list(map(max, previous, previous[jump:])) + previous[self.n - jump:])
                jump *= 2
        level = count.bit_length() - 1
        row = self.maxTable[level]
        a, b = row[l], row[last - ((1 << level) - 1) * step]
        return a if a > b else b
