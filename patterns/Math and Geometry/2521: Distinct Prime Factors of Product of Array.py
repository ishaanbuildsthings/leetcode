# https://leetcode.com/problems/distinct-prime-factors-of-product-of-array/description/
# difficulty: medium
# tags: math

# problem
# Given an array of positive integers nums, return the number of distinct prime factors in the product of the elements of nums.

# Note that:

# A number greater than 1 is called prime if it is divisible by only 1 and itself.
# An integer val1 is a factor of another integer val2 if val2 / val1 is an integer.

# O(sieve) overhead time and space + O(n*n) time and O(sieve) space for factors and primes
# Solution, for each number, prime factorize which takes O(n) time I think (though can be optimized to sqrt n? I might do this already implicitly), get the factors, and add to a set.
# returns a bool array of prime status for [0, n]
def getPrimes(n):
    arr = [True for _ in range(n + 1)]
    arr[0] = False
    arr[1] = False
    for factor in range(2, n + 1):
        if not arr[factor]:
            continue
        for multiple in range(factor * factor, n + 1, factor):
            arr[multiple] = False
    return arr

class Solution:
    def distinctPrimeFactors(self, nums: List[int]) -> int:
        primesBool = getPrimes(max(nums))
        primes = []
        for i in range(len(primesBool)):
            if primesBool[i]:
                primes.append(i)

        factors = set()
        for num in nums:
            for prime in primes:
                if num % prime != 0:
                    continue
                factors.add(prime)
                while num % prime == 0:
                    num = num / prime

        return len(factors)
