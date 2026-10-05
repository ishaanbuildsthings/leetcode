# Wrong Answer
# 971 / 999 testcases passed
# Input
# nums =
# [-72]
# Use Testcase
# Output
# 0
# Expected
# -72
class Solution:
    def maxAlternatingSum(self, nums: list[int]) -> int:

        fmax = lambda x, y : x if x > y else y

        @cache
        def dp(i, deleteUsed, isAdding):
            if i == len(nums):
                return -inf

            v = nums[i] if isAdding else -nums[i]

            ifTakeAndEnd = v
            ifTakeAndCont = v + dp(i + 1, deleteUsed, not isAdding)
            res = fmax(ifTakeAndEnd, ifTakeAndCont)

            if not deleteUsed:
                ifDelete = dp(i + 1, True, isAdding)
                res = fmax(res, ifDelete)

            return res

        answer = -inf
        for i in range(len(nums)):
            answer = fmax(answer, dp(i, False, True))

        dp.cache_clear()

        return answer