 class Solution:
    def divide(self, dividend: int, divisor: int) -> int:

        SAFE_MIN = -2**31
        SAFE_UP = 2**31 - 1
        # edge case
        if dividend == SAFE_MIN and divisor == -1:
            return SAFE_UP

        negs = int(dividend < 0) + int(divisor < 0)
        if negs == 1:
            isNeg = True
        else:
            isNeg = False

        dividend = abs(dividend)
        divisor = abs(divisor)

        
        SAFE_HALF = SAFE_UP >> 1

        res = 0
        while dividend > 0:
            if dividend < divisor:
                break
            count = 1
            div = divisor
            if div > SAFE_HALF:
                res += 1
                break
            while dividend >= (div << 1):
                div <<= 1
                count <<= 1
            dividend -= div
            res += count
        
        return res if not isNeg else 0 - res
            