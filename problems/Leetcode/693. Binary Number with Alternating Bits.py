class Solution:
    def hasAlternatingBits(self, n: int) -> bool:
        prevBit = n & 1
        n //= 2
        while n:
            if n & 1 != prevBit:
                prevBit = 1 - prevBit
                n //= 2
            else:
                return False
        return True
