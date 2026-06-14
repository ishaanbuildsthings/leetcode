class RangeSumQuery1d:
    def __init__(self, iterable):
        self.runningSum = 0
        self.prefixSums = []
        for num in iterable:
            self.runningSum += num
            self.prefixSums.append(self.runningSum)

    def sumQuery(self, l, r):
        if l == 0:
            return self.prefixSums[r]
        return self.prefixSums[r] - self.prefixSums[l - 1]
    
class Solution:
    def maxSubarraySum(self, nums: List[int], k: int) -> int:
        query = RangeSumQuery1d(nums)
        
        
        @cache
        def dp(i):
            if i >= len(nums):
                return -inf
            
            R = i + k - 1
            nextI = R + 1
            
            resHere = -inf # we can always not take this start
            
            if R < len(nums):
                totHere = query.sumQuery(i, R)
                takeAndCont = totHere + dp(nextI)
                resHere = max(resHere, takeAndCont)
                resHere = max(resHere, totHere)
            
            return resHere
        
        ans = max(dp(i) for i in range(len(nums)))
        dp.cache_clear()
        return ans
            
            
            
            
            
#         sizes = [k]
#         curr = k
#         while curr <= len(nums):
#             curr += k
#             if curr <= len(nums):
#                 sizes.append(curr)
        
#         print(sizes)
        
#         def getMax(size):
#             # print(f'size: {size}')
#             curr = sum(nums[:size])
#             l = 0
#             r = size - 1
#             big = curr
#             while r < len(nums) - 1:
#                 r += 1
#                 gained = nums[r]
#                 curr += gained
#                 lost = nums[l]
#                 curr -= lost
#                 l += 1
#                 big = max(big, curr)
#             # print(f'big: {big}')
#             return big
        
#         return max(getMax(sz) for sz in sizes)
                