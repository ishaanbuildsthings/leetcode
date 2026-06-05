class Solution:
    def findNumberOfLIS(self, nums: List[int]) -> int:
        n = len(nums)

        dp = [1] * n # longest subsequence ending at index `i`
        counts = [1] * n # counts of longest subsequence ending at index `i`

        for end in range(n):
            for prevEnd in range(end):
                if nums[end] <= nums[prevEnd]:
                    continue
                
                if 1 + dp[prevEnd] > dp[end]:
                    dp[end] = 1 + dp[prevEnd]
                    counts[end] = counts[prevEnd]
                elif 1 + dp[prevEnd] == dp[end]:
                    counts[end] += counts[prevEnd]

        big = max(dp)
        return sum(counts[i] for i in range(len(counts)) if dp[i] == big)