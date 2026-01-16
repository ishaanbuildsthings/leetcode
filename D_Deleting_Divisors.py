# # get someone to a prime means they lose
# # from a prime, only factors less than that prime could be subtracted

# # 5e7 primes < 1e9

# # if we take a prime + X and claim the new number is divisible by X, that means the prime is divisible by X
# # obviously that cannot happen

# # so we can never force someone to a prime?

# # unless we are DOUBLE a prime

# # # if we are double a prime we subtract half and win


# # # take all primes, double then, you get a winner


# # # If I am double a prime, I halve and win
# # # Otherwise, I cannot reduce to a number that is double a prime, I'll lose
# # # Pick any factor that results in not being double a prime


# # # guess, if my number is a power of 2 >= 2^1, times some prime, I will


# # # If I can be double a prime, I'll win
# # # If I can get someone to a position that would force them to be double a prime, I will win
# # # That would be squares which, when you subtract the factor, are double a prime

# # 20
# import math
# def isPrime(n: int) -> bool:
#     if n < 2:
#         return False
#     if n % 2 == 0:
#         return n == 2
#     if n % 3 == 0:
#         return n == 3
#     # 6k ± 1 optimization
#     r = int(math.isqrt(n))
#     f = 5
#     while f <= r:
#         if n % f == 0 or n % (f + 2) == 0:
#             return False
#         f += 6
#     return True
# from functools import lru_cache
# @lru_cache(maxsize=None)
# def dp(number):
#     if number == 1:
#         return False
#     if isPrime(number):
#         return False
#     for f in range(2, number):
#         if number % f == 0:
#             if not dp(number - f):
#                 return True
#     return False
# for number in range(1, 5000):
#     if number % 2 == 0 and not dp(number):
#         print(f'couldnt win on this even: {number}')

#     # print(f'number={number}, win={dp(number)}')


# # 8
# # 32
# # 128

banned = [2]
while banned[-1] <= 1000000000:
    banned.append(banned[-1] * 4)
banned = set(banned)
# print(banned)

t = int(input())
for _ in range(t):
    n = int(input())
    if n % 2:
        print("Bob")
        continue
    if n in banned:
        print("Bob")
        continue
    print("Alice")