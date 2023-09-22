# https://leetcode.com/problems/count-primes/description/
# difficulty: Medium
# tags: math

# Problem
# Given an integer n, return the number of prime numbers that are strictly less than n.

# Solution, O(n) time and space
# Create a sieve of size n. For each number, if it was not yet divided by, mark all multiples as not prime. If it was divided by, skip it. We can start iterating from num*num because all smaller multiples were already marked.

class Solution:
    def countPrimes(self, n: int) -> int:
        if n == 0:
            return 0
        if n == 1:
            return 0

        sieve = [True for _ in range(n)]
        sieve[0] = False
        sieve[1] = False
        res = 0
        for i in range(2, n):
            if sieve[i]:
                res += 1
            else:
                continue # linear optimization
            for j in range(i * i, n, i): # square optimization since all multiples of i less than i*i would have been marked
                sieve[j] = False
        return res

