# https://leetcode.com/problems/special-permutations/
# difficulty: medium
# tags: dp bitmask

# Problem
# You are given a 0-indexed integer array nums containing n distinct positive integers. A permutation of nums is called special if:

# For all indexes 0 <= i < n - 1, either nums[i] % nums[i+1] == 0 or nums[i+1] % nums[i] == 0.
# Return the total number of special permutations. As the answer could be large, return it modulo 109 + 7.

# Solution, O(2^n * n^2) time, O(2^n * n) space
# DP Bitmask. Store a mask of chosen numbers, and the last number, and see what we can pick. I failed this in a contest before I knew what DP bitmask was, but could easily do it the second time!

MOD = 10**9 + 7

class Solution:
    def specialPerm(self, nums: List[int]) -> int:
        FULL_MASK = 0
        for i in range(len(nums)):
            FULL_MASK = FULL_MASK | (1 << i)

        @cache
        def dp(mask, lastNum):
            # base case if we have taken all numbers
            if mask == FULL_MASK:
                return 1

            resForThis = 0

            # try taking a new number
            for i in range(len(nums)):
                # skip taken numbers
                if (mask >> i) & 1:
                    continue
                potentialNextNum = nums[i]
                if not (potentialNextNum % lastNum == 0 or lastNum % potentialNextNum == 0):
                    continue
                newMask = mask | (1 << i)
                resForThis += dp(newMask, potentialNextNum)

            return resForThis % MOD
        return dp(0, 1)
