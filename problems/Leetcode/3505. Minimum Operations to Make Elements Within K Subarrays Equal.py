# TEMPLATE FROM MY GITHUB: ishaanbuildsthings
# tested here https://leetcode.com/problems/sliding-window-median/submissions/2007494507/

from bisect import bisect_left as lower_bound
from bisect import bisect_right as upper_bound

class FenwickTree:
    def __init__(self, x):
        bit = self.bit = list(x)
        size = self.size = len(bit)
        for i in range(size):
            j = i | (i + 1)
            if j < size:
                bit[j] += bit[i]

    def update(self, idx, x):
        """updates bit[idx] += x"""
        while idx < self.size:
            self.bit[idx] += x
            idx |= idx + 1

    def __call__(self, end):
        """calc sum(bit[:end])"""
        x = 0
        while end:
            x += self.bit[end - 1]
            end &= end - 1
        return x

    def find_kth(self, k):
        """Find largest idx such that sum(bit[:idx]) <= k"""
        idx = -1
        for d in reversed(range(self.size.bit_length())):
            right_idx = idx + (1 << d)
            if right_idx < self.size and self.bit[right_idx] <= k:
                idx = right_idx
                k -= self.bit[idx]
        return idx + 1, k


class SortedList:
    block_size = 700

    def __init__(self, iterable=()):
        iterable = sorted(iterable)
        self.micros = [iterable[i:i + self.block_size - 1] for i in range(0, len(iterable), self.block_size - 1)] or [[]]
        self.macro = [i[0] for i in self.micros[1:]]
        self.micro_size = [len(i) for i in self.micros]
        self.fenwick = FenwickTree(self.micro_size)
        self.size = len(iterable)

    def insert(self, x):
        i = lower_bound(self.macro, x)
        j = upper_bound(self.micros[i], x)
        self.micros[i].insert(j, x)
        self.size += 1
        self.micro_size[i] += 1
        self.fenwick.update(i, 1)
        if len(self.micros[i]) >= self.block_size:
            self.micros[i:i + 1] = self.micros[i][:self.block_size >> 1], self.micros[i][self.block_size >> 1:]
            self.micro_size[i:i + 1] = self.block_size >> 1, self.block_size >> 1
            self.fenwick = FenwickTree(self.micro_size)
            self.macro.insert(i, self.micros[i + 1][0])

    def pop(self, k=-1):
        i, j = self._find_kth(k)
        self.size -= 1
        self.micro_size[i] -= 1
        self.fenwick.update(i, -1)
        return self.micros[i].pop(j)

    def __getitem__(self, k):
        i, j = self._find_kth(k)
        return self.micros[i][j]

    def count(self, x):
        return self.upper_bound(x) - self.lower_bound(x)

    def __contains__(self, x):
        return self.count(x) > 0

    def lower_bound(self, x):
        i = lower_bound(self.macro, x)
        return self.fenwick(i) + lower_bound(self.micros[i], x)

    def upper_bound(self, x):
        i = upper_bound(self.macro, x)
        return self.fenwick(i) + upper_bound(self.micros[i], x)

    def _find_kth(self, k):
        return self.fenwick.find_kth(k + self.size if k < 0 else k)

    def __len__(self):
        return self.size

    def __iter__(self):
        return (x for micro in self.micros for x in micro)

    def __repr__(self):
        return str(list(self))


class MedianWindow:
    def __init__(self):
        self.lo = SortedList() # smaller half
        self.hi = SortedList() # larger half
        # Invariant: |lo| >= |hi|, |lo| - |hi| <= 1, every elem in lo <= every elem in hi
        self.loSum = 0
        self.hiSum = 0
    
    # maintain size invariants
    def _rebalance(self):
        while len(self.lo) > len(self.hi) + 1:
            x = self.lo.pop(-1)
            self.loSum -= x
            self.hi.insert(x)
            self.hiSum += x
        while len(self.hi) > len(self.lo):
            x = self.hi.pop(0)
            self.hiSum -= x
            self.lo.insert(x)
            self.loSum += x
    
    # insert a value
    def add(self, x):
        if len(self.lo) == 0 or x <= self.lo[-1]:
            self.lo.insert(x)
            self.loSum += x
        else:
            self.hi.insert(x)
            self.hiSum += x
        self._rebalance()
    
    # remove one occurrence of x
    def remove(self, x):
        idx = self.lo.lower_bound(x)
        if idx < len(self.lo) and self.lo[idx] == x:
            self.lo.pop(idx)
            self.loSum -= x
        else:
            idx = self.hi.lower_bound(x)
            self.hi.pop(idx)
            self.hiSum -= x
        self._rebalance()
    
    # total number of elements
    def __len__(self):
        return len(self.lo) + len(self.hi)
    
    # true if no elements
    def empty(self):
        return len(self) == 0
    
    # current median (lower median for even-sized windows)
    def median(self):
        return self.lo[-1]
    
    # sum of all elements
    def sum(self):
        return self.loSum + self.hiSum
    
    # sum of the smaller half
    def lowerSum(self):
        return self.loSum
    
    # sum of the larger half
    def upperSum(self):
        return self.hiSum
    
    # count of elements in the smaller half
    def lowerSize(self):
        return len(self.lo)
    
    # count of elements in the larger half
    def upperSize(self):
        return len(self.hi)
    
    # smallest element
    def minVal(self):
        return self.lo[0]
    
    # largest element
    def maxVal(self):
        return self.lo[-1] if len(self.hi) == 0 else self.hi[-1]
    
    # total cost to make every element equal to the median
    def costToMedian(self):
        m = self.median()
        return m * len(self.lo) - self.loSum + self.hiSum - m * len(self.hi)



class Solution:
    def minOperations(self, nums: List[int], x: int, k: int) -> int:
        n = len(nums)
        w = MedianWindow()
        for r in range(x):
            w.add(nums[r])
        costs = [inf] * n # cost to set i...i+k-1
        costs[0] = w.costToMedian()
        for r in range(x, n):
            w.add(nums[r])
            w.remove(nums[r-x])
            costs[r-x+1] = w.costToMedian()
        @cache
        def dp(i, complete):
            if i >= n:
                return 0 if complete == k else inf
            if complete == k:
                return 0
            ifSkip = dp(i + 1, complete)
            ifTake = costs[i] + dp(i + x, complete + 1)
            return min(ifSkip, ifTake)
        
        ans = dp(0, 0)
        dp.cache_clear()
        return ans
