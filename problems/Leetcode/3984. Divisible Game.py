import random
from math import gcd

def isPrime(n):
    if n < 2:
        return False
    smallPrimes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in smallPrimes:
        if n % p == 0:
            return n == p

    d = n - 1
    s = 0
    while d & 1 == 0:
        d >>= 1
        s += 1

    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

    
class Solution:
    def divisibleGame(self, nums: list[int]) -> int:
        numToFacs = defaultdict(list)
        for v in list(set(nums)):
            B = math.isqrt(v)
            for fac in range(1, B + 1):
                if v % fac:
                    continue
                if fac != 1 and isPrime(fac):
                    numToFacs[v].append(fac)
                if v // fac != fac and ((v // fac) != 1) and isPrime(v // fac):
                    numToFacs[v].append(v // fac)

        # print(numToFacs)
                
            
        # enumerate all subarrays
        # map factor -> sum of elements with that factor as we loop
        # SL stores (-tot, fac)

        # print(numToFacs)

        n = len(nums)

        MOD = 10**9 + 7

        mxScore = -inf
        chosenK = inf

        for l in range(n):
            # sl = SortedList() # holds (-tot, fac)
            sums = defaultdict(int) # maps factor to sum of numbers with that factor
            rangeSum = 0
            maxSum = -inf
            minK = inf
            for r in range(l, n):
                # print(f'==========')
                # print(f'{l=} r={r}')
                v = nums[r]
                rangeSum += v
                factors = numToFacs[v]
                # print(f'{factors=}')
                for fac in factors:
                    oldSum = sums[fac]
                    newSum = oldSum + v
                    # sl.discard((-oldSum, fac))
                    # sl.add((-newSum, fac))
                    sums[fac] = newSum
                    if newSum > maxSum:
                        maxSum = newSum
                        minK = fac
                    elif newSum == maxSum:
                        minK = min(minK, fac)

                # print(f'sums: {sums}')

                # if not sl:
                #     continue
                # maxSum, fac = sl[0]
                # maxSum *= -1
                fac = minK
    
                # print(f'sl={sl}')

                # rawScore is maxSum
                bobScore = rangeSum - maxSum
                aliceScore = maxSum - bobScore


                if aliceScore > mxScore:
                    mxScore = aliceScore
                    chosenK = fac
                elif aliceScore == mxScore:
                    chosenK = min(chosenK, fac)

        if max(nums) == 1:
            return 1000000005
        return (mxScore * chosenK) % MOD
                
                
                
                    
                