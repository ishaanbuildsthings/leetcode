# Soltuion 1, n log n w/ binary search
class Solution:
    # def maxSubarrayLength(self, nums: List[int]) -> int:
    #     pfBig = []
    #     currBig = -inf
    #     for i in range(len(nums)):
    #         currBig = max(currBig, nums[i])
    #         pfBig.append(currBig)
        
    #     res = 0
    #     for r in range(len(nums)):
    #         v = nums[r]
    #         left = 0
    #         right = r - 1
    #         resI = None
    #         while left <= right:
    #             m = (left+right)//2
    #             if pfBig[m] > v:
    #                 resI = m
    #                 right = m - 1
    #             else:
    #                 left = m + 1
    #         if resI is not None:
    #             width = r - resI + 1
    #             res = max(res, width)
        
    #     return res

# O(n) clout solution
    def maxSubarrayLength(self, nums: List[int]) -> int:
        pfBig = []
        currBig = -inf
        for i in range(len(nums)):
            currBig = max(currBig, nums[i])
            pfBig.append(currBig)

        suffSmall = [inf] * len(nums)
        small = inf
        for i in range(len(nums) - 1, -1, -1):
            small = min(small, nums[i])
            suffSmall[i] = small
        
        res = 0
        for j in range(len(nums) - 1, -1, -1):
            if nums[j] < nums[0]:
                break
        if j == -1:
            j = 0
        
        for l in range(len(nums)):
            if nums[l] != pfBig[l]:
                continue
            while j < len(nums) - 1 and suffSmall[j + 1] < nums[l]:
                j += 1
            res = max(res, j - l + 1)
        
        return res if res != 1 else 0
