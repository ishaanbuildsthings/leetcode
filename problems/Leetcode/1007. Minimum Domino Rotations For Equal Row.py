class Solution:
    def minDominoRotations(self, tops: List[int], bottoms: List[int]) -> int:

        # can do O(1) space

        @cache
        def dp(i, flipPrev, matchTop):
            if i == len(tops):
                return 0
            if flipPrev:
                prevT = bottoms[i - 1]
                prevB = tops[i - 1]
            else:
                prevT = tops[i - 1]
                prevB = bottoms[i - 1]
            ans = inf
            if tops[i] == prevT and matchTop:
                ans = dp(i + 1, False, matchTop)
            if bottoms[i] == prevB and not matchTop:
                ans = min(ans, dp(i + 1, False, matchTop))
            if bottoms[i] == prevT and matchTop:
                ans = min(ans, 1 + dp(i + 1, True, matchTop))
            if tops[i] == prevB and not matchTop:
                ans = min(ans, 1 + dp(i + 1, True, matchTop))

            return ans
        
        a = min(dp(1, False, False), 1 + dp(1, True, False), dp(1, False, True), 1 + dp(1, True, True))
        if a == inf:
            return -1
        return a
                