class Solution:
    def maxAdjacentDistance(self, nums: List[int]) -> int:
        res = -inf
        for i in range(len(nums) - 1):
            res = max(res, abs(nums[i] - nums[i + 1]))
        if len(nums) > 1:
            res = max(res, abs(nums[0] - nums[-1]))
        return res