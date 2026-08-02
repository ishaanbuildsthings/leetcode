class Solution:
    def maxAscendingSum(self, nums: List[int]) -> int:
        res = curr = 0
        for i in range(len(nums)):
            if i and nums[i] <= nums[i - 1]:
                curr = nums[i]
            else:
                curr += nums[i]
            res = max(res, curr)
        return res