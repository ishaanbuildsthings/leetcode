class Solution:
    def maxPairStrength(self, nums: list[int]) -> int:
        res = -inf
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                up = nums[i] * nums[j]
                down = gcd(nums[i], nums[j]) ** 2
                res = max(res, up / down)
        return int(res)