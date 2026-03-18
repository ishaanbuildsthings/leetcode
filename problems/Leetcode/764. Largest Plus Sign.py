class Solution:
    def orderOfLargestPlusSign(self, n: int, mines: List[List[int]]) -> int:
        h = n
        w = h
        mSet = set(tuple(x) for x in mines)

        # how far can we go forming just 1s
        @cache
        def dp(r, c, dirTup):
            if r < 0 or r == h or c < 0 or c == w:
                return 0
            if (r, c) in mSet:
                return 0
            return 1 + dp(r + dirTup[0], c + dirTup[1], dirTup)
        
        res = 0
        for r in range(n):
            for c in range(n):
                limiter = inf
                for d in [(1,0),(-1,0),(0,1),(0,-1)]:
                    limiter = min(limiter, dp(r,c,d))
                res = max(res, limiter)
        return res
                    

                
        

            
