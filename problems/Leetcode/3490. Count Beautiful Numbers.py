class Solution:
    def beautifulNumbers(self, l: int, r: int) -> int:
        @cache
        def dp(i, product, tot, nonZeroTaken, isTight, strNum):
            if i == len(strNum):
                if not tot:
                    return 0
                return int((product % tot) == 0)
            upper = int(strNum[i]) if isTight else 9
            resHere = 0
            for nextDigit in range(upper + 1):
                newTight = isTight and nextDigit == upper
                newNonZeroTaken = nonZeroTaken or nextDigit > 0
                newProduct = product * nextDigit
                newTot = tot + nextDigit
                if not nonZeroTaken and nextDigit > 0:
                    newProduct = nextDigit
                resHere += dp(i + 1, newProduct, newTot, newNonZeroTaken, newTight, strNum)
            return resHere
        
        up = dp(0, 0, 0, False, True, str(r))
        down = dp(0, 0, 0, False, True, str(l-1))
        dp.cache_clear()
        return up - down