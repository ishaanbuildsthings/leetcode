class Solution:
    def longestArithSeqLength(self, nums):
        # maybe amortized top down?
        # valToIdxs = defaultdict(list)
        # for i, v in enumerate(nums):
        #     valToIdxs[v].append(i)

        # @cache
        # def dp(i, diff):
        #     target = nums[i] - diff
        #     best = 1
        #     for j in valToIdxs[target]:
        #         if j >= i:
        #             break
        #         best = max(best, 1 + dp(j, diff))
        #     return best

        # res = 1
        # for i in range(len(nums)):
        #     for j in range(i):
        #         diff = nums[i] - nums[j]
        #         res = max(res, dp(i, diff))
        # return res

        dp = [defaultdict(lambda: 1) for _ in range(len(nums))]
        # dp[i][diff] is the best we can make for ...i (ends on i specifically) with an increase of diff

        for i in range(len(nums)):
            for j in range(i):
                reqDiff = nums[i] - nums[j]
                dp[i][reqDiff] = max(dp[i][reqDiff], 1 + dp[j][reqDiff])
        
        res = 0
        for i in range(len(nums)):
            for diffK, diffV in dp[i].items():
                res = max(res, diffV)
        return res