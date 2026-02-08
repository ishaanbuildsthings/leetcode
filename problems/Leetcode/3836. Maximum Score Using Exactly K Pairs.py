class Solution:
    def maxScore(self, nums1: List[int], nums2: List[int], k: int) -> int:
        @cache
        def dp(i, j, pairsLeft):
            if pairsLeft == 0:
                return 0
            if i == len(nums1):
                return -inf
            if j == len(nums2):
                return -inf
            ifI = dp(i + 1, j, pairsLeft)
            ifJ = dp(i, j + 1, pairsLeft)
            res = max(ifI, ifJ)
            if pairsLeft:
                ifTake = nums1[i] * nums2[j] + dp(i + 1, j + 1, pairsLeft - 1)
                res = max(res, ifTake)
            return res

        ans = dp(0,0,k)
        dp.cache_clear()
        return ans