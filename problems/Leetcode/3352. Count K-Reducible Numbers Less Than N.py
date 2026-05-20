class Solution:
    def countKReducibleNumbers(self, s: str, k: int) -> int:
        
        def isReducible(numberOfSetBitsFromLastNumber, transformsMade):
            if numberOfSetBitsFromLastNumber == 1:
                return True
            if transformsMade == k:
                return False
            newNum = numberOfSetBitsFromLastNumber
            newCount = newNum.bit_count()
            return isReducible(newCount, transformsMade + 1)
        
        M = 10**9 + 7
        @cache
        def dp(i, isTight, setBits):
            if i == len(s):
                if setBits == 0:
                    return 0
                if isReducible(setBits, 1):
                    return 1
                return 0
            anyWaysHere = 0
            upperBoundary = int(s[i]) if isTight else 1
            for nextDigit in range(upperBoundary + 1):
                newIsTight = isTight and nextDigit == upperBoundary
                anyWays = dp(i + 1, newIsTight, setBits + nextDigit)
                anyWaysHere += anyWays
            return anyWaysHere % M
        
        ans = dp(0, True, 0)
        num = int(s, 2)
        if num == 1:
            ans -= 1
        else:
            setBits = num.bit_count()
            if isReducible(setBits, 1):
                ans -= 1
        
        dp.cache_clear()
        return ans
                