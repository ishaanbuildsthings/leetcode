class MinSegTree:
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)

        size = 1
        while size < self.n:
            size <<= 1
        self.size = size

        tree = [float("inf")] * (2 * size)
        base = size
        for i, v in enumerate(arr):
            tree[base + i] = v
        for idx in range(size - 1, 0, -1):
            left = tree[idx << 1]
            right = tree[(idx << 1) | 1]
            tree[idx] = left if left <= right else right
        self.tree = tree

    def _queryHalfOpen(self, l, r):
        tree = self.tree
        l += self.size
        r += self.size
        ans = float("inf")
        while l < r:
            if l & 1:
                v = tree[l]
                ans = v if v <= ans else ans
                l += 1
            if r & 1:
                r -= 1
                v = tree[r]
                ans = v if v <= ans else ans
            l >>= 1
            r >>= 1
        return ans

    def queryMin(self, l, r):
        return self._queryHalfOpen(l, r + 1)

    def pointUpdateAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        tree = self.tree
        pos = self.size + index
        tree[pos] = newVal
        pos >>= 1
        while pos:
            left = tree[pos << 1]
            right = tree[(pos << 1) | 1]
            tree[pos] = left if left <= right else right
            pos >>= 1

    def leftmostLteX(self, l, r, x):
        tree = self.tree
        size = self.size
        left_cands = []
        right_cands = []
        lo = l + size
        hi = r + 1 + size
        while lo < hi:
            if lo & 1:
                left_cands.append(lo)
                lo += 1
            if hi & 1:
                hi -= 1
                right_cands.append(hi)
            lo >>= 1
            hi >>= 1
        candidates = left_cands + right_cands[::-1]
        for node in candidates:
            if tree[node] > x:
                continue
            while node < size:
                left_child = node << 1
                if tree[left_child] <= x:
                    node = left_child
                else:
                    node = (node << 1) | 1
            return node - size
        return -1

    def rightmostLteX(self, l, r, x):
        tree = self.tree
        size = self.size
        left_cands = []
        right_cands = []
        lo = l + size
        hi = r + 1 + size
        while lo < hi:
            if lo & 1:
                left_cands.append(lo)
                lo += 1
            if hi & 1:
                hi -= 1
                right_cands.append(hi)
            lo >>= 1
            hi >>= 1
        candidates = right_cands + left_cands[::-1]
        for node in candidates:
            if tree[node] > x:
                continue
            while node < size:
                right_child = (node << 1) | 1
                if tree[right_child] <= x:
                    node = right_child
                else:
                    node = node << 1
            return node - size
        return -1


class SumSegTree:
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)

        size = 1
        while size < self.n:
            size <<= 1
        self.size = size

        tree = [0] * (2 * size)
        base = size
        for i, v in enumerate(arr):
            tree[base + i] = v
        for idx in range(size - 1, 0, -1):
            tree[idx] = tree[idx << 1] + tree[(idx << 1) | 1]
        self.tree = tree

    def _queryHalfOpen(self, l, r):
        tree = self.tree
        l += self.size
        r += self.size
        ans = 0
        while l < r:
            if l & 1:
                ans += tree[l]
                l += 1
            if r & 1:
                r -= 1
                ans += tree[r]
            l >>= 1
            r >>= 1
        return ans

    def querySum(self, l, r):
        return self._queryHalfOpen(l, r + 1)

    def pointUpdateAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        tree = self.tree
        pos = self.size + index
        tree[pos] = newVal
        pos >>= 1
        while pos:
            tree[pos] = tree[pos << 1] + tree[(pos << 1) | 1]
            pos >>= 1
# to gather we need to find the earliest row with >= k spots
class BookMyShow:

    def __init__(self, n: int, m: int):
        self.ROWS = n
        self.WIDTH = m
        self.firstEmpty = 0 # current row which is still empty

        # last unused
        self.latest = [0] * n

        self.st = MinSegTree(self.latest)
        self.seats = [m] * self.ROWS
        self.sumst = SumSegTree(self.seats) # how many seats are left
        

    def gather(self, k: int, maxRow: int) -> List[int]:
        upperAllowed = self.WIDTH - k
        earliestRow = self.st.leftmostLteX(0, maxRow, upperAllowed)
        if earliestRow == -1:
            return []
        currLatest = self.latest[earliestRow]
        self.st.pointUpdateAndMutateArray(earliestRow, currLatest + k)
        
    
        self.sumst.pointUpdateAndMutateArray(earliestRow, self.sumst.querySum(earliestRow, earliestRow) - k)
        return [earliestRow, currLatest]


    def scatter(self, k: int, maxRow: int) -> bool:
        currSum = self.sumst.querySum(0, maxRow)
        if currSum < k:
            return False
        remainToPlace = k
        for row in range(self.firstEmpty, maxRow + 1):
            currSpots = self.seats[row]
            placed = min(remainToPlace, currSpots)
            remainToPlace -= placed
            self.sumst.pointUpdateAndMutateArray(row, currSpots - placed)
            newRemain = currSpots - placed
            lastUnused = self.WIDTH - newRemain
            self.st.pointUpdateAndMutateArray(row, lastUnused)
            if newRemain == 0:
                self.firstEmpty += 1
            # vital pruning
            if remainToPlace == 0:
                break
        return True




        


# Your BookMyShow object will be instantiated and called as such:
# obj = BookMyShow(n, m)
# param_1 = obj.gather(k,maxRow)
# param_2 = obj.scatter(k,maxRow)