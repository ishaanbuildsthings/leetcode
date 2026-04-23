from bisect import lower_bound as _lb, upper_bound as _ub
from bisect import bisect_left, bisect_right

class MergeSortTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [None] * (4 * self.n)  # each node stores a sorted list of its elements
        self.cntL = [None] * (4 * self.n)  # cntL[nodeI][j] = # of first j elements in tree[nodeI] from left child, j=0 considers NO elements, so exclusive prefix
        self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, nodeI, tl, tr):
        if tl == tr:
            self.tree[nodeI] = [arr[tl]]
            self.cntL[nodeI] = [0, 1]
            return
        mid = (tl + tr) // 2
        self._build(arr, 2 * nodeI, tl, mid)
        self._build(arr, 2 * nodeI + 1, mid + 1, tr)

        L = self.tree[2 * nodeI]
        R = self.tree[2 * nodeI + 1]
        sz = len(L) + len(R)
        merged = [0] * sz
        cnt = [0] * (sz + 1)
        cnt[0] = 0
        li = ri = idx = 0
        while li < len(L) and ri < len(R):
            if L[li] <= R[ri]:
                merged[idx] = L[li]
                li += 1
                cnt[idx + 1] = cnt[idx] + 1
            else:
                merged[idx] = R[ri]
                ri += 1
                cnt[idx + 1] = cnt[idx]
            idx += 1
        while li < len(L):
            merged[idx] = L[li]
            li += 1
            cnt[idx + 1] = cnt[idx] + 1
            idx += 1
        while ri < len(R):
            merged[idx] = R[ri]
            ri += 1
            cnt[idx + 1] = cnt[idx]
            idx += 1
        self.tree[nodeI] = merged
        self.cntL[nodeI] = cnt

    # --- count >= x ---

    # p = number of elements < x in this node (cascaded from parent)
    def _countGteX(self, nodeI, tl, tr, ql, qr, p):
        if ql > tr or qr < tl:
            return 0
        if ql <= tl and tr <= qr:
            return len(self.tree[nodeI]) - p
        mid = (tl + tr) // 2
        leftP = self.cntL[nodeI][p]
        rightP = p - leftP
        return self._countGteX(2 * nodeI, tl, mid, ql, qr, leftP) + \
               self._countGteX(2 * nodeI + 1, mid + 1, tr, ql, qr, rightP)

    # O(log n) — count elements >= x in [ql, qr]
    # One binary search at the root for lower_bound(x), then fractional cascading passes p down in O(1) per level
    def countGteX(self, ql, qr, x):
        p = bisect_left(self.tree[1], x)  # # elements < x in entire tree
        return self._countGteX(1, 0, self.n - 1, ql, qr, p)

    # --- count <= x ---

    # p = number of elements <= x in this node (cascaded from parent)
    def _countLteX(self, nodeI, tl, tr, ql, qr, p):
        if ql > tr or qr < tl:
            return 0
        if ql <= tl and tr <= qr:
            return p
        mid = (tl + tr) // 2
        leftP = self.cntL[nodeI][p]
        rightP = p - leftP
        return self._countLteX(2 * nodeI, tl, mid, ql, qr, leftP) + \
               self._countLteX(2 * nodeI + 1, mid + 1, tr, ql, qr, rightP)

    # O(log n) — count elements <= x in [ql, qr]
    # One binary search at the root for upper_bound(x), then fractional cascading passes p down in O(1) per level
    def countLteX(self, ql, qr, x):
        p = bisect_right(self.tree[1], x)  # # elements <= x in entire tree
        return self._countLteX(1, 0, self.n - 1, ql, qr, p)

    # O(log n) — count elements in value range [valLow, valHigh] (inclusive) in index range [ql, qr]
    # Computed as countLteX(valHigh) - countLteX(valLow - 1)
    def countInRange(self, ql, qr, valLow, valHigh):
        return self.countLteX(ql, qr, valHigh) - self.countLteX(ql, qr, valLow - 1)

    # --- find k-th element >= x by position ---

    # returns (position, gteCount) where:
    #   position = array index of the k-th element >= x found in this subtree's overlap with [ql,qr], or -1 if not enough
    #   gteCount = how many elements >= x were found in this subtree's overlap with [ql,qr] (only meaningful when position == -1, used to adjust kRemaining for the right subtree)
    # p = number of elements < x in this node (cascaded)
    # kRemaining = how many more elements >= x we still need to find (decreases as left subtrees contribute partial counts)
    def _findKthGteX(self, nodeI, tl, tr, ql, qr, kRemaining, p):
        if ql > tr or qr < tl:
            return (-1, 0)
        gteInNode = len(self.tree[nodeI]) - p
        if ql <= tl and tr <= qr:
            if gteInNode < kRemaining:
                return (-1, gteInNode)  # not enough in this entire subtree, pass count up
            # enough elements exist in this subtree, but we don't know the exact index yet — must recurse to a leaf
            if tl == tr:
                return (tl, 1)  # reached a leaf, this is the exact position
        mid = (tl + tr) // 2
        leftP = self.cntL[nodeI][p]
        rightP = p - leftP
        leftPos, leftGteCount = self._findKthGteX(2 * nodeI, tl, mid, ql, qr, kRemaining, leftP)
        if leftPos != -1:
            return (leftPos, 0)  # found answer in left subtree, 0 is a dummy
        rightPos, rightGteCount = self._findKthGteX(2 * nodeI + 1, mid + 1, tr, ql, qr, kRemaining - leftGteCount, rightP)
        if rightPos != -1:
            return (rightPos, 0)  # found answer in right subtree, 0 is a dummy
        return (-1, leftGteCount + rightGteCount)  # answer not in this subtree, pass total count up

    # O(log n) — find the array index (position) of the k-th element >= x in [ql, qr] (1-indexed k, scanning left to right)
    # Returns -1 if fewer than k elements >= x exist in range
    # Note: this returns a POSITION (array index), not a VALUE
    # One binary search at root, then walks down with fractional cascading, going left first to find the earliest position
    def findKthGteX(self, ql, qr, k, x):
        p = bisect_left(self.tree[1], x)  # # elements < x in entire tree
        return self._findKthGteX(1, 0, self.n - 1, ql, qr, k, p)[0]

    # --- find k-th element <= x by position ---

    # returns (position, lteCount) where:
    #   position = array index of the k-th element <= x found in this subtree's overlap with [ql,qr], or -1 if not enough
    #   lteCount = how many elements <= x were found in this subtree's overlap with [ql,qr] (only meaningful when position == -1, used to adjust kRemaining for the right subtree)
    # p = number of elements <= x in this node (cascaded)
    # kRemaining = how many more elements <= x we still need to find (decreases as left subtrees contribute partial counts)
    def _findKthLteX(self, nodeI, tl, tr, ql, qr, kRemaining, p):
        if ql > tr or qr < tl:
            return (-1, 0)
        lteInNode = p
        if ql <= tl and tr <= qr:
            if lteInNode < kRemaining:
                return (-1, lteInNode)  # not enough in this entire subtree, pass count up
            # enough elements exist in this subtree, but we don't know the exact index yet — must recurse to a leaf
            if tl == tr:
                return (tl, 1)  # reached a leaf, this is the exact position
        mid = (tl + tr) // 2
        leftP = self.cntL[nodeI][p]
        rightP = p - leftP
        leftPos, leftLteCount = self._findKthLteX(2 * nodeI, tl, mid, ql, qr, kRemaining, leftP)
        if leftPos != -1:
            return (leftPos, 0)  # found answer in left subtree, 0 is a dummy
        rightPos, rightLteCount = self._findKthLteX(2 * nodeI + 1, mid + 1, tr, ql, qr, kRemaining - leftLteCount, rightP)
        if rightPos != -1:
            return (rightPos, 0)  # found answer in right subtree, 0 is a dummy
        return (-1, leftLteCount + rightLteCount)  # answer not in this subtree, pass total count up

    # O(log n) — find the array index (position) of the k-th element <= x in [ql, qr] (1-indexed k, scanning left to right)
    # Returns -1 if fewer than k elements <= x exist in range
    # Note: this returns a POSITION (array index), not a VALUE
    # One binary search at root, then walks down with fractional cascading, going left first to find the earliest position
    def findKthLteX(self, ql, qr, k, x):
        p = bisect_right(self.tree[1], x)  # # elements <= x in entire tree
        return self._findKthLteX(1, 0, self.n - 1, ql, qr, k, p)[0]