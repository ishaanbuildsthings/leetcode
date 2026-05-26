# TEMPLATE FROM MY GITHUB: ishaanbuildsthings
class FenwickMedianSet:
    """
    Multiset over non-negative integers in [0, maxVal].
    Supports add, remove, kth element, median, sum, and cost-to-target queries.
    """
    def __init__(self, maxVal):
        self.n = maxVal
        # Two Fenwicks: one tracks counts, one tracks sums of values
        self.cntTree = [0] * (self.n + 2)
        self.sumTree = [0] * (self.n + 2)
        self.cnt = [0] * (self.n + 1)
        self.size = 0
        self.totalSum = 0
    
    def _updateCnt(self, i, delta):
        i += 1
        while i <= self.n + 1:
            self.cntTree[i] += delta
            i += i & (-i)
    
    def _updateSum(self, i, delta):
        i += 1
        while i <= self.n + 1:
            self.sumTree[i] += delta
            i += i & (-i)
    
    def _queryCnt(self, i):
        # prefix count [0..i]
        i += 1
        s = 0
        while i > 0:
            s += self.cntTree[i]
            i -= i & (-i)
        return s
    
    def _querySum(self, i):
        # prefix sum [0..i]
        i += 1
        s = 0
        while i > 0:
            s += self.sumTree[i]
            i -= i & (-i)
        return s
    
    # Insert a value
    def add(self, val):
        self.cnt[val] += 1
        self._updateCnt(val, 1)
        self._updateSum(val, val)
        self.size += 1
        self.totalSum += val
    
    # Remove one occurrence of value
    def remove(self, val):
        if self.cnt[val] == 0:
            return False
        self.cnt[val] -= 1
        self._updateCnt(val, -1)
        self._updateSum(val, -val)
        self.size -= 1
        self.totalSum -= val
        return True
    
    # Total number of elements
    def __len__(self):
        return self.size
    
    # True if no elements
    def empty(self):
        return self.size == 0
    
    # Count of elements < x
    def countLT(self, x):
        if x <= 0:
            return 0
        return self._queryCnt(min(x - 1, self.n))
    
    # Count of elements <= x
    def countLTE(self, x):
        if x < 0:
            return 0
        return self._queryCnt(min(x, self.n))
    
    # Count of elements > x
    def countGT(self, x):
        return self.size - self.countLTE(x)
    
    # Count of elements >= x
    def countGTE(self, x):
        return self.size - self.countLT(x)
    
    # Sum of elements < x
    def sumLT(self, x):
        if x <= 0:
            return 0
        return self._querySum(min(x - 1, self.n))
    
    # Sum of elements <= x
    def sumLTE(self, x):
        if x < 0:
            return 0
        return self._querySum(min(x, self.n))
    
    # Sum of elements > x
    def sumGT(self, x):
        return self.totalSum - self.sumLTE(x)
    
    # Sum of elements >= x
    def sumGTE(self, x):
        return self.totalSum - self.sumLT(x)

    # Count of elements in [lo, hi]
    def countInRange(self, lo, hi):
        if lo > hi:
            return 0
        return self.countLTE(hi) - self.countLT(lo)

    # Sum of elements in [lo, hi]
    def sumInRange(self, lo, hi):
        if lo > hi:
            return 0
        return self.sumLTE(hi) - self.sumLT(lo)
    
    # Find the kth smallest element (0-indexed), O(log n)
    def kthSmallest(self, k):
        idx = 0
        step = 1
        while step * 2 <= self.n + 1:
            step *= 2
        while step > 0:
            if idx + step <= self.n + 1 and self.cntTree[idx + step] <= k:
                idx += step
                k -= self.cntTree[idx]
            step >>= 1
        return idx
    
    # Lower median (for odd: middle; for even: lower middle)
    def median(self):
        return self.kthSmallest((self.size - 1) // 2)
    
    # Sum of all elements
    def sum(self):
        return self.totalSum
    
    # Smallest element
    def minVal(self):
        return self.kthSmallest(0)
    
    # Largest element
    def maxVal(self):
        return self.kthSmallest(self.size - 1)
    
    # Total cost to make every element equal to target t
    def costToTarget(self, t):
        cntLTE = self.countLTE(t)
        sumLTE = self.sumLTE(t)
        cntGT = self.size - cntLTE
        sumGT = self.totalSum - sumLTE
        return t * cntLTE - sumLTE + sumGT - t * cntGT
    
    # Total cost to make every element equal to the median
    def costToMedian(self):
        return self.costToTarget(self.median())


class Solution:
    def minOperations(self, nums: list[int], k: int) -> int:
        
        def process(numbers):
            remainders = [num % k for num in numbers]
            fw = FenwickMedianSet(k)
            for v in remainders:
                fw.add(v)
            
            options = [] # holds (cost, value) which is the cost to set all numbers to that value
            halfL = k // 2
            halfR = (k - 1) // 2

            for x in range(k):
                cost = 0

                # direct left [max(0, x-halfL) ... x - 1]
                lo = max(0, x - halfL)
                if lo <= x - 1:
                    c = fw.countInRange(lo, x - 1)
                    s = fw.sumInRange(lo, x - 1)
                    cost += x * c - s

                # direct right, [x+1 ... min(k - 1, x + halfR)]
                hi = min(k - 1, x + halfR)
                if x + 1 <= hi:
                    c = fw.countInRange(x + 1, hi)
                    s = fw.sumInRange(x + 1, hi)
                    cost += s - x * c

                # left wrap: if x - halfL < 0, elements [k + x - halfL, k-1]
                if x - halfL < 0:
                    c = fw.countInRange(k + x - halfL, k - 1)
                    s = fw.sumInRange(k + x - halfL, k - 1)
                    cost += (k + x) * c - s

                # right wrap: if x + halfR > k-1, elements [0, x + halfR - k]
                if x + halfR > k - 1:
                    c = fw.countInRange(0, x + halfR - k)
                    s = fw.sumInRange(0, x + halfR - k)
                    cost += (k - x) * c + s

                options.append((cost, x))
            options.sort()
            return options
        
        evenNums = [nums[i] for i in range(len(nums)) if i % 2 == 0]
        oddNums = [nums[i] for i in range(len(nums)) if i % 2 == 1]
        
        evenOpts = process(evenNums)
        oddOpts = process(oddNums)

        if evenOpts[0][1] != oddOpts[0][1]:
            return evenOpts[0][0] + oddOpts[0][0]
        v1 = evenOpts[1][0] + oddOpts[0][0]
        v2 = evenOpts[0][0] + oddOpts[1][0]
        return min(v1, v2)