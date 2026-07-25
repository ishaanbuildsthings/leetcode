# TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant

# ✅ Tested thoroughly
# ⚠️ Not constant opimized
# ⚠️ Not using one template per-operation type (might reduce some small overhead?)
class SparseTable:
    def __init__(self, nums, combineFn):
        n = len(nums)
        log = [0] * (n + 1)
        for i in range(2, n + 1):
            log[i] = log[i // 2] + 1
        BITS = log[n] + 1
        sparse = [[None] * n for _ in range(BITS)]
        sparse[0][:] = nums
        for p in range(1, BITS):
            span = 1 << p
            half = span >> 1
            prev = sparse[p - 1]
            curr = sparse[p]
            for i in range(n - span + 1):
                curr[i] = combineFn(prev[i], prev[i + half])
        self.sparse = sparse
        self.log = log
        self.combineFn = combineFn

    def query(self, l, r):
        width = r - l + 1
        p = self.log[width]
        span = 1 << p
        row = self.sparse[p]
        return self.combineFn(row[l], row[r - span + 1])

class Solution:
    def smallestSubarrays(self, nums: List[int]) -> List[int]:

        # can also do a BITS*n solution where we check the earliest occurence of each bit in the range i... for all bits

        s = SparseTable(nums, lambda x, y: x | y)

        suffOr = [0] * len(nums)
        o = 0
        for i in range(len(nums) - 1, -1, -1):
            o |= nums[i]
            suffOr[i] = o
        
        res = []
        
        
        res = []
        for l in range(len(nums)):
            req = suffOr[l]
            left = l
            right = len(nums) - 1
            resI =None
            while left <= right:
                m = (left+right)//2
                o = s.query(l, m)
                if o >= req:
                    resI = m
                    right = m - 1
                else:
                    left = m + 1
            res.append(resI - l + 1)
        
        return res

        
            