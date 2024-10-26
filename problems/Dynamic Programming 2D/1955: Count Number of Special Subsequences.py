# https://leetcode.com/problems/count-number-of-special-subsequences/
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# A sequence is special if it consists of a positive number of 0s, followed by a positive number of 1s, then a positive number of 2s.

# For example, [0,1,2] and [0,0,1,1,1,2] are special.
# In contrast, [2,1,0], [1], and [0,1,2,0] are not special.
# Given an array nums (consisting of only integers 0, 1, and 2), return the number of different subsequences that are special. Since the answer may be very large, return it modulo 109 + 7.

# A subsequence of an array is a sequence that can be derived from the array by deleting some or no elements without changing the order of the remaining elements. Two subsequences are different if the set of indices chosen are different.

# Solution, O(n) time and O(n) space, I just had a basic dp. We can also do the O(1) space dp easily. I solved this on my phone lol.

class Solution:
    def countSpecialSubsequences(self, nums: List[int]) -> int:
        memo = [[-1 for _ in range(4)] for _ in range(len(nums))]
        def dp(prevMax, i):
            # base case
            if i == len(nums):
                return 1 if prevMax == 2 else 0
            if memo[i][prevMax] != -1:
                return memo[i][prevMax]

            res = 0
            curr = nums[i]

            if curr < prevMax:
                return dp(prevMax, i + 1)

            # if skip
            res = dp(prevMax, i + 1)
            # if take
            if curr == prevMax or curr == prevMax + 1:
             res += dp(curr, i + 1)

            memo[i][prevMax] = res % (10**9 + 7)
            return memo[i][prevMax]
        return dp(-1, 0)