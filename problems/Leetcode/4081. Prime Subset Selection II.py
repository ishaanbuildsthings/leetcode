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


class Solution:
    def maxPrimeSubset(self, n: int, s: int) -> list[int]:
        P = PrimeSieve(n + 20)
        primes = P.getPrimeList()


        # NOT REVERSED
        primes = [x for x in primes if x <= n]
        # print(primes)

        # max size subset is ~25 before exceeding S

        # gives us the best subset

        # gives us (sum, subsetIncOrder)
        @cache
        def dp(i, tot):
            if i == len(primes):
                return 0, []
            v = primes[i]
            if v + tot > s:
                return dp(i + 1, tot)
                
            skipTot, skipList = dp(i + 1, tot)
            takeTot, takeList = dp(i + 1, tot + v)
            takeTot += v
            takeList = [v] + takeList
            
            if skipTot > takeTot:
                return skipTot, skipList
            if takeTot > skipTot:
                return takeTot, takeList

            if len(skipList) < len(takeList):
                return skipTot, skipList
            if len(takeList) < len(skipList):
                return takeTot, takeList

            if skipList <= takeList:
                return skipTot, skipList
            return takeTot, takeList

        ansTot, ansList = dp(0, 0)
        dp.cache_clear()
        return ansList
            
