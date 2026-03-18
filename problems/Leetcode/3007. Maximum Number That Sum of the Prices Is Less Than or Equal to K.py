class Solution:
    def findMaximumNumber(self, k: int, x: int) -> int:
        
        # find the number of set bits at a position divisible by X from the LSB for all numbers <= N
        positions = []
        for pos in range(64):
            if pos % x == 0:
                positions.append(pos)
        positions = set(positions)
        print(positions)

        @cache
        def dp(i, isTight, setBits, strNum):
            if i == len(strNum):
                return setBits
            fromRight = len(strNum) - i
            wouldBitCount = fromRight in positions

            upperBoundary = int(strNum[i]) if isTight else 1
            resHere = 0
            for number in range(upperBoundary + 1):
                newIsTight = isTight and number == upperBoundary
                nextDp = dp(i + 1, newIsTight, setBits + (number if wouldBitCount else 0), strNum)
                resHere += nextDp
            
            return resHere
        
        # binary search for biggest number with total <= k
        l = 0
        r = 10**18
        res = None
        while l <= r:
            m = (r+l)//2
            cost = dp(0, True, 0, str(bin(m)[2:]))
            dp.cache_clear()
            if cost <= k:
                res = m
                l = m + 1
            else:
                r = m - 1
        return res
