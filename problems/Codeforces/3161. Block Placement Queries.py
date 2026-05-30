class Node:
    def __init__(self, leftWall, rightWall, width, tl, tr):
        self.leftWall = leftWall
        self.rightWall = rightWall
        self.width = width
        self.tl = tl
        self.tr = tr

class Seg:
    def __init__(self, sz):
        self.n = sz
        self.tree = [None] * (4 * (self.n + 1))
        self._build(1, 0, self.n)
    
    def _build(self, nodeI, tl, tr):
        if tl == tr:
            self.tree[nodeI] = Node(None, None, 0, tl, tr)
            return
        tm = (tl + tr) // 2
        self._build(2 * nodeI, tl, tm)
        self._build(2 * nodeI + 1, tm + 1, tr)
        self._pull(nodeI)
    
    def _setWall(self, nodeI, tl, tr, pos):
        if tl == tr:
            self.tree[nodeI] = Node(tl, tl, 0, tl, tr)
            return
        tm = (tl + tr) // 2
        if pos <= tm:
            self._setWall(2 * nodeI, tl, tm, pos)
        else:
            self._setWall(2 * nodeI + 1, tm + 1, tr, pos)
        self._pull(nodeI)
    
    def _agg(self, v1, v2):
        ntl = v1.tl
        ntr = v2.tr
        nleftWall = v1.leftWall if v1.leftWall is not None else v2.leftWall
        nrightWall = v2.rightWall if v2.rightWall is not None else v1.rightWall
        nwidth = max(v1.width, v2.width)
        # cross spanning
        leftWall = v1.rightWall if v1.rightWall is not None else v1.tl
        rightWall = v2.leftWall if v2.leftWall is not None else v2.tr
        gap = rightWall - leftWall
        nwidth = max(nwidth, gap)
        return Node(nleftWall, nrightWall, nwidth, ntl, ntr)
    
    def _pull(self, nodeI):
        self.tree[nodeI] = self._agg(self.tree[2 * nodeI], self.tree[2 * nodeI + 1])
    
    def setWall(self, pos):
        self._setWall(1, 0, self.n, pos)
    
    def _queryLarge(self, nodeI, tl, tr, ql, qr):
        # fully inside
        if ql <= tl and qr >= tr:
            return self.tree[nodeI]
        
        tm = (tl + tr) // 2
        if qr <= tm:
            left = self._queryLarge(2 * nodeI, tl, tm, ql, qr)
            return left
        elif ql >= tm + 1:
            right = self._queryLarge(2 * nodeI + 1, tm + 1, tr, ql, qr)
            return right
        left = self._queryLarge(2 * nodeI, tl, tm, ql, qr)
        right = self._queryLarge(2 * nodeI + 1, tm + 1, tr, ql, qr)
        return self._agg(left, right)

    def queryLarge(self, x):
        return self._queryLarge(1, 0, self.n, 0, x)

class Solution:
    def getResults(self, queries: List[List[int]]) -> List[bool]:
        mx = 0
        for q in queries:
            if q[0] == 1:
                mx = max(mx, q[-1])
            else:
                mx = max(mx, q[-2])
        
        st = Seg(mx + 10)
        res = []
        for q in queries:
            if q[0] == 1:
                st.setWall(q[-1])
            else:
                node = st.queryLarge(q[1])
                allowed = node.width
                res.append(allowed >= q[2])
        
        return res