class Solution:
    def maximumTastiness(self, price: List[int], k: int) -> int:
        price.sort()

        def canSpaceOutAllByX(x):
            takenCandies = 1 # we take the 0th candy
            prevCandyPrice = price[0]
            for j in range(1, len(price)):
                if price[j] - prevCandyPrice >= x:
                    takenCandies += 1
                    prevCandyPrice = price[j]
                if takenCandies >= k:
                    return True
            return takenCandies >= k

        # binary search on the answer
        l = 0
        r = max(price)
        res = None
        while l <= r:
            m = (r+l)//2
            canSpaceOut = canSpaceOutAllByX(m)
            if canSpaceOut:
                res = m
                l = m + 1
            else:
                r = m - 1
        return res
