def getPrimesUpTo(limitVal):
    sieve = [True] * (limitVal + 1)
    sieve[0] = sieve[1] = False
    p = 2
    while p * p <= limitVal:
        if sieve[p]:
            step = p
            start = p * p
            sieve[start:limitVal + 1:step] = [False] * (((limitVal - start) // step) + 1)
        p += 1
    return [i for i in range(2, limitVal + 1) if sieve[i]]

primesUpTo100 = getPrimesUpTo(100)
smallPrimes = [p for p in primesUpTo100 if p <= 50]
smallIndex = {p: i for i, p in enumerate(smallPrimes)}

# maps a number to the bitmask for small primes only, we don't care about big primes >50 because they can only be used once
# states would collide, e.g. if we picked 97 or we picked 89, future states don't care to distinguish these as it makes no difference
def smallMaskOf(num):
    y = num
    mask = 0
    for p in smallPrimes:
        if p * p > y:
            break
        if y % p == 0:
            mask |= 1 << smallIndex[p]
            while y % p == 0:
                y //= p
    if y > 1 and y <= 50:
        mask |= 1 << smallIndex[y]
    return mask


# With your usedMask DP, these are different states:

# used {71}

# used {97}

# used {71,97}

# even though for the rest of the problem they behave almost identically (they don’t block any composites, only themselves).

import functools
import collections
MOD = 10**9 + 7
T = int(input())
for _ in range(T):
    print('======')
    n, m = map(int, input().split())
    print(f'{n=} {m=}')

    smallMaskToNumbers = collections.defaultdict(list)



    @functools.lru_cache(maxsize=None)
    def dp(maskI, emptySpots, below50PrimeMask):
        if emptySpots < 0:
            return 0
        if maskI == len(smallPrimes):
            return 1
        
    
    print(primesUpTo100)
    print(smallPrimes)
