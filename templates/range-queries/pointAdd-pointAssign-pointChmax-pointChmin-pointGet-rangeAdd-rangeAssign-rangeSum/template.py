# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeSum
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeAssign: log(N)
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: pow2-iterative
#   node: sm[4*N]
#   tags: add[2*N] asg[2*N] hasAsg[2*N]
#   other: none
#   note: arrays are 2*size, size the next power of two >= n; a node's tag is either "assign v" (later adds fold into v) or "add d"
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/lazy/RangeAddRangeAssignRangeSum.cpp

# Range add + range assign + range sum (no mod), plus point ops. All indices 0-based, ranges inclusive [l, r].
# Iterative lazy tree over a power-of-two layout. Tags do not commute (add then assign != assign then add), so an
# update first pushes every tag on the two boundary root-to-leaf paths, then tags the O(log N) covering nodes, then
# recomputes the boundary paths bottom-up. A tag is either "assign v" or "add d"; an add landing on an assign tag
# just shifts v.


class AddAssignSumTree:
    __slots__ = ("n", "size", "H", "sm", "add", "asg", "hasAsg")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        size, H = 1, 0
        while size < max(n, 1):
            size <<= 1
            H += 1
        self.size, self.H = size, H
        sm = self.sm = [0] * (2 * size)
        sm[size:size + n] = arr
        for x in range(size - 1, 0, -1):
            sm[x] = sm[2 * x] + sm[2 * x + 1]
        self.add = [0] * size
        self.asg = [0] * size
        self.hasAsg = [False] * size

    # node x covers `length` slots
    def _apply(self, x, length, isAsg, v):
        if isAsg:
            self.sm[x] = v * length
            if x < self.size:
                self.hasAsg[x] = True
                self.asg[x] = v
                self.add[x] = 0
        else:
            self.sm[x] += v * length
            if x < self.size:
                if self.hasAsg[x]:
                    self.asg[x] += v
                else:
                    self.add[x] += v

    # push node x's tag into its two children, which cover childLen slots each
    def _push(self, x, childLen):
        if self.hasAsg[x]:
            v = self.asg[x]
            self._apply(2 * x, childLen, True, v)
            self._apply(2 * x + 1, childLen, True, v)
            self.hasAsg[x] = False
        elif self.add[x]:
            v = self.add[x]
            self._apply(2 * x, childLen, False, v)
            self._apply(2 * x + 1, childLen, False, v)
            self.add[x] = 0

    def _pushToRoot(self, p):
        for s in range(self.H, 0, -1):
            self._push(p >> s, 1 << (s - 1))

    # a node that got tagged during the update keeps its own tag's effect
    def _recomputeToRoot(self, p):
        sm, add, asg, hasAsg = self.sm, self.add, self.asg, self.hasAsg
        p >>= 1
        length = 2
        while p:
            if hasAsg[p]:
                sm[p] = asg[p] * length
            else:
                sm[p] = sm[2 * p] + sm[2 * p + 1] + add[p] * length
            p >>= 1
            length <<= 1

    def _update(self, l, r, isAsg, v):
        if l > r:
            return
        l0, r0 = l + self.size, r + self.size
        self._pushToRoot(l0)
        self._pushToRoot(r0)
        lo, hi, length = l0, r0 + 1, 1
        while lo < hi:
            if lo & 1:
                self._apply(lo, length, isAsg, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._apply(hi, length, isAsg, v)
            lo >>= 1
            hi >>= 1
            length <<= 1
        self._recomputeToRoot(l0)
        self._recomputeToRoot(r0)

    # O(logN) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        self._update(l, r, False, v)

    # O(logN) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        self._update(l, r, True, v)

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        if l > r:
            return 0
        l += self.size
        r += self.size
        self._pushToRoot(l)
        self._pushToRoot(r)
        sm = self.sm
        res = 0
        r += 1
        while l < r:
            if l & 1:
                res += sm[l]
                l += 1
            if r & 1:
                r -= 1
                res += sm[r]
            l >>= 1
            r >>= 1
        return res

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.size
        self._pushToRoot(p)
        return self.sm[p]

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        self._update(i, i, True, val)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self._update(i, i, False, delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
