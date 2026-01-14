# ______________________________________________________________________
# TEMPLATE - count and kth segment tree, tells us how many times a certain number appears in a range, and the index of the kth instance of that number in a range, only works for one number at build time
# TODO: test

# FUNCTIONS:
# Query number of times a fixed number appears in range O(logN)
# Query index of the kth instance of a fixed number in range O(logN)
# Update value O(logN)

# General reqs:
# An array of data

# Complexities:
# Build: O(n)
# Space: O(n)

class CountAndKthIndexSegmentTree:

    def __init__(self, data, number):
        self.number = number
        self.n = len(data)
        self.data = data
        self.tree = [None] * 4 * self.n  # each element of the tree will hold a count for how many times the fixed number appears in that range
        self._build(0, 0, self.n - 1)

    # i is the index of the vertex we are at, tl is the left boundary, tr is the right boundary
    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = 1 if self.data[tl] == self.number else 0
            return
        tm = (tr + tl) // 2
        self._build(2*i + 1, tl, tm)
        self._build(2*i + 2, tm + 1, tr)
        self.tree[i] = self.tree[2*i + 1] + self.tree[2*i + 2]

    # tl and tr are the boundaries of the current node
    # l and r are boundaries we need a count from, in the current node
    def _queryRecurse(self, i, tl, tr, l, r):
        # simplify the code
        if l > r:
            return 0
        # perfect match
        if l == tl and r == tr:
            return self.tree[i]

        tm = (tr + tl) // 2 # calculate the middle of our node, basically get the two children
        # TODO: do we add pruning if that range doesnt have any of the number at all? what about for other segment trees?
        leftCount = self._queryRecurse(2*i + 1, tl, tm, l, min(r, tm))
        rightCount = self._queryRecurse(2*i + 2, tm + 1, tr, max(l, tm + 1), r)
        return leftCount + rightCount

    def _updateRecurse(self, i, tl, tr, posToBeUpdated, newVal):
        if tl == tr:
            self.tree[i] = 1 if newVal == self.number else 0
            return

        tm = (tr + tl) // 2
        if posToBeUpdated <= tm:
            self._updateRecurse(2*i + 1, tl, tm, posToBeUpdated, newVal)
        else:
            self._updateRecurse(2*i + 2, tm + 1, tr, posToBeUpdated, newVal)
        self.tree[i] = self.tree[2*i + 1] + self.tree[2*i + 2]

    ################################## PUBLIC METHODS START HERE ##################################

    # Update the value of a cell in the segment tree in O(logN)
    def update(self, index, newVal) -> None:
        self._updateRecurse(0, 0, self.n - 1, index, newVal)

    def queryCount(self, l, r) -> int:
        return self._queryRecurse(0, 0, self.n - 1, l, r)


"dbca"
2
"gggg"
4
"aann"
2
"gh"
1
"dah"
3