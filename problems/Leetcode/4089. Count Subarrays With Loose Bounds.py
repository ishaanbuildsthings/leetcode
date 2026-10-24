class Solution:
    def countSubarrays(self, nums: list[int], minK: int, maxK: int) -> int:
        res = 0
        left = 0
        for i, v in enumerate(nums):
            if v < minK or v > maxK:
                left = i + 1
                continue
            res += i - left + 1
        return res
            