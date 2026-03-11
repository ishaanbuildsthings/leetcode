class Solution:
    def numTrees(self, n: int) -> int:
        @cache
        def dp(l, r):
            if l == r:
                return 1
            if l > r:
                return 1
            res = 0
            for rt in range(l, r + 1):
                left = dp(l, rt - 1)
                right = dp(rt + 1, r)
                res += left * right
            return res
    return dp(1, n) 