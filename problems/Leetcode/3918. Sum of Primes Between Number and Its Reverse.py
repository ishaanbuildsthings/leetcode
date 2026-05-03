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

sieve = PrimeSieve(10005)
class Solution:
    def sumOfPrimesInRange(self, n: int) -> int:
        rev = int(str(n)[::-1])
        res = 0
        for num in range(min(n, rev), max(n, rev) + 1):
            if sieve.isPrime(num):
                res += num
        return res
            
            