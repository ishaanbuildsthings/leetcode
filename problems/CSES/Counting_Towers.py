MOD = 10**9 + 7

MAX_N = 10**6

# If previous is combined, we can either start 2 individual blocks, start a double block, or extend the previous double
# If previous is separate, we can either start 2 individual blocks, extend 1 restart 1, extend 1 restart the other, extend both, or start a new double
prevCombined = 1 # we can start with a double block
prevSeparate = 1 # we can start with 2 single blocks

answers = [0] * (MAX_N + 1)
answers[1] = 2

for height in range(2, MAX_N + 1):
    newCombined = 2 * prevCombined + prevSeparate
    newSeparate = prevCombined + 4 * prevSeparate
    prevCombined = newCombined % MOD
    prevSeparate = newSeparate % MOD
    answers[height] = (prevCombined + prevSeparate) % MOD

t = int(input())
for _ in range(t):
    height = int(input())
    print(answers[height])


# Matrix exponentiation version
# import numpy as np

# mod = 10**9 + 7

# def matPow(mat, exp):
#     res = np.array([[1, 0], [0, 1]], dtype=np.int64)
#     while exp > 0:
#         if exp & 1:
#             res = (res @ mat) % mod
#         mat = (mat @ mat) % mod
#         exp >>= 1
#     return res

# def solveOne(n):
#     if n == 1:
#         return 2
#     mat = np.array([[2, 1], [1, 4]], dtype=np.int64)
#     powerMat = matPow(mat, n - 1)
#     sameN = (powerMat[0, 0] + powerMat[0, 1]) % mod
#     diffN = (powerMat[1, 0] + powerMat[1, 1]) % mod
#     return (sameN + diffN) % mod

# t = int(input())
# for _ in range(t):
#     n = int(input())
#     print(solveOne(n))
