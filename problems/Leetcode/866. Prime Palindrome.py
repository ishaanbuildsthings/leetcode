# hit it with a hammer approach, generate palindrome halves, create a palindrome, then fast check if prime

# # TEMPLATE BY ishaanbuildsthings on github

# def _checkBase(n, a, d, s):
#     x = pow(a, d, n)
#     if x == 1 or x == n - 1:
#         return True
#     for _ in range(1, s):
#         x = x * x % n
#         if x == n - 1:
#             return True
#     return False

# # Deterministic miller rabin to check if it is prime, O(logN), it uses that weird fermat theorem remainder thing
# def isPrime(n):
#     if n < 2:
#         return False
#     for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
#         if n == p:
#             return True
#         if n % p == 0:
#             return False
#     d = n - 1
#     s = 0
#     while (d & 1) == 0:
#         d >>= 1
#         s += 1
#     # deterministic for all n (uses 64-bit witness set)
#     for a in [2, 325, 9375, 28178, 450775, 9780504, 1795265022]:
#         if a % n == 0:
#             continue
#         if not _checkBase(n, a, d, s):
#             return False
#     return True

# class Solution:
#     def primePalindrome(self, n: int) -> int:
#         if n <= 2: return 2
#         if n <= 3: return 3
#         if n <= 5: return 5
#         if n <= 7: return 7
#         res = inf
#         smallestPureDoubleFound = False
#         smallestWithMiddleFound = False
#         for half in range(1, n // 2):
#             if smallestPureDoubleFound and smallestWithMiddleFound:
#                 break
#             if str(half)[0] not in ['1', '3', '7', '9']:
#                 continue
#             double = int(str(half) + str(half)[::-1])
#             if double >= n and isPrime(double):
#                 res = min(res, double)
#                 smallestPureDoubleFound = True
#             if not smallestWithMiddleFound:
#                 for d in range(10):
#                     ndouble = int(str(half) + str(d) + str(half)[::-1])
#                     if ndouble >= n and isPrime(ndouble):
#                         res = min(res, ndouble)
#                         smallestWithMiddleFound = True
#             # oops, this was key because my pure double found would never find a valid prime palindrome!
#             else:
#                 break
#         return res


# enumerate only odd length palindromes, naive rootN prime check, works well
# we can enumerate odd length ones only by showing any even length palindrome is divisble by 11, and therefore not prime, except for 11
# proof in leetgoat notes, it's the 10%11 === -1%11 stuff
# basically the earlier solution but a slower prime check, I guess depends on some prime gaps property to show we find a prime quickly
class Solution:
    def primePalindrome(self, n: int) -> int:
        if n <= 11:
            for x in [2, 3, 5, 7, 11]:
                if x >= n:
                    return x

        def isPrime(n):
            if n < 2:
                return False
            if n % 2 == 0:
                return n == 2
            i = 3
            while i * i <= n:
                if n % i == 0:
                    return False
                i += 2
            return True

        for length in range(3, 10, 2):
            halfLen = length // 2 + 1
            for half in range(10 ** (halfLen - 1), 10 ** halfLen):
                s = str(half)
                pal = int(s + s[-2::-1])
                if pal >= n and isPrime(pal):
                    return pal
        