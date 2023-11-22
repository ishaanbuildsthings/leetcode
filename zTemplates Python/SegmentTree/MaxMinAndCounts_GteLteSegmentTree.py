# ______________________________________________________________________
# TEMPLATE - can give max, min, counts, earliest and latest indices for a number >= or <= some threshold
# TODO: test, validate if pruning helps

# FUNCTIONS:
# Query max of range O(logN)
# Query # of times max appears in range O(logN)
# Query min of range O(logN)
# Query # of times min appears in range O(logN)
# Query earliest index of a number >= `num` in range O(logN)
# Query latest index of a number >= `num` in range O(logN)
# Query earliest index of a number <= `num` in range O(logN)
# Query latest index of a number <= `num` in range O(logN)
# Update value O(logN)

# General reqs:
# An array of numbers

# Complexities:
# Build: O(n)
# Space: O(n)

class MaxMinAndCounts_GteLteSegmentTree:

    def __init__(self, data):
        self.n = len(data)
        self.data = data
        self.tree = [None] * 4 * self.n # stores (max, maxCount, min, minCount)
        self._build(0, 0, self.n - 1)

    # i is the index of the vertex we are at, tl is the left boundary, tr is the right boundary
    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = (self.data[tl], 1, self.data[tl], 1)
            return
        tm = (tr + tl) // 2
        self._build(2*i + 1, tl, tm)
        self._build(2*i + 2, tm + 1, tr)
        leftMax, leftMaxCount, leftMin, leftMinCount = self.tree[2*i + 1]
        rightMax, rightMaxCount, rightMin, rightMinCount = self.tree[2*i + 2]
        self.tree[i] = self._combine(leftMax, leftMaxCount, leftMin, leftMinCount, rightMax, rightMaxCount, rightMin, rightMinCount)

    def _combine(self, leftMax, leftMaxCount, leftMin, leftMinCount, rightMax, rightMaxCount, rightMin, rightMinCount):
        newMaxCount = leftMaxCount + rightMaxCount if leftMax == rightMax else max(leftMaxCount, rightMaxCount)
        newMinCount = leftMinCount + rightMinCount if leftMin == rightMin else max(leftMinCount, rightMinCount)
        newMax = max(leftMax, rightMax)
        newMin = min(leftMin, rightMin)
        return (newMax, newMaxCount, newMin, newMinCount)

    # tl and tr are the boundaries of the current node
    # l and r are boundaries we need our data from, in the current node
    def _queryRecurse(self, i, tl, tr, l, r):
        # simplify the code
        if l > r:
            return (float('-inf'), 0, float('inf'), 0)
        # perfect match
        if l == tl and r == tr:
            return self.tree[i]
        tm = (tr + tl) // 2 # calculate the middle of our node, basically get the two children
        leftMax, leftMaxCount, leftMin, leftMinCount = self._queryRecurse(2*i + 1, tl, tm, l, min(r, tm))
        rightMax, rightMaxCount, rightMin, rightMinCount = self._queryRecurse(2*i + 2, tm + 1, tr, max(l, tm + 1), r)
        return self._combine(leftMax, leftMaxCount, leftMin, leftMinCount, rightMax, rightMaxCount, rightMin, rightMinCount)

    def _updateRecurse(self, i, tl, tr, posToBeUpdated, newVal):
        if tl == tr:
            self.tree[i] = (newVal, 1, newVal, 1)
            return

        tm = (tr + tl) // 2
        if posToBeUpdated <= tm:
            self._updateRecurse(2*i + 1, tl, tm, posToBeUpdated, newVal)
        else:
            self._updateRecurse(2*i + 2, tm + 1, tr, posToBeUpdated, newVal)
        self.tree[i] = self._combine(*self.tree[2*i + 1], *self.tree[2*i + 2])

    def _recurseGetEarliestGTENum(self, i, tl, tr, l, r, numToBeat):
        if l > r:
            return -1
        if tl == tr:
            numAtNode = self.data[tl]
            return tl if numAtNode >= numToBeat else -1

        # pruning
        biggest = self.tree[i][0]
        if biggest < numToBeat:
            return -1
        leftMax = self.tree[2*i + 1][0]
        if leftMax < numToBeat:
            return self._recurseGetEarliestGTENum(2*i + 2, tr, tr, max(l, tl), r, numToBeat)
        rightMax = self.tree[2*i + 2][0]
        if rightMax < numToBeat:
            return self._recurseGetEarliestGTENum(2*i + 1, tl, tl, l, min(r, tr), numToBeat)

        tm = (tr + tl) // 2
        leftResult = self._recurseGetEarliestGTENum(2*i + 1, tl, tm, l, min(r, tm), numToBeat)
        if leftResult != -1:
            return leftResult
        return self._recurseGetEarliestGTENum(2*i + 2, tm + 1, tr, max(tm + 1, l), r, numToBeat)

    def _recurseGetLatestGTENum(self, i, tl, tr, l, r, numToBeat):
        if l > r:
            return -1
        if tl == tr:
            numAtNode = self.data[tl]
            return tl if numAtNode >= numToBeat else -1

        # pruning
        biggest = self.tree[i][0]
        if biggest < numToBeat:
            return -1
        leftMax = self.tree[2*i + 1][0]
        if leftMax < numToBeat:
            return self._recurseGetEarliestGTENum(2*i + 2, tr, tr, max(l, tl), r, numToBeat)
        rightMax = self.tree[2*i + 2][0]
        if rightMax < numToBeat:
            return self._recurseGetEarliestGTENum(2*i + 1, tl, tl, l, min(r, tr), numToBeat)

        tm = (tr + tl) // 2
        rightResult = self._recurseGetLatestGTENum(2*i + 2, tm + 1, tr, max(tm + 1, l), r, numToBeat)
        if rightResult != -1:
            return rightResult
        return self._recurseGetLatestGTENum(2*i + 1, tl, tm, l, min(r, tm), numToBeat)

    def _recurseGetEarliestLTENum(self, i, tl, tr, l, r, numToBeat):
        if l > r:
            return -1
        if tl == tr:
            numAtNode = self.data[tl]
            return tl if numAtNode <= numToBeat else -1
        tm = (tr + tl) // 2

        # pruning
        smallest = self.tree[i][2]
        if smallest > numToBeat:
            return -1
        leftMin = self.tree[2*i + 1][2]
        if leftMin > numToBeat:
            return self._recurseGetEarliestLTENum(2*i + 2, tm + 1, tr, max(tm + 1, l), r, numToBeat)
        rightMin = self.tree[2*i + 2][2]
        if rightMin > numToBeat:
            return self._recurseGetEarliestLTENum(2*i + 1, tl, tm, l, min(r, tm), numToBeat)

        leftResult = self._recurseGetEarliestLTENum(2*i + 1, tl, tm, l, min(r, tm), numToBeat)
        if leftResult != -1:
            return leftResult
        return self._recurseGetEarliestLTENum(2*i + 2, tm + 1, tr, max(tm + 1, l), r, numToBeat)

    def _recurseGetLatestLTENum(self, i, tl, tr, l, r, numToBeat):
        if l > r:
            return -1
        if tl == tr:
            numAtNode = self.data[tl]
            return tl if numAtNode <= numToBeat else -1
        tm = (tr + tl) // 2

        # pruning
        smallest = self.tree[i][2]
        if smallest > numToBeat:
            return -1
        leftMin = self.tree[2*i + 1][2]
        if leftMin > numToBeat:
            return self._recurseGetEarliestLTENum(2*i + 2, tm + 1, tr, max(tm + 1, l), r, numToBeat)
        rightMin = self.tree[2*i + 2][2]
        if rightMin > numToBeat:
            return self._recurseGetEarliestLTENum(2*i + 1, tl, tm, l, min(r, tm), numToBeat)

        rightResult = self._recurseGetLatestLTENum(2*i + 2, tm + 1, tr, max(tm + 1, l), r, numToBeat)
        if rightResult != -1:
            return rightResult
        return self._recurseGetLatestLTENum(2*i + 1, tl, tm, l, min(r, tm), numToBeat)

    ################################## PUBLIC METHODS START HERE ##################################

    # Update the value of a cell in the segment tree in O(logN)
    def update(self, index, newVal) -> None:
        self._updateRecurse(0, 0, self.n - 1, index, newVal)

    # Query the max from [l:r] in O(logN)
    def queryMax(self, l, r) -> int:
        return self._queryRecurse(0, 0, self.n - 1, l, r)[0]

    # Query the # of times max in [l:r] appears, in [l:r] in O(logN)
    def queryMaxCount(self, l, r) -> int:
        return self._queryRecurse(0, 0, self.n - 1, l, r)[1]

    # Query the min from [l:r] in O(logN)
    def queryMin(self, l, r) -> int:
        return self._queryRecurse(0, 0, self.n - 1, l, r)[2]

    # Query the # of times min in [l:r] appears, in [l:r] in O(logN)
    def queryMinCount(self, l, r) -> int:
        return self._queryRecurse(0, 0, self.n - 1, l, r)[3]

    # Query the earliest index of a number >= `num` in [l:r] in O(logN), or -1 if it doesn't exist
    def queryEarliestGTENum(self, l, r, numToBeat) -> int:
        return self._recurseGetEarliestGTENum(0, 0, self.n - 1, l, r, numToBeat)

    # Query the latest index of a number >= `num` in [l:r] in O(logN), or -1 if it doesn't exist
    def queryLatestGTENum(self, l, r, numToBeat) -> int:
        return self._recurseGetLatestGTENum(0, 0, self.n - 1, l, r, numToBeat)

    # Query the earliest index of a number <= `num` in [l:r] in O(logN), or -1 if it doesn't exist
    def queryEarliestLTENum(self, l, r, numToBeat) -> int:
        return self._recurseGetEarliestLTENum(0, 0, self.n - 1, l, r, numToBeat)

    # Query the latest index of a number <= `num` in [l:r] in O(logN), or -1 if it doesn't exist
    def queryLatestLTENum(self, l, r, numToBeat) -> int:
        return self._recurseGetLatestLTENum(0, 0, self.n - 1, l, r, numToBeat)