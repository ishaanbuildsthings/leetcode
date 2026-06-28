class Solution:
    def maxSum(self, nums: list[int], k: int, mul: int) -> int:
        nums.sort(reverse=True)
        nums = nums[:k]
        res = 0
        for i, v in enumerate(nums):
            if mul >= 1:
                res += v * mul
                mul -= 1
            else:
                res += v
        return res