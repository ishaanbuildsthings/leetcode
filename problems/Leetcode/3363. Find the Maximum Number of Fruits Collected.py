class Solution:
    def maxCollectedFruits(self, fruits: List[List[int]]) -> int:
        
#         ------>               |
#         |                  <  v  >
#         |  \
#         |   x
#         v
        
        
#          x
#         /
#         --->
#         \
#          \
#           \
#            x

        n = len(fruits)
        # TODO: duplicate goal counting
        
        greenScore = sum(fruits[r][r] for r in range(n))

        @cache
        def bottom(r, c):
            if c == n - 1:
                return 0 if r == n - 1 else -inf # green always takes bottom right
            
            gainable = fruits[r][c] if r != c else 0
            goUp = (gainable + bottom(r - 1, c + 1)) if r > 0 else -inf
            goRight = gainable + bottom(r, c + 1)
            goDown = gainable + bottom(r + 1, c + 1) if r < n - 1 else -inf
            return max(goUp, goRight, goDown)
        
        @cache
        def topRight(r, c):
            if r == n - 1:
                return 0 if c == n - 1 else -inf
            
            gainable = fruits[r][c] if r != c else 0
            
            goDl = (gainable + topRight(r + 1, c - 1)) if c > 0 else -inf
            goDown = gainable + topRight(r + 1, c)
            goDr = (gainable + topRight(r + 1, c + 1)) if c < n - 1 else -inf
            return max(goDl, goDown, goDr)
        
        ans = greenScore + bottom(n - 1, 0) + topRight(0, n - 1)
        bottom.cache_clear()
        topRight.cache_clear()
        return ans
            
        
            
            # \ X X X X
            # X \ X X X
            # X X \ X X
            # X X X \ X
            # X X X X \

        
        
        
        
        
        