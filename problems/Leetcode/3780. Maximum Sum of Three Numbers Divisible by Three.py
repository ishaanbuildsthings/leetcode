# We can do basic combinatorics like pick three numbers all with remainder 2. I think this complexity scales nicely with the remainder and pick count, it's like n + f(rem, pick) instead of n * rem * pick. Can use bucket sort for each remainder bucket.
# Knapsack dp is the multiplied time complexity. We can do it with ndp or without in a few different ways.

# DP solution is O(n * pick * remain) = 9n
class Solution:
    def maximumSum(self, nums: List[int]) -> int:
        # Not using ndp, push style dp (pull also doable)
        dp = [[-inf] * 4 for _ in range(4)]
        dp[0][0] = 0
        for i in range(len(nums)):
            for taken in range(2, -1, -1):
                for r in range(2, -1, -1):
                    newR = (r + nums[i]) % 3
                    dp[newR][taken+1] = max(dp[newR][taken + 1], dp[r][taken] + nums[i])                
        return max(0, dp[0][3])

        # Using ndp, push style dp
        # dp = [[-inf] * 4 for _ in range(4)]
        # dp[0][0] = 0
        # for i in range(len(nums)):
        #     ndp = [x[:] for x in dp]
        #     for r in range(2, -1, -1):
        #         for taken in range(2, -1, -1):
        #             newR = (r + nums[i]) % 3
        #             ndp[newR][taken+1] = max(dp[newR][taken + 1], dp[r][taken] + nums[i])                
        #     dp = ndp
        # return max(0, dp[0][3])

        # Using ndp, pull style dp
        # dp = [[-inf] * 4 for _ in range(4)] # dp[remainder][taken]
        # dp[0][0] = 0
        # for num in nums:
        #     ndp = [x[:] for x in dp]
        #     for r in range(3):
        #         oldR = (r - num) % 3
        #         for taken in range(1, 4):
        #             ndp[r][taken] = max(dp[r][taken], dp[oldR][taken - 1] + num)
        #     dp = ndp
        # return max(dp[0][3], 0)