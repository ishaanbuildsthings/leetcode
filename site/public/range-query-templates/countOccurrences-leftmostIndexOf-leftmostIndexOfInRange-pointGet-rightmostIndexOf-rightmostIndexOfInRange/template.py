# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointGet-rightmostIndexOf-rightmostIndexOfInRange/template.py
# @operations: countOccurrences leftmostIndexOf leftmostIndexOfInRange pointGet rightmostIndexOf rightmostIndexOfInRange
# @data-structure-type: positions
# @letters: same
# @complexities:
#   countOccurrences: log(N)
#   leftmostIndexOf: log(N)
#   leftmostIndexOfInRange: log(N)
#   pointGet: 1
#   rightmostIndexOf: log(N)
#   rightmostIndexOfInRange: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: pos[1*N]
#   tags: none
#   other: arr[1*N]
#   note: pos maps each value to the sorted list of indices holding it; the build is O(N): a dict of lists filled left to right

from bisect import bisect_left, bisect_right

# Static "how many times does x appear in a[l..r]?" and "where is x's first / last copy (in a[l..r])?". All indices
# 0-based, ranges inclusive. Each value keeps the sorted list of its indices; a query is a binary search or two in
# x's list.


class OccurrenceLists:
    __slots__ = ("arr", "pos")

    # O(N)
    def __init__(self, arr):
        self.arr = arr
        pos = self.pos = {}
        for i, v in enumerate(arr):
            if v in pos:
                pos[v].append(i)
            else:
                pos[v] = [i]

    # O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        p = self.pos.get(x)
        return bisect_right(p, r) - bisect_left(p, l) if p and l <= r else 0

    # O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        p = self.pos.get(x)
        return p[0] if p else -1

    # O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        p = self.pos.get(x)
        return p[-1] if p else -1

    # O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        p = self.pos.get(x)
        if not p:
            return -1
        k = bisect_left(p, l)
        return p[k] if k < len(p) and p[k] <= r else -1

    # O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        p = self.pos.get(x)
        if not p:
            return -1
        k = bisect_right(p, r) - 1
        return p[k] if k >= 0 and p[k] >= l else -1

    # O(1) -- the length of the array
    def size(self):
        return len(self.arr)

    # O(1) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        return self.arr[i]
