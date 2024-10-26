# https://leetcode.com/problems/minimum-subarrays-in-a-valid-split/description/
# difficulty: medium
# tags: dynamic programming 1d

# Solution, O(n^2*log n) time, O(n) space

class Solution:
    def validSubarraySplit(self, nums: List[int]) -> int:
        @cache
        def dp(l):
            # base case
            if l == len(nums):
                return 0

            res = float('inf')

            for r in range(l, len(nums)):
                # if we split
                if math.gcd(nums[l], nums[r]) > 1:
                    res = min(res, 1 + dp(r + 1))

            return res

        return dp(0) if dp(0) != float('inf') else -1

