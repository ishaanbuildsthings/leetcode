# https://leetcode.com/problems/maximum-erasure-value/description/
# difficulty: medium

# Solution
class Solution:
    def maximumUniqueSubarray(self, nums: List[int]) -> int:
        res = 0
        l = r = 0
        total = 0
        seen = set()
        while r < len(nums):
            while nums[r] in seen:
                seen.remove(nums[l])
                total -= nums[l]
                l += 1
            total += nums[r]
            seen.add(nums[r])
            res = max(res, total)
            r += 1
        return res

