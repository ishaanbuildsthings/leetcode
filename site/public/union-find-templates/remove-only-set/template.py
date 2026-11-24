# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/remove-only-set/template.py
# @operations: contains largestLtX largestLteX max min popInValRange popMax popMin remove smallestGtX smallestGteX
# @data-structure-type: remove-only-set
# @complexities:
#   contains: 1
#   largestLtX: α(N) amortized
#   largestLteX: α(N) amortized
#   max: α(N) amortized
#   min: α(N) amortized
#   popInValRange: α(N) amortized
#   popMax: α(N) amortized
#   popMin: α(N) amortized
#   remove: α(N) amortized
#   smallestGtX: α(N) amortized
#   smallestGteX: α(N) amortized
#   build: N
# @memory:
#   layout: none
#   node: par[1*N] lo[1*N] hi[1*N]
#   tags: none
#   other: present[1*N]
#   note: N = the range it covers: n, or max(values) - min(values) + 1. popInValRange costs α(N) per value they remove, and a value is only removed once, so O(N α(N)) over every call together

# s = RemoveOnlySet(10)                   # holds 0, 1, 2, ..., 9
# s = RemoveOnlySet(values=[1, 4, 7])     # holds 1, 4, 7
# s = RemoveOnlySet(values=[-50, 3, 99])  # any ints (negatives too); memory is max - min + 1
# A set that only ever loses values: nothing can be added back. smallestGteX / largestLteX jump to the nearest value
# still in it from any x, present or not.
# Union find underneath: each run of removed values is grouped with the value just after it, groups linked by size.


class RemoveOnlySet:
    # O(N) -- pass exactly one: n (holds 0..n-1) or values (holds just those: any ints, duplicates are fine)
    def __init__(self, n=None, values=None):
        if (n is None) == (values is None):
            raise TypeError("RemoveOnlySet: pass n (holds 0..n-1) or values=[...] (holds just those), exactly one")
        if values is None:
            self.base, size = 0, n
            present = bytearray([1]) * n
        else:
            values = list(values)
            self.base = min(values, default=0)
            size = max(values) - self.base + 1 if values else 0
            present = bytearray(size)
            for x in values:
                present[x - self.base] = 1
        self.n = size
        self.cnt = sum(present)
        present.append(1)  # index n: a stand-in that never leaves, so every group ends in something present
        self.present = present
        # each group: a run of removed values plus the present value right after it; its root knows both ends
        par = self.par = list(range(size + 1))
        lo = self.lo = list(range(size + 1))
        self.hi = list(range(size + 1))
        start = 0
        for i in range(size + 1):
            if present[i]:
                for j in range(start, i):
                    par[j] = i
                lo[i] = start
                start = i + 1

    def _find(self, i):
        par = self.par
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    # O(1) -- True if x is in the set (any x is fine)
    def contains(self, x):
        i = x - self.base
        return 0 <= i < self.n and self.present[i] == 1

    # O(1) -- how many values are still in the set
    def size(self):
        return self.cnt

    # O(α(N)) amortized -- remove x; returns 1 if it was there, else 0 (any x is fine)
    def remove(self, x):
        i = x - self.base
        if not 0 <= i < self.n or not self.present[i]:
            return 0
        self.present[i] = 0
        self.cnt -= 1
        left = self._find(i)
        right = self._find(i + 1)
        lo, hi = self.lo, self.hi
        if hi[left] - lo[left] > hi[right] - lo[right]:
            self.par[right] = left
            hi[left] = hi[right]
        else:
            self.par[left] = right
            lo[right] = lo[left]
        return 1

    # O(α(N)) amortized -- smallest value >= x; None if there is none (any x is fine)
    def smallestGteX(self, x):
        i = x - self.base
        if i >= self.n:
            return None
        found = self.hi[self._find(max(i, 0))]
        return None if found == self.n else found + self.base

    # O(α(N)) amortized -- smallest value > x; None if there is none (any x is fine)
    def smallestGtX(self, x):
        return self.smallestGteX(x + 1)

    # O(α(N)) amortized -- largest value <= x; None if there is none (any x is fine)
    def largestLteX(self, x):
        i = min(x - self.base, self.n - 1)
        if i < 0:
            return None
        if self.present[i]:
            return i + self.base
        found = self.lo[self._find(i)] - 1
        return None if found < 0 else found + self.base

    # O(α(N)) amortized -- largest value < x; None if there is none (any x is fine)
    def largestLtX(self, x):
        return self.largestLteX(x - 1)

    # O(α(N)) amortized -- the smallest value; raises IndexError if empty
    def min(self):
        if not self.cnt:
            raise IndexError("min: the set is empty")
        return self.smallestGteX(self.base)

    # O(α(N)) amortized -- the largest value; raises IndexError if empty
    def max(self):
        if not self.cnt:
            raise IndexError("max: the set is empty")
        return self.largestLteX(self.base + self.n - 1)

    # O(α(N)) amortized -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        if not self.cnt:
            raise IndexError("popMin: the set is empty")
        x = self.smallestGteX(self.base)
        self.remove(x)
        return x

    # O(α(N)) amortized -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        if not self.cnt:
            raise IndexError("popMax: the set is empty")
        x = self.largestLteX(self.base + self.n - 1)
        self.remove(x)
        return x

    # O(α(N)) per value removed, amortized -- remove every value in [lo, hi] and return them in increasing order
    # ([] if lo > hi)
    def popInValRange(self, lo, hi):
        res = []
        x = self.smallestGteX(lo)
        while x is not None and x <= hi:
            self.remove(x)
            res.append(x)
            x = self.smallestGteX(x + 1)
        return res
