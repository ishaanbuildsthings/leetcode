# https://leetcode.com/problems/falling-squares/description/
# difficulty: hard
# tags: segment tree, lazy propagation, coordinate compression, square root decomposition

# Problem
# There are several squares being dropped onto the X-axis of a 2D plane.

# You are given a 2D integer array positions where positions[i] = [lefti, sideLengthi] represents the ith square with a side length of sideLengthi that is dropped with its left edge aligned with X-coordinate lefti.

# Each square is dropped one at a time from a height above any landed squares. It then falls downward (negative Y direction) until it either lands on the top side of another square or on the X-axis. A square brushing the left/right side of another square does not count as landing on it. Once it lands, it freezes in place and cannot be moved.

# After each square is dropped, you must record the height of the current tallest stack of squares.

# Return an integer array ans where ans[i] represents the height described above after dropping the ith square.

# Solution 1
# I coordinate compressed the notable regions (left and right x-coordinates for each square) then used a lazy propagation segment tree. I think we could also just do normal coordinate compression but brute force loop each query. Basically we query among all the compressed coordinates each time for a max or the current max to add our new square too. And when we update we do it for n cells.
# We could also coordinate compress, then square root decomp on the compressed coordinates, so if we get 100 compressed coordinates we split it into blocks of 10. I haven't walked through the full logic but I think each cell should store the max height in it, and if we need more granular we read each of the cells inside the block itself. Whenever we update a range we update the max for the relevant blocks and when we query we can do so with granularity of cells if needed as well. This is no different than how a segment tree stores data for every cell, but then also segments store data.

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

        self.tree[i] = max(self.tree[2*i], self.tree[2*i + 1])

    def _queryMaxRecurse(self, i, tl, tr, l, r):
        # no intersection
        if tl > r or tr < l:
            if self.lazy[i] != 0:
                self.tree[i] = self.lazy[i]
                # push down if needed
                if tl != tr:
                    self.lazy[2*i] = self.lazy[i]
                    self.lazy[2*i + 1] = self.lazy[i]
                # clear the lazy
                self.lazy[i] = 0

            return float('-inf') # identity

        if self.lazy[i] != 0:
            self.tree[i] = self.lazy[i]
            # push down if needed
            if tl != tr:
                self.lazy[2*i] = self.lazy[i]
                self.lazy[2*i + 1] = self.lazy[i]
            # clear the lazy
            self.lazy[i] = 0


        # fully contained
        if tl >= l and tr <= r:
            return self.tree[i]

        tm = (tr + tl) // 2
        # check left and right
        leftRes = self._queryMaxRecurse(2*i, tl, tm, l, r)
        rightRes = self._queryMaxRecurse(2*i + 1, tm + 1, tr, l, r)
        return max(leftRes, rightRes)

    def _updateRangeRecurse(self, i, tl, tr, l, r, newVal):
        # if we are lazy, update our current value and push
        if self.lazy[i]:
            self.tree[i] = self.lazy[i]
            # push down if we have children
            if tl != tr:
                self.lazy[2*i] = self.lazy[i]
                self.lazy[2*i + 1] = self.lazy[i]

            self.lazy[i] = 0 # clear the lazy


        # no intersection
        if l > tr or r < tl:
            return

        # fully contained
        if tl >= l and tr <= r:
            self.tree[i] = newVal # update the segment, after all the new max for the segment is the entire value we set
            if tl != tr:
                # push the assignment down to future children, after all that granularity isn't needed yet
                self.lazy[2*i] = newVal
                self.lazy[2*i + 1] = newVal
            return

        tm = (tr + tl) // 2

        # we need to recurse deeper if we aren't fully contained, though during our descent we at least applied lazys that were needed for the first time now
        self._updateRangeRecurse(2*i, tl, tm, l, r, newVal)
        self._updateRangeRecurse(2*i + 1, tm + 1, tr, l, r, newVal)

        self.tree[i] = max(self.tree[2*i], self.tree[2*i + 1])


    ### PUBLIC METHODS

    def queryMax(self, l, r):
        return self._queryMaxRecurse(1, 0, self.n - 1, l, r)

    def assignRangeToValue(self, l, r, newMax):
        self._updateRangeRecurse(1, 0, self.n - 1, l, r, newMax)



class Solution:
    def fallingSquares(self, positions: List[List[int]]) -> List[int]:
        coords = set()
        for leftSide, sideLength in positions:
            coords.add(leftSide)
            coords.add(leftSide + sideLength)
        compressed = sorted(list(coords))
        valToIndex = { val : i for i, val in enumerate(compressed) }

        seg = SegTree(len(compressed))
        res = []
        for left, sidelength in positions:
            leftCompressed = valToIndex[left]
            sidelengthCompressed = valToIndex[left + sidelength]
            # first find the max in the region we are dropping
            maxInRegion = seg.queryMax(leftCompressed, sidelengthCompressed - 1) # exclusive range
            # now assign the new height
            seg.assignRangeToValue(leftCompressed, sidelengthCompressed - 1, maxInRegion + sidelength)
            # now determine the new max anywhere
            res.append(seg.queryMax(0, len(compressed) - 1))

        return res
