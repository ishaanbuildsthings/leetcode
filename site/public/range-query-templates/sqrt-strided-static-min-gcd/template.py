# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-strided-static-min-gcd/template.py
# @operations: stridedGcd stridedMin
# @data-structure-type: sqrt
# @complexities:
#   stridedGcd: N*log(N)+N*log(U) ?
#   stridedMin: N*log(N)
#   build: N
# @memory:
#   layout: none
#   node: minTable[1*N*log(N)] gcdTable[1*N*log(N)]
#   tags: none
#   other: A[1*N]
#   note: the listed cost is a rebuild. Each op keeps one table, for the last step it saw; a repeat of that step is O(1) and a step above sqrt(N) walks, so sorting queries by step offline costs one rebuild per distinct step

# Static strided queries in linear memory: each query covers a[l], a[l + step], a[l + 2 * step], ... up to at most r
# (the last position used may be below r). Each op keeps a single table for the last step it saw, rebuilt when the
# step changes, so the expected use is offline: sort the queries by step, then ask them in that order. All indices
# 0-based, ranges inclusive.
from math import gcd


class StridedQueries:
    # O(build) -- arr: the initial array
    def __init__(self, arr):
        self.A = list(arr)
        self.n = len(self.A)
        self.minStep = 0  # the step the min table was built for
        self.minTable = None
        self.gcdStep = 0  # the step the gcd table was built for
        self.gcdTable = None

    # min of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    # step; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedMin(self, l, r, step):
        if l < 0 or l > r or r >= self.n or step < 1:
            raise IndexError(f"stridedMin: needs 0 <= l <= r < n and step >= 1, got l={l}, r={r}, step={step}, n={self.n}")
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

    # gcd of a[l], a[l + step], ..., up to at most r. O(1) when step is the last step this op built for, so ask queries grouped by
    # step; needs 0 <= l <= r < n and step >= 1, else raises IndexError
    def stridedGcd(self, l, r, step):
        if l < 0 or l > r or r >= self.n or step < 1:
            raise IndexError(f"stridedGcd: needs 0 <= l <= r < n and step >= 1, got l={l}, r={r}, step={step}, n={self.n}")
        last = l + (r - l) // step * step
        count = (r - l) // step + 1
        if step != self.gcdStep:
            if count <= 1024 or step * step > self.n:
                return gcd(*self.A[l:last + 1:step])
            self.gcdStep = step
            self.gcdTable = table = [self.A]
            jump = step
            while jump < self.n:
                previous = table[-1]
                table.append(list(map(gcd, previous, previous[jump:])) + previous[self.n - jump:])
                jump *= 2
        level = count.bit_length() - 1
        row = self.gcdTable[level]
        a, b = row[l], row[last - ((1 << level) - 1) * step]
        return gcd(a, b)
