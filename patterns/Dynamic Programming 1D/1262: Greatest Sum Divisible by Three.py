# https://leetcode.com/problems/greatest-sum-divisible-by-three/description/
# difficulty: medium
# tags: dynamic programming 1d, dynamic programming 2d

# Solution, O(n) time O(1) space with bottom up, or O(3n) space for the commented out top down

# can do O(3) space with greedy
class Solution:
    def maxSumDivThree(self, nums: List[int]) -> int:
        # @cache
        # def dp(i, remain):
        #     # base case
        #     if i == len(nums):
        #         return 0 if remain == 0 else float('-inf')

        #     ifTake = nums[i] + dp(i + 1, (remain + nums[i]) % 3)
        #     ifSkip = dp(i + 1, remain)

        #     return max(ifTake, ifSkip)

        # return dp(0, 0)

        cache = [0, float('-inf'), float('-inf')]
        for num in nums:
            numRemainder = num % 3
            newCache = cache[:]
            for newRemainder in range(3):
                newCache[newRemainder] = max(cache[newRemainder], cache[(newRemainder + (3 - numRemainder)) % 3] + num)
            cache = newCache
        return cache[0]

        # 0->0
        # 1->2
        # 2->1
        # 3-newRemainder % mod


