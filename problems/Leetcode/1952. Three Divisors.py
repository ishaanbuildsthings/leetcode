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

root = math.ceil(math.sqrt(10**4)) + 1

primes = PrimeSieve(root)

class Solution:
    def isThree(self, n: int) -> bool:
        root = math.floor(math.sqrt(n))
        return math.sqrt(n) == math.floor(math.sqrt(n)) and primes.isPrime(math.floor(math.sqrt(n)))
        