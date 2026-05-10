class Solution:
    def findRotateSteps(self, ring: str, key: str) -> int:
        @cache
        def dp(i, pos):
            # base case
            if i == len(key):
                return 0
            
            resForThis = float('inf')
            
            for nextPos in range(len(ring)):
                if ring[nextPos] != key[i]:
                    continue
                small = min(nextPos, pos)
                big = max(nextPos, pos)
                dist1 = big - small
                dist2 = small + len(ring) - big
                dist = min(dist1, dist2)
                resForThis = min(resForThis, dist + dp(i + 1, nextPos))
            
            return resForThis
        
        return dp(0, 0) + len(key)

        # TODO: dp state doesnt use for loop :o