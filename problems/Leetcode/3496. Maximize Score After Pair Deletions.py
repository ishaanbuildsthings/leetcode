class Solution:
    def maxScore(self, nums: List[int]) -> int:
        if len(nums) % 2:
            return sum(nums) - min(nums)
        tot = sum(nums)
        minPair = inf
        for i in range(len(nums) - 1):
            minPair = min(minPair, nums[i] + nums[i + 1])
        return tot - minPair