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
#   note: popInValRange costs α(N) per value it removes, and a value is only removed once, so O(N α(N)) over every call together

# s = RemoveOnlySet(10)  # holds 0, 1, 2, ..., 9
# A set of 0..n-1 that only ever loses values: nothing can be added back. smallestGteX / largestLteX jump to the
# nearest value still in it from any x, present or not.
# Union find underneath: a removed value joins the group to its right, so each group is a run of removed values plus
# the one present value at its right end; the root keeps the group's two ends, and groups are linked by size.


class RemoveOnlySet:
    # O(n) -- holds 0, 1, ..., n-1
    def __init__(self, n):
        self.n = self.cnt = n
        self.present = bytearray([1]) * (n + 1)  # index n: a stand-in that never leaves, so every group has a right end
        self.par = list(range(n + 1))
        self.lo = list(range(n + 1))  # at a root: the group's smallest value
        self.hi = list(range(n + 1))  # at a root: the group's largest value, the only one still present

    def _find(self, i):
        par = self.par
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    # O(1) -- True if x is in the set (any x is fine)
    def contains(self, x):
        return 0 <= x < self.n and self.present[x] == 1

    # O(1) -- how many values are still in the set
    def size(self):
        return self.cnt

    # O(α(N)) amortized -- remove x; returns 1 if it was there, else 0 (any x is fine)
    def remove(self, x):
        if not self.contains(x):
            return 0
        self.present[x] = 0
        self.cnt -= 1
        left = self._find(x)
        right = self._find(x + 1)
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
        if x >= self.n:
            return None
        found = self.hi[self._find(max(x, 0))]
        return None if found == self.n else found

    # O(α(N)) amortized -- smallest value > x; None if there is none (any x is fine)
    def smallestGtX(self, x):
        return self.smallestGteX(x + 1)

    # O(α(N)) amortized -- largest value <= x; None if there is none (any x is fine)
    def largestLteX(self, x):
        x = min(x, self.n - 1)
        if x < 0:
            return None
        if self.present[x]:
            return x
        found = self.lo[self._find(x)] - 1
        return None if found < 0 else found

    # O(α(N)) amortized -- largest value < x; None if there is none (any x is fine)
    def largestLtX(self, x):
        return self.largestLteX(x - 1)

    # O(α(N)) amortized -- the smallest value; raises IndexError if empty
    def min(self):
        if not self.cnt:
            raise IndexError("min: the set is empty")
        return self.smallestGteX(0)

    # O(α(N)) amortized -- the largest value; raises IndexError if empty
    def max(self):
        if not self.cnt:
            raise IndexError("max: the set is empty")
        return self.largestLteX(self.n - 1)

    # O(α(N)) amortized -- remove and return the smallest value; raises IndexError if empty
    def popMin(self):
        x = self.min()
        self.remove(x)
        return x

    # O(α(N)) amortized -- remove and return the largest value; raises IndexError if empty
    def popMax(self):
        x = self.max()
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
