# @operations: countOccurrences pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: positions
# @complexities:
#   countOccurrences: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: pos[1*N]
#   tags: none
#   other: a[1*N]
#   note: pos maps each value to its sorted indices (C++: an order-statistics tree per value; Python: plain sorted lists, so an assign is a memmove over that value's occurrences)

from bisect import bisect_left, bisect_right

# "How many times does x appear in a[l..r]?" with point updates. All indices 0-based, ranges inclusive.
# Each value keeps the sorted list of its indices; a query is two binary searches in x's list, and an assign moves
# one index from the old value's list to the new one's.


class DynamicOccurrenceLists:
    __slots__ = ("a", "pos")

    # O(N)
    def __init__(self, arr):
        self.a = list(arr)
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

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        old = self.a[i]
        if old == val:
            return
        pos = self.pos
        p = pos[old]
        p.pop(bisect_left(p, i))
        if not p:
            del pos[old]
        if val in pos:
            p = pos[val]
            p.insert(bisect_left(p, i), i)
        else:
            pos[val] = [i]
        self.a[i] = val

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.a[i]

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.a[i] + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.a[i]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.a[i]:
            self.pointAssign(i, val)
