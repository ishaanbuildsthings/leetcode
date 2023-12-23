
# MY MODPOW TEMPLATE
# computes num^exponent % MOD in log(exponent) time
# cache is optional, can be good if you are calling modPow a lot with the same base but a different exponent

import functools

MOD = 10**9 + 7 # change this
EXPONENT = 2

@functools.lru_cache(None)
def modPow(base, exponent=EXPONENT, mod=MOD):
  if exponent == 0:
      return 1
  if exponent == 1:
      return base % mod
  half = modPow(base, exponent // 2, mod)
  if exponent % 2 == 0:
      return (half * half) % mod
  else:
      return (half * half * base) % mod


    #   # PASTE INTO LC
    #     @cache
    #     def modPow(base, exponent, mod):
    #         if exponent == 0:
    #             return 1
    #         if exponent == 1:
    #             return base % mod
    #         half = modPow(base, exponent // 2, mod)
    #         if exponent % 2 == 0:
    #             return (half * half) % mod
    #         else:
    #             return (half * half * base) % mod