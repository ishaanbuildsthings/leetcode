# template by: https://github.com/agrawalishaan/leetcode
# O(n) time / space
class PrimeSieve:
    def __init__(self, n):
        self.sieve = [True for _ in range(n)]
        self.sieve[0] = False
        self.sieve[1] = False
        for i in range(2, n):
            if self.sieve[i]: # linear optimization
                for j in range(i * i, n, i):
                    self.sieve[j] = False
        self.primeList = [i for i in range(n) if self.sieve[i]]

    def isPrime(self, n):
        return self.sieve[n]

    def getPrimeList(self):
        return self.primeList

# digit dp 8)

class Solution:
    def countPrimeSetBits(self, left: int, right: int) -> int:
        b1 = bin(left - 1)[2:]
        b2 = bin(right)[2:]
        BITS = max(len(b1), len(b2))
        leftPadded = b1.zfill(BITS)
        rightPadded = b2.zfill(BITS)
        sieve = PrimeSieve(BITS + 1)

        @cache
        def dp(i, isTight, setBits, strTop):
            if i == BITS:
                return 1 if sieve.isPrime(setBits) else 0
            
            upperBound = int(strTop[i]) if isTight else 1
            resThis = 0
            for nextDigit in range(upperBound + 1):
                newIsTight = isTight and nextDigit == upperBound
                newSetBits = setBits + (nextDigit == 1)
                resThis += dp(i + 1, newIsTight, newSetBits, strTop)
            
            return resThis
        
        dp2 = dp(0, True, 0, rightPadded)
        dp1 = dp(0, True, 0, leftPadded)
        return dp2 - dp1

