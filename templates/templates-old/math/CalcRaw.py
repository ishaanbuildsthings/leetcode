from functools import cache
import math
# template by: https://github.com/agrawalishaan/leetcode
class CalcRaw:
    def __init__(self):
        pass

    def modMul(self, *args, mod):
        result = 1
        for num in args:
            result = (result * num) % mod
        return result

    # @cache # uncomment to cache
    def modPow(self, base, exponent, mod):
        return pow(base, exponent, mod)

    # @cache # uncomment to cache
    def modInv(self, num, mod):
        return self.modPow(num, mod - 2, mod)

    def gcd(a, b):
        return math.gcd(a, b)

