# https://leetcode.com/problems/number-of-flowers-in-full-bloom/description/?envType=daily-question&envId=2023-10-11
# difficulty: hard
# tags: sweep line, coordinate compression, segment tree, lazy propagation

# Problem
# You are given a 0-indexed 2D integer array flowers, where flowers[i] = [starti, endi] means the ith flower will be in full bloom from starti to endi (inclusive). You are also given a 0-indexed integer array people of size n, where people[i] is the time that the ith person will arrive to see the flowers.

# Return an integer array answer of size n, where answer[i] is the number of flowers that are in full bloom when the ith person arrives.

# Solution, O(n log n) time, O(n) space
# The range where flowers can exist is too wide to create a true sweep line. Instead, we just make a sweep line representing the critical moments where the number of flowers change. Then, we can create a prefix sweep to tell us the number of flowers in some range. Then we binary search on that prefix sweep to answer a query.
# EDIT NODE: Later (after learning lazy segment trees), I realize this was coordinate compression. I came up with it before realizing it existed!
# I think this can be done with a single sweep line. Just iterate over the ranges, and construct the prefix sweep in one go.
# SOLUTION 2: We can also use a segment tree for the coordinates flowers appear. We add to segments with lazy propagation, and query individual indices. We use coordinate compression since the range flowers can be in is wide. (Scroll down to see the code, below the first solution)

class Solution:
    def fullBloomFlowers(self, flowers: List[List[int]], people: List[int]) -> List[int]:
        sweepMap = defaultdict(int) # maps a pos to a diff
        for l, r in flowers:
            sweepMap[l] += 1
            sweepMap[r+1] -=1
        sweep = [] # holds [pos, diff]
        for pos in sweepMap.keys():
            diff = sweepMap[pos]
            sweep.append([pos, diff])
        sweep.sort()

        prefixMap = defaultdict(int) # maps a prefix amount of steps at a critical moment to the number of flowers
        runningFlowers = 0
        for pos, diff in sweep:
            runningFlowers += diff
            prefixMap[pos] = runningFlowers

        prefix = [] # holds [pos, total acrrued]
        for pos in prefixMap:
            totalAccrued = prefixMap[pos]
            prefix.append([pos, totalAccrued])
        prefix.sort()
        positions = [tup[0] for tup in prefix] # helps bisect

        res = []
        for personPosition in people:
            index = bisect.bisect_right(positions, personPosition) # index where we would inser to maintain sorted
            lastSmallerPosition = index - 1
            flowerAmount = prefix[lastSmallerPosition][1]
            res.append(flowerAmount)
        return res




# Solution 2, segment tree + lazy propagation + coordinate compression

class SegTree:
    def __init__(self, n):
        self.n = n
        self.tree = [None] * 4 * self.n
        self.lazy = [0] * len(self.tree)
        self._build(1, 0, self.n - 1)

    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = 0
            return
        # build left and right
        tm = (tr + tl) // 2
        self._build(2*i, tl, tm)
        self._build(2*i + 1, tm + 1, tr)

        self.tree[i] = self.tree[2*i] + self.tree[2*i + 1]

    def _queryMaxRecurse(self, i, tl, tr, l, r):
        # no intersection
        if tl > r or tr < l:
            if self.lazy[i] != 0:
                self.tree[i] += self.lazy[i]
                # push down if needed
                if tl != tr:
                    self.lazy[2*i] += self.lazy[i]
                    self.lazy[2*i + 1] += self.lazy[i]
                # clear the lazy
                self.lazy[i] = 0

            return 0 # identity

        if self.lazy[i] != 0:
            self.tree[i] += self.lazy[i]
            # push down if needed
            if tl != tr:
                self.lazy[2*i] += self.lazy[i]
                self.lazy[2*i + 1] += self.lazy[i]
            # clear the lazy
            self.lazy[i] = 0


        # fully contained
        if tl >= l and tr <= r:
            return self.tree[i]

        tm = (tr + tl) // 2
        # check left and right
        leftRes = self._queryMaxRecurse(2*i, tl, tm, l, r)
        rightRes = self._queryMaxRecurse(2*i + 1, tm + 1, tr, l, r)
        return leftRes + rightRes

    def _updateRangeRecurse(self, i, tl, tr, l, r, newVal):
        # if we are lazy, update our current value and push
        if self.lazy[i]:
            self.tree[i] = self.tree[i] + self.lazy[i]
            # push down if we have children
            if tl != tr:
                self.lazy[2*i] += self.lazy[i]
                self.lazy[2*i + 1] += self.lazy[i]

            self.lazy[i] = 0 # clear the lazy


        # no intersection
        if l > tr or r < tl:
            return

        # fully contained
        if tl >= l and tr <= r:
            self.tree[i] += newVal # update the segment, after all the new max for the segment is the entire value we set
            if tl != tr:
                # push the assignment down to future children, after all that granularity isn't needed yet
                self.lazy[2*i] += newVal
                self.lazy[2*i + 1] += newVal
            return

        tm = (tr + tl) // 2

        # we need to recurse deeper if we aren't fully contained, though during our descent we at least applied lazys that were needed for the first time now
        self._updateRangeRecurse(2*i, tl, tm, l, r, newVal)
        self._updateRangeRecurse(2*i + 1, tm + 1, tr, l, r, newVal)

        self.tree[i] = self.tree[2*i] + self.tree[2*i + 1]


    ### PUBLIC METHODS

    def queryMax(self, l, r):
        return self._queryMaxRecurse(1, 0, self.n - 1, l, r)

    def assignRangeToValue(self, l, r, newMax):
        self._updateRangeRecurse(1, 0, self.n - 1, l, r, newMax)


class Solution:
    def fullBloomFlowers(self, flowers: List[List[int]], people: List[int]) -> List[int]:
        coords = set()
        for left, right in flowers:
            coords.add(left)
            coords.add(right)
        for person in people:
            coords.add(person)
        valToCompressedIndex = { val : i for i, val in enumerate(sorted(coords)) }

        seg = SegTree(len(coords))
        res = []
        for l, r in flowers:
            seg.assignRangeToValue(valToCompressedIndex[l], valToCompressedIndex[r], 1)
        for i in range(len(people)):
            res.append(seg.queryMax(valToCompressedIndex[people[i]], valToCompressedIndex[people[i]]))
        return res

