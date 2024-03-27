# https://leetcode.com/problems/subarray-product-less-than-k/description/?envType=daily-question&envId=2024-03-27
# difficulty: medium
# tags: sliding window variable

# Solution O(n) time O(1) space

class Solution:
    def numSubarrayProductLessThanK(self, nums: List[int], k: int) -> int:
        l = r = 0
        res = 0
        currProduct = 1
        while r < len(nums):
            currProduct *= nums[r]
            while currProduct >= k and r >= l:
                currProduct /= nums[l]
                l += 1
            res += (r - l + 1)
            r += 1
        return res
