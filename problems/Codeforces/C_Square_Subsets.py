import functools
import math

n = int(input())
arr = list(map(int, input().split()))
MOD = 10**9 + 7

def primeParityFactorizationsUpTo70():
    primeParities = [[] for _ in range(71)]
    primeParities[1] = []
    for num in range(2, 71):
        x = num
        factor = 2
        while factor * factor <= x:
            parity = 0
            while x % factor == 0:
                parity ^= 1
                x //= factor
            if parity:
                primeParities[num].append(factor)
            factor += 1
        if x > 1:
            primeParities[num].append(x)
    return primeParities

primeParities = primeParityFactorizationsUpTo70()

def primesUpTo70():
    isPrime = [True] * 71
    isPrime[0] = isPrime[1] = False
    for i in range(2, 71):
        if isPrime[i]:
            for j in range(i * i, 71, i):
                isPrime[j] = False
    return [i for i in range(2, 71) if isPrime[i]]

primes = primesUpTo70()

primeToIdx = { prime : i for i, prime in enumerate(primes) }

biggestNumber = max(arr)
uniqueNumbers = set()
frqs = [0] * (biggestNumber + 1)
for i, v in enumerate(arr):
    frqs[v] += 1
    uniqueNumbers.add(v)
uniqueNumbers = sorted(uniqueNumbers)

# Bottom up version
fmask = (1 << len(primes)) - 1
dp = [0] * (fmask + 1) # ways to end up with that mask, as we process elements one by one
dp[0] = 1 # initially select nothing
for uniqueI, uniqueNum in enumerate(uniqueNumbers):
    ndp = [0] * (fmask + 1) # dont include the previous subsequences that were doable, they will get added again when we consider selecting 0 numbers which is handled in the even case
    frq = frqs[uniqueNum]
    waysToSelectHalf = pow(2, frq - 1, MOD) # selecting an odd frequency, or an even frequency
    for mask in range(fmask + 1):
        ndp[mask] += dp[mask] * waysToSelectHalf # selecting an even amount yields the same mask
        ndp[mask] %= MOD
        oddMask = mask
        for oddParityFac in primeParities[uniqueNum]:
            oddIdx = primeToIdx[oddParityFac]
            oddMask ^= (1 << oddIdx)
        ndp[oddMask] += dp[mask] * waysToSelectHalf
        ndp[oddMask] %= MOD
    dp = ndp

print(dp[0] - 1)


# Top down version (MLE)
# ways to end with all even mask starting from uniqueI... with the current mask
# @functools.lru_cache(maxsize=None)
# def dp(uniqueI, currOddMask):
#     if uniqueI == len(uniqueNumbers):
#         return bool(currOddMask == 0)
#     frq = frqs[uniqueNumbers[uniqueI]]
#     waysToSelectEven = pow(2, frq - 1, MOD)
#     ifTakeEven = dp(uniqueI + 1, currOddMask) * waysToSelectEven

#     oddPrimeParityIfTake = primeParities[uniqueNumbers[uniqueI]]
#     newMask = currOddMask
#     for oddPrime in oddPrimeParityIfTake:
#         bitIdx = primeToIdx[oddPrime]
#         newMask ^= (1 << bitIdx)
#     waysToSelectOdd = pow(2, frq - 1, MOD)
#     ifTakeOdd = dp(uniqueI + 1, newMask) * waysToSelectOdd

#     return (ifTakeEven + ifTakeOdd) % MOD

# print(dp(0, 0) - 1) # remove empty subsequence




