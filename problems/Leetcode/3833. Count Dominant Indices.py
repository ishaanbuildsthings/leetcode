class Solution:
    def dominantIndices(self, nums: List[int]) -> int:
        res = 0
        for i in range(len(nums) - 1):
            tot = 0
            for j in range(i + 1, len(nums)):
                tot += nums[j]
            onRight = len(nums) - (i + 1)
            avgRight = tot / onRight
            res += nums[i] > avgRight
        return res