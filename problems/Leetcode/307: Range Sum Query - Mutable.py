class SegTree:
    def __init__(self, data):
        self.n = len(data)
        self.data = data
        self.tree = [None] * 4 * self.n
        self._build(0, 0, self.n - 1)
    
    def _build(self, i, tl, tr):
        # base case
        if tl == tr:
            self.tree[i] = self.data[tl]
            return
        tm = (tr + tl) // 2
        self._build(2*i + 1, tl, tm)
        self._build(2*i + 2, tm + 1, tr)
        self.tree[i] = self.tree[2*i + 1] + self.tree[2*i + 2]
    
    # solves a subproblem at a given ST node
    def _queryRecurse(self, i, tl, tr, l, r):
        # clean code trick
        if l > r:
            return 0 # neutral value

        # base case
        if tl == tr:
            return self.tree[i]

        # filled
        if tl == l and tr == r:
            return self.tree[i]

        tm = (tr + tl) // 2

        leftSum = self._queryRecurse(2*i + 1, tl, tm, l, min(tm, r))
        rightSum = self._queryRecurse(2*i + 2, tm + 1, tr, max(tm + 1, l), r)
        return leftSum + rightSum

    def _updateRecurse(self, i, tl, tr, pos, newVal):
        # base case
        if tl == pos == tr:
            self.tree[i] = newVal
            return
        
        tm = (tr + tl) // 2
        
        if pos <= tm:
            self._updateRecurse(2*i + 1, tl, tm, pos, newVal)
        else:
            self._updateRecurse(2*i + 2, tm + 1, tr, pos, newVal)
        
        self.tree[i] = self.tree[2*i + 1] + self.tree[2*i + 2] # update the current ST node regardless of which child was updated

    def update(self, index, val):
        self._updateRecurse(0, 0, self.n - 1, index, val)

    def sumQuery(self, l, r):
        return self._queryRecurse(0, 0, self.n - 1, l, r)




class NumArray:

    def __init__(self, nums: List[int]):
        self.ST = SegTree(nums)

    def update(self, index: int, val: int) -> None:
        self.ST.update(index, val)

    def sumRange(self, left: int, right: int) -> int:
        return self.ST.sumQuery(left, right)


# Your NumArray object will be instantiated and called as such:
# obj = NumArray(nums)
# obj.update(index,val)
# param_2 = obj.sumRange(left,right)