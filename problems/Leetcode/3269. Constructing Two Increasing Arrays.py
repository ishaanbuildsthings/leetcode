class Solution:
    def minLargest(self, nums1: List[int], nums2: List[int]) -> int:
        n = len(nums1)
        m = len(nums2)
        dp = [
            [inf for _ in range(m + 1)] for _ in range(n + 1)
        ]
        dp[0][0] = 0
        for i in range(n + 1):
            for j in range(m + 1):
                if i:
                    cameFromI = dp[i-1][j]
                    cameFromI += (1 if cameFromI % 2 != nums1[i-1] else 2)
                    dp[i][j] = min(dp[i][j], cameFromI)
                if j:
                    cameFromJ = dp[i][j-1]
                    cameFromJ += (1 if cameFromJ % 2 != nums2[j-1] else 2)
                    dp[i][j] = min(dp[i][j], cameFromJ)
        return dp[n][m]

