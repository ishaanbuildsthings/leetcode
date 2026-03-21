class Solution:
    def maxCoins(self, lane1: List[int], lane2: List[int]) -> int:
        @cache
        def dp(i, lane, moved):
            if i==len(lane1):
                return 0
            ifAbort = 0 if i else -inf
            l = lane1 if lane==1 else lane2
            ifCont = l[i]+dp(i+1,lane,moved)
            if moved == 2:
                ifMove=-inf
            else:
                ifMove=dp(i,(lane+1)%2,moved+1)
            return max(ifAbort,ifCont,ifMove)
        a = max(dp(start,1,0) for start in range(len(lane1)))
        if 0 > max(max(lane1), max(lane2)):
            return max(max(lane1), max(lane2))
        return a
    