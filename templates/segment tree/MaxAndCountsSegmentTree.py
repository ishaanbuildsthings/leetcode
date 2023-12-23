# ______________________________________________________________________
# TEMPLATE - max and appearances segment tree

# FUNCTIONS:
# Query max of range O(logN)
# Query number of times the max appears in range O(logN)
# Update value O(logN)

# General reqs:
# An array of numbers

# Complexities:
# Build: O(n)
# Space: O(n)

class MaxAndAppearancesSegmentTree:

    def __init__(self, data):
        self.n = len(data)
        self.data = data
        self.tree = [None] * 4 * self.n  # each element of the tree will hold a tuple (max, count)
        self._build(0, 0, self.n - 1)

    # i is the index of the vertex we are at, tl is the left boundary, tr is the right boundary
    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = (self.data[tl], 1)
            return
        tm = (tr + tl) // 2
        self._build(2*i + 1, tl, tm)
        self._build(2*i + 2, tm + 1, tr)
        leftMax, leftCount = self.tree[2*i + 1]
        rightMax, rightCount = self.tree[2*i + 2]
        self.tree[i] = self._combine(leftMax, leftCount, rightMax, rightCount)

    def _combine(self, leftMax, leftCount, rightMax, rightCount):
        if leftMax == rightMax:
            return (leftMax, leftCount + rightCount)
        elif leftMax > rightMax:
            return (leftMax, leftCount)
        return (rightMax, rightCount)

    # tl and tr are the boundaries of the current node
    # l and r are boundaries we need a max from, in the current node
    def _queryRecurse(self, i, tl, tr, l, r):
        # simplify the code
        if l > r:
            return (float('-inf'), 0) # always fail with -inf, simplifies code to always make 2 calls
        # perfect match
        if l == tl and r == tr:
            return self.tree[i]
        tm = (tr + tl) // 2 # calculate the middle of our node, basically get the two children
        leftMax, leftCount = self._queryRecurse(2*i + 1, tl, tm, l, min(r, tm))
        rightMax, rightCount = self._queryRecurse(2*i + 2, tm + 1, tr, max(l, tm + 1), r)
        return self._combine(leftMax, leftCount, rightMax, rightCount)

    def _updateRecurse(self, i, tl, tr, posToBeUpdated, newVal):
        if tl == tr:
            self.tree[i] = (newVal, 1)
            return

        tm = (tr + tl) // 2
        if posToBeUpdated <= tm:
            self._updateRecurse(2*i + 1, tl, tm, posToBeUpdated, newVal)
        else:
            self._updateRecurse(2*i + 2, tm + 1, tr, posToBeUpdated, newVal)
        leftMax, leftCount = self.tree[2*i + 1]
        rightMax, rightCount = self.tree[2*i + 2]
        self.tree[i] = self._combine(leftMax, leftCount, rightMax, rightCount)

    ################################## PUBLIC METHODS START HERE ##################################

    # Update the value of a cell in the segment tree in O(logN)
    def update(self, index, newVal) -> None:
        self._updateRecurse(0, 0, self.n - 1, index, newVal)

    # Query the max from [l:r] and the amount of times it occurs in O(logN)
    def queryMaxAndFreq(self, l, r) -> int:
        return self._queryRecurse(0, 0, self.n - 1, l, r)
