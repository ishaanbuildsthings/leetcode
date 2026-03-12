# class Solution:
#     def stoneGameV(self, stoneValue: List[int]) -> int:
#         # O(n^3), dp(l, r) and try all splits
#         pf = []
#         curr = 0
#         for v in stoneValue:
#             curr += v
#             pf.append(curr)
#         def query(l, r):
#             return pf[r] - (pf[l-1] if l else 0)
#         @cache
#         def dp(l, r):
#             if l > r:
#                 return 0
#             resHere = 0
#             currRight = query(l, r)
#             currLeft = 0
#             for left in range(l, r + 1):
#                 currLeft += stoneValue[left]
#                 currRight -= stoneValue[left]
#                 if currLeft > currRight:
#                     aliceRight = dp(left + 1, r) + currRight
#                     resHere = max(resHere, aliceRight)
#                 elif currLeft < currRight:
#                     aliceLeft = dp(l, left) + currLeft
#                     resHere = max(resHere, aliceLeft)
#                 else:
#                     aliceRight = dp(left + 1, r) + currRight
#                     aliceLeft = dp(l, left) + currLeft
#                     resHere = max(resHere, aliceLeft, aliceRight)
#             return resHere
        
#         return dp(0, len(stoneValue) - 1)



# Solution 2, O(n^2 log n)
# same as top down DP version but we binary search for the split point and use prefix and suffix maxes
# can probably do that top down with 2 other dp functions
class Solution:
    def stoneGameV(self, stoneValue: List[int]) -> int:
        n = len(stoneValue)
        pf = []
        curr = 0
        for v in stoneValue:
            curr += v
            pf.append(curr)

        def rangeSum(l, r):
            return pf[r] - (pf[l-1] if l else 0)

        # binary search, first k where left half >= right half
        def search(i, j):
            total = rangeSum(i, j)
            left = i
            right = j
            resI = None
            while left <= right:
                m = (left+right)//2
                if rangeSum(i, m) >= rangeSum(m + 1, j):
                    resI = m
                    right = m - 1
                else:
                    left = m + 1
            return resI

        dp = [[0 for _ in range(n)] for _ in range(n)] # dp[i][j] is the answer for l...r
        left = [[0] * n for _ in range(n)] # left[i][j] is max over k in [i...j] of rangeSum(i, k) + dp[i][k]
        right = [[0] * n for _ in range(n)] # right[i][j] is max over k in [i...j] of rangeSum(k, j) + dp[k][j]

        for i in range(n):
            left[i][i] = right[i][i] = stoneValue[i]

        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                k = search(i, j)
                total = rangeSum(i, j)
                leftHalf = rangeSum(i, k)
                # if these are equal, we take the best of the two
                if leftHalf * 2 == total:
                    dp[i][j] = max(left[i][k], right[k + 1][j])
                # we become greater on the left at k...j
                # so any division rightwards or inclusive of k, like a b c k | . . .
                # we score that right division range sum + right dp
                # that's just right[k+1]
                else:
                    onRight = right[k+1][j] if k != n - 1 else 0
                    onLeft = left[i][k-1] if k else 0
                    dp[i][j] = max(onRight, onLeft)

                left[i][j] = max(left[i][j - 1], total + dp[i][j])
                right[i][j] = max(right[i + 1][j], total + dp[i][j])

        return dp[0][n - 1]