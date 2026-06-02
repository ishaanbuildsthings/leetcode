class Solution:
    def minEatingSpeed(self, piles: List[int], h: int) -> int:
        l = 1
        r = 10**20
        res = None

        def canEat(speed):
            return sum(math.ceil(pile / speed) for pile in piles) <= h
        
        while l <= r:
            m = (r + l) // 2
            if canEat(m):
                res = m
                r = m - 1
            else:
                l = m + 1
        return res