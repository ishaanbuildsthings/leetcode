primesUpTo50 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

def primeFactorMask(x):
    mask = 0
    for i, p in enumerate(primesUpTo50):
        if p * p > x:
            break
        if x % p == 0:
            mask |= 1 << i
            while x % p == 0:
                x //= p
    if x > 1:
        mask |= 1 << primesUpTo50.index(x)
    return mask

import functools

T = int(input())
for _ in range(T):
    n = int(input())
    A = list(map(int, input().split()))

    dp = [0] * (1 << 15)
    for v in A:
        msk = primeFactorMask(v)
        for msk2 in range(len(dp) - 1, -1, -1):
            if not msk & msk2:
                nmsk = msk | msk2
                dp[nmsk] = max(dp[nmsk], dp[msk2] + 1)
    
    print(max(dp))
