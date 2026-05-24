class Solution:
    def findMiddleIndex(self, nums: List[int]) -> int:
        tot = sum(nums)
        left = 0
        for i in range(len(nums)):
            right = tot - left - nums[i]
            if left == right:
                return i
            left += nums[i]
        return -1