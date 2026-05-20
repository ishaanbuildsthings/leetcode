class Solution:
    def countNumbersWithUniqueDigits(self, n: int) -> int:
        @cache
        def dp(i, isLeadingZero, mask):
            if i == n:
                return 1
            upperBound = 9
            resThis = 0
            for nextDigit in range(upperBound + 1):
                if nextDigit == 0:
                    if not isLeadingZero:
                        nextIsLeadingZero = False
                        # if we already used a 0, we cannot use one again
                        if mask >> 0 & 1:
                            continue
                        # if we haven't used a 0 before, add it to the mask
                        nextMask = mask | 1
                    # if we are leading zeroes, we still are, and don't count the 0 as being used
                    else:
                        nextMask = mask
                        nextIsLeadingZero = True
                else:
                    nextIsLeadingZero = False
                    if mask >> nextDigit & 1:
                        continue
                    nextMask = mask | 1 << nextDigit
                resThis += dp(i + 1, nextIsLeadingZero, nextMask)
            
            return resThis

        return dp(0, True, 0)
            
