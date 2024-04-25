# https://leetcode.com/problems/find-the-sum-of-subsequence-powers/description/
# difficulty: hard
# tags: dynamic programming 2d

# Solution, O(n^4) time and space

class Solution:
    def sumOfPowers(self, nums: List[int], k: int) -> int:
        nums.sort()

        @cache
        def dp(i, lastChoice, minDiff, picks):
            # base case
            if picks == k:
                return minDiff

            if i == len(nums):
                return 0

            # if we take this
            ifTakeNewMinDiff = float('inf') if lastChoice == None else min(minDiff, nums[i] - lastChoice)
            ifTake = dp(i + 1, nums[i], ifTakeNewMinDiff, picks + 1)
            # if we skip this
            ifSkip = dp(i + 1, lastChoice, minDiff, picks)

            return (ifTake + ifSkip) % (10**9 + 7)

        return dp(0, None, float('inf'), 0)
