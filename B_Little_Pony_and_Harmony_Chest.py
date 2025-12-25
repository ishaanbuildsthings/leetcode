import functools
n = int(input())
A = list(map(int, input().split()))

def uniquePrimeFactorsUpTo60():
    res = []
    for x in range(2, 61):
        n = x
        factors = []
        p = 2
        while p * p <= n:
            if n % p == 0:
                factors.append(p)
                while n % p == 0:
                    n //= p
            p += 1
        if n > 1:
            factors.append(n)
        res.append(factors)
    return res
pf = [[], []] + uniquePrimeFactorsUpTo60()
allPrimesUnder60 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]
primeToIdx = {prime : i for i, prime in enumerate(allPrimesUnder60)}

choice = {} # maps (i, primeMask) -> the number we chose
@functools.lru_cache(maxsize=None)
def dp(i, primeMask):
    if i == n:
        return 0
    diff = A[i] - 1
    maxTakeable = A[i] + diff # We would never use a number over this because we can just use 1 which has smaller distance and does not affect the prime mask
    resHere = dp(i + 1, primeMask) + (abs(A[i] - 1)) # we can always take a 1
    choice[(i, primeMask)] = 1
    for taken in range(2, maxTakeable + 1):
        primeFactors = pf[taken]
        mustSkip = False
        newMask = primeMask
        for fac in primeFactors:
            idx = primeToIdx[fac]
            if primeMask & (1 << idx):
                mustSkip = True
                break
            newMask |= (1 << idx)
        if mustSkip:
            continue
        ifTakeThisNumber = dp(i + 1, newMask) + abs(A[i] - taken)
        if ifTakeThisNumber < resHere:
            resHere = ifTakeThisNumber
            choice[(i, primeMask)] = taken
    return resHere

dp(0, 0)
resArr = []
currI = 0
currMask = 0
while currI < n:
    pickedNumber = choice[(currI, currMask)]
    resArr.append(pickedNumber)
    currI += 1
    facs = pf[pickedNumber]
    for fac in facs:
        idx = primeToIdx[fac]
        currMask |= (1 << idx)
print(*resArr)
        
        



