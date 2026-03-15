class Solution:
    def longestSubarray(self, nums: List[int]) -> int:
        res = l = r = zeros = 0
        while r < len(nums):
            zeros += nums[r] == 0
            while zeros > 1:
                zeros -= nums[l] == 0
                l += 1
            res = max(res, r - l)
            r += 1
        return res