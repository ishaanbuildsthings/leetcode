# _____________________________________________________
# TEMPLATE
# TODO FINAL: build fast iterative, efficient memory allocation, test updates

# FUNCTIONS:
# Query sum of range O(logN)
# Update value O(logN)

# General reqs:
# An array of numbers

# Complexities:
# Build: O(n)
# Space: O(n)

# FUNCTIONS:
# Query sum of range O(logN)
# Update value O(logN)

# General reqs:
# An array of numbers

# Complexities:
# Build: O(n)
# Space: O(n)

IDENTITY = 0 # combine or sum of (a, IDENTITY) is always a
class SumSegmentTree:

    def __init__(self, data):
        self.n = len(data)
        self.data = data
        self.tree = [None] * 4 * self.n
        self._build(1, 0, self.n - 1)

    # returns the data we hold the ST node of width 1, for instance in max + counts we might hold (val, 1)
    def _basefn(self, val):
        return val

    # i is the index of the vertex we are at, tl is the left boundary, tr is the right boundary
    def _build(self, i, tl, tr):
        # base case
        if tl == tr:
            self.tree[i] = self._basefn(self.data[tl])
            return
        tm = (tr + tl) // 2
        self._build(2*i, tl, tm)
        self._build(2*i + 1, tm + 1, tr)
        self.tree[i] = self._combine(self.tree[2*i], self.tree[2*i + 1])

    # takes the result of two children ST nodes (regardless of if they're the value at that node, or some computed value based on l and r bounds), and merges them to get a new parent value
    def _combine(self, a, b):
        return a + b

    # tl and tr are the boundaries of the current node
    # l and r are boundaries we need a sum from, we compare to the current node
    def _queryRecurse(self, i, tl, tr, l, r):
        # if we are contained
        if tl >= l and tr <= r:
            return self.tree[i]

        # if we have no intersection
        if tr < l or tl > r:
            return IDENTITY

        tm = (tr + tl) // 2 # calculate the middle of our node, basically get the two children
        sumLeft = self._queryRecurse(2*i, tl, tm, l, r)
        sumRight = self._queryRecurse(2*i + 1, tm + 1, tr, l, r)
        return self._combine(sumLeft, sumRight)

    def _updateRecurse(self, i, tl, tr, posToBeUpdated, newVal):
        if tl == tr:
            self.tree[i] = self._basefn(newVal)
            return

        tm = (tr + tl) // 2
        if posToBeUpdated <= tm:
            self._updateRecurse(2*i, tl, tm, posToBeUpdated, newVal)
        else:
            self._updateRecurse(2*i + 1, tm + 1, tr, posToBeUpdated, newVal)

        self.tree[i] = self._combine(self.tree[2*i], self.tree[2*i + 1]) # get the new sum irrespective of which side was updated

    ################################## PUBLIC METHODS START HERE ##################################

    # Update the value of a cell in the segment tree in O(logN)
    def update(self, index, newVal) -> None:
        self._updateRecurse(1, 0, self.n - 1, index, newVal)

    # Query the sum from [l:r] in O(logN)
    def querySum(self, l, r) -> int:
        return self._queryRecurse(1, 0, self.n - 1, l, r)
