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
    def maxPrimes(self, n: int, s: int) -> list[int]:
        sieve = PrimeSieve(n + 20)
        plist = sieve.getPrimeList()
        tot = 0
        res = []
        for v in plist:
            if v > n:
                break
            if tot + v > s:
                break
            tot += v
            res.append(v)

        return res
            
        