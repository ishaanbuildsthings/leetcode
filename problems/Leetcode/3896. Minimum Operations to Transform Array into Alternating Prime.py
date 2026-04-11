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
plist = PrimeSieve(10**5 + 1000)
class Solution:
    def minOperations(self, nums: list[int]) -> int:
        
        res = 0
        for i, v in enumerate(nums):
            while True:
                if i % 2 == 0 and not plist.isPrime(nums[i]):
                    nums[i] += 1
                    res += 1
                elif i % 2 == 0:
                    break

                if i % 2 == 1 and plist.isPrime(nums[i]):
                    nums[i] += 1
                    res += 1
                elif i % 2 == 1:
                    break

        return res
        