# ______________________________________________________________________
# TEMPLATE - min and appearances segment tree

# FUNCTIONS:
# Query min of range O(logN)
# Query number of times the min appears in range O(logN)
# Update value O(logN)

# General reqs:
# An array of numbers

# Complexities:
# Build: O(n)
# Space: O(n)

class MinAndAppearancesSegmentTree:

    def __init__(self, data):
        self.n = len(data)
        self.data = data
        self.tree = [None] * 4 * self.n  # each element of the tree will hold a tuple (min, count)
        self._build(0, 0, self.n - 1)

    # i is the index of the vertex we are at, tl is the left boundary, tr is the right boundary
    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = (self.data[tl], 1)
            return
        tm = (tr + tl) // 2
        self._build(2*i + 1, tl, tm)
        self._build(2*i + 2, tm + 1, tr)
        leftMin, leftCount = self.tree[2*i + 1]
        rightMin, rightCount = self.tree[2*i + 2]
        self.tree[i] = self._combine(leftMin, leftCount, rightMin, rightCount)

    # helper function
    def _combine(self, leftMin, leftCount, rightMin, rightCount):
        if leftMin == rightMin:
            return (leftMin, leftCount + rightCount)
        elif leftMin < rightMin:
            return (leftMin, leftCount)
        return (rightMin, rightCount)

    # tl and tr are the boundaries of the current node
    # l and r are boundaries we need a min from, in the current node
    def _queryRecurse(self, i, tl, tr, l, r):
        # simplify the code
        if l > r:
            return (float('inf'), 0) # always fail with inf, simplifies code to always make 2 calls
        # perfect match
        if l == tl and r == tr:
            return self.tree[i]
        tm = (tr + tl) // 2 # calculate the middle of our node, basically get the two children
        leftMin, leftCount = self._queryRecurse(2*i + 1, tl, tm, l, min(r, tm))
        rightMin, rightCount = self._queryRecurse(2*i + 2, tm + 1, tr, max(l, tm + 1), r)
        return self._combine(leftMin, leftCount, rightMin, rightCount)

    def _updateRecurse(self, i, tl, tr, posToBeUpdated, newVal):
        if tl == tr:
            self.tree[i] = (newVal, 1)
            return

        tm = (tr + tl) // 2
        if posToBeUpdated <= tm:
            self._updateRecurse(2*i + 1, tl, tm, posToBeUpdated, newVal)
        else:
            self._updateRecurse(2*i + 2, tm + 1, tr, posToBeUpdated, newVal)
        leftMin, leftCount = self.tree[2*i + 1]
        rightMin, rightCount = self.tree[2*i + 2]
        self.tree[i] = self._combine(leftMin, leftCount, rightMin, rightCount)

    ################################## PUBLIC METHODS START HERE ##################################

    # Update the value of a cell in the segment tree in O(logN)
    def update(self, index, newVal) -> None:
        self._updateRecurse(0, 0, self.n - 1, index, newVal)

    # Query the min from [l:r] and the amount of times it occurs in O(logN)
    def queryMinAndFreq(self, l, r) -> int:
        return self._queryRecurse(0, 0, self.n - 1, l, r)
