# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-pointGet/template.py
# @operations: countOccurrences pointGet
# @data-structure-type: positions
# @complexities:
#   countOccurrences: log(N)
#   pointGet: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: pos[1*N]
#   tags: none
#   other: arr[1*N]
#   note: pos maps each value to the sorted list of indices holding it; the build is O(N): a dict of lists filled left to right

from bisect import bisect_left, bisect_right

# Static "how many times does x appear in a[l..r]?". All indices 0-based, ranges inclusive.
# Each value keeps the sorted list of its indices; a query is two binary searches in x's list.


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

    # O(logN) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        p = self.pos.get(x)
        return bisect_right(p, r) - bisect_left(p, l) if p and l <= r else 0

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]
