class Seg:
    def __init__(self, A):
        self.A = A
        self.n = len(A)
        self.tree = [0] * (4 * self.n) # holds max
        self._build(1, 0, self.n - 1)
    def _build(self, nodeI, tl, tr):
        if tl == tr:
            self.tree[nodeI] = self.A[tl]
            return
        tm = (tl + tr) // 2
        self._build(2 * nodeI, tl, tm)
        self._build(2 * nodeI + 1, tm + 1, tr)
        self._pull(nodeI)
    def _pull(self, nodeI):
        self.tree[nodeI] = self._agg(self.tree[2*nodeI],self.tree[2*nodeI+1])
    def _agg(self, l, r):
        return max(l, r)
    def _pointFill(self, nodeI, tl, tr, pos):
        if tl == tr:
            self.tree[nodeI] = 0
            return
        tm = (tl + tr) // 2
        if pos <= tm:
            self._pointFill(2 * nodeI, tl, tm, pos)
        else:
            self._pointFill(2 * nodeI + 1, tm + 1, tr, pos)
        self._pull(nodeI)
    def pointFill(self, pos):
        self._pointFill(1, 0, self.n - 1, pos)
    def queryLeftmostGteX(self, x):
        return self._walk(1, 0, self.n - 1, x)
    def _walk(self, nodeI, tl, tr, x):
        if tl == tr:
            return tl if self.tree[nodeI] >= x else None
        tm = (tl + tr) // 2
        lmax = self.tree[2*nodeI]
        if lmax >= x:
            return self._walk(2*nodeI,tl,tm,x)
        rmax = self.tree[2*nodeI+1]
        if rmax >= x:
            return self._walk(2*nodeI+1,tm+1,tr,x)
        return None

class Solution:
    def numOfUnplacedFruits(self, fruits: List[int], baskets: List[int]) -> int:
        s = Seg(baskets)
        res = 0
        for f in fruits:
            qval = s.queryLeftmostGteX(f)
            if qval is None:
                continue
            res += 1
            s.pointFill(qval)
        return len(fruits) - res