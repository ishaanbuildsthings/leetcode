# TEMPLATE BY https://github.com/agrawalishaan
# You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

# Complexities:
# Build: O(n)
# Space: O(n)
# Query/Update: O(log N)

# baseFn: (val, i) => ...
# combineFn: (leftVal, rightVal, leftLeftIdx, leftRightIdx, rightLeftIdx, rightRightIdx) => ...
# tupleNametags: If baseFn returns a tuple, we can supply nametags for each value, like ('min', 'max'), used for debugging

class SegmentTree:
    def __init__(self, arr, baseFn, combine):
        self.n = len(arr)
        self.arr = arr
        self.tree = [None] * (4 * self.n)
        self._combine = combine
        self._baseFn = baseFn
        self._build(1, 0, self.n - 1)

    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = self._baseFn(self.arr[tl], tl)
            return
        tm = (tr + tl) // 2
        self._build(2 * i, tl, tm)
        self._build(2 * i + 1, tm + 1, tr)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1], tl, tm, tm + 1, tr)

    def _queryRecurse(self, i, tl, tr, l, r):
        # our node is fully in range
        if l <= tl and tr <= r:
            return self.tree[i]

        tm = (tl + tr) // 2

        # the left child is not in range
        if l > tm:
            return self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        # the right child is not in range
        elif r < tm + 1:
            return self._queryRecurse(2 * i, tl, tm, l, r)

        leftResult = self._queryRecurse(2 * i, tl, tm, l, r)
        rightResult = self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        combinedResult = self._combine(leftResult, rightResult, max(l, tl), min(tm, r), max(l, tm + 1), min(r, tr))
        return combinedResult

    def _pointUpdateRecurse(self, i, tl, tr, posToBeUpdated):
        if tl == tr:
            self.tree[i] = self._baseFn(self.arr[tl], tl)
            return
        tm = (tl + tr) // 2
        if posToBeUpdated <= tm:
            self._pointUpdateRecurse(2 * i, tl, tm, posToBeUpdated)
        else:
            self._pointUpdateRecurse(2 * i + 1, tm + 1, tr, posToBeUpdated)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1], tl, tm, tm + 1, tr)

    def pointUpdateAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        self._pointUpdateRecurse(1, 0, self.n - 1, index)


    def query(self, l, r):
        return self._queryRecurse(1, 0, self.n - 1, l, r)
