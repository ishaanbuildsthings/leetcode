class Solution:
    def findIntegers(self, n: int) -> int:
        binaryString = bin(n)[2:]
        @cache
        def dp(i, lastDigit, tight):
            # base case
            if i == len(binaryString):
                return 1
            
            currentBit = binaryString[i]

            resForThis = 0

            if tight:
                upperBoundary = int(currentBit)
            else:
                upperBoundary = 1
            
            for newBit in range(upperBoundary + 1):
                if lastDigit == 1 and newBit == 1:
                    continue
                newTight = tight and newBit == upperBoundary
                newLastDigit = newBit
                resForThis += dp(i + 1, newLastDigit, newTight)
            
            return resForThis
        
        return dp(0, -1, True)
            