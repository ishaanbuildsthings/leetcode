# ______________________________________________________________________
# TEMPLATE - max segment tree

# FUNCTIONS:
# Query max of range O(logN)
# Update value O(logN)

# General reqs:
# An array of numbers

# Complexities:
# Build: O(n)
# Space: O(n)

class MaxSegmentTree:

    def __init__(self, data):
        self.n = len(data)
        self.data = data
        self.tree = [None] * 4 * self.n
        self._build(0, 0, self.n - 1)

    # i is the index of the vertex we are at, tl is the left boundary, tr is the right boundary
    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = self.data[tl]
            return
        tm = (tr + tl) // 2
        self._build(2*i + 1, tl, tm)
        self._build(2*i + 2, tm + 1, tr)
        self.tree[i] = max(self.tree[2*i + 1], self.tree[2*i + 2])

    # tl and tr are the boundaries of the current node
    # l and r are boundaries we need a max from, in the current node
    def _queryMaxRecurse(self, i, tl, tr, l, r):
        # simplify the code
        if l > r:
            return float('-inf')
        # perfect match
        if l == tl and r == tr:
            return self.tree[i]
        tm = (tr + tl) // 2 # calculate the middle of our node, basically get the two children
        maxLeft = self._queryMaxRecurse(2*i + 1, tl, tm, l, min(r, tm))
        maxRight = self._queryMaxRecurse(2*i + 2, tm + 1, tr, max(l, tm + 1), r)
        return max(maxLeft, maxRight)

    def _updateRecurse(self, i, tl, tr, posToBeUpdated, newVal):
        if tl == tr:
            self.tree[i] = newVal
            return

        tm = (tr + tl) // 2
        if posToBeUpdated <= tm:
            self._updateRecurse(2*i + 1, tl, tm, posToBeUpdated, newVal)
        else:
            self._updateRecurse(2*i + 2, tm + 1, tr, posToBeUpdated, newVal)
        self.tree[i] = max(self.tree[2*i + 1], self.tree[2*i + 2])

    ################################## PUBLIC METHODS START HERE ##################################

    # Update the value of a cell in the segment tree in O(logN)
    def update(self, index, newVal) -> None:
        self._updateRecurse(0, 0, self.n - 1, index, newVal)

    # Query the max from [l:r] in O(logN)
    def queryMax(self, l, r) -> int:
        return self._queryMaxRecurse(0, 0, self.n - 1, l, r)
