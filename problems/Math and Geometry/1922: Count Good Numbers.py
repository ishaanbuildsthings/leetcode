# https://leetcode.com/problems/count-good-numbers/description/
# difficulty: medium
# tags: math

# Problem
# A digit string is good if the digits (0-indexed) at even indices are even and the digits at odd indices are prime (2, 3, 5, or 7).

# For example, "2582" is good because the digits (2 and 8) at even positions are even and the digits (5 and 2) at odd positions are prime. However, "3245" is not good because 3 is at an even index but is not even.
# Given an integer n, return the total number of good digit strings of length n. Since the answer may be large, return it modulo 109 + 7.

# A digit string is a string consisting of digits 0 through 9 that may contain leading zeros.

# Solution, just mod pow.

MOD = 10**9 + 7
class Solution:
    def countGoodNumbers(self, n: int) -> int:
        @cache
        def modPow(base, exponent, mod=MOD):
            if exponent == 0:
                return 1
            if exponent == 1:
                return base % mod
            half = modPow(base, exponent // 2, mod)
            if exponent % 2 == 0:
                return (half * half) % mod
            else:
                return (half * half * base) % mod

        # length is odd means we have 1 more 5x (even)
        # length is even means we have equal amounts

        res = 1
        if n % 2 == 1:
            res *= 5
            n -= 1

        res *= modPow(20, int(n//2))
        res %= MOD
        return res
