from math import inf

class SegmentTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.arr = arr[:]
        self.tree = [None] * (4 * self.n)
        if self.n > 0:
            self._build(1, 0, self.n - 1)

    def _combine(self, leftNode, rightNode):
        leftMinVal, leftMinIdx, leftInfCount = leftNode
        rightMinVal, rightMinIdx, rightInfCount = rightNode

        if leftMinVal <= rightMinVal:
            minVal, minIdx = leftMinVal, leftMinIdx
        else:
            minVal, minIdx = rightMinVal, rightMinIdx

        return (minVal, minIdx, leftInfCount + rightInfCount)

    def _makeLeaf(self, val, idx):
        infCount = 1 if val == inf else 0
        return (val, idx, infCount)

    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = self._makeLeaf(self.arr[tl], tl)
            return

        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm)
        self._build(2 * i + 1, tm + 1, tr)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1])

    def _queryRecurse(self, i, tl, tr, l, r):
        if l == tl and r == tr:
            return self.tree[i]

        tm = (tl + tr) // 2

        if r <= tm:
            return self._queryRecurse(2 * i, tl, tm, l, r)
        if l > tm:
            return self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)

        leftResult = self._queryRecurse(2 * i, tl, tm, l, tm)
        rightResult = self._queryRecurse(2 * i + 1, tm + 1, tr, tm + 1, r)
        return self._combine(leftResult, rightResult)

    def _updateRecurse(self, i, tl, tr, pos):
        if tl == tr:
            self.tree[i] = self._makeLeaf(self.arr[tl], tl)
            return

        tm = (tl + tr) // 2
        if pos <= tm:
            self._updateRecurse(2 * i, tl, tm, pos)
        else:
            self._updateRecurse(2 * i + 1, tm + 1, tr, pos)

        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1])

    def updateAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        self._updateRecurse(1, 0, self.n - 1, index)

    def query(self, l, r):
        return self._queryRecurse(1, 0, self.n - 1, l, r)

    def countInf(self, l, r):
        return self.query(l, r)[2]

    def rangeMin(self, l, r):
        minVal, minIdx, _ = self.query(l, r)
        return (minVal, minIdx)

class Solution:
    def countOperationsToEmptyArray(self, nums: List[int]) -> int:
        st = SegmentTree(nums)
        head = res = 0
        n = len(nums)
        for _ in range(n):
            v, smallestI, _ = st.query(0, n - 1)
            if smallestI >= head:
                _, _, infinities = st.query(head, smallestI)
                ops = smallestI - head
                ops -= infinities
                res += ops
            else:
                opsToFront = n - head
                _, _, infinitiesOne = st.query(head, n - 1)
                opsTwo = smallestI
                _, _, infinitiesTwo = st.query(0, smallestI)
                ops = opsToFront + opsTwo - infinitiesOne - infinitiesTwo
                res += ops
            head = (smallestI + 1) % n
            st.updateAndMutateArray(smallestI, inf)
        return res + n # count the removals