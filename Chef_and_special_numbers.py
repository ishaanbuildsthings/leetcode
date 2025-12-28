"""
Chef's team is going to participate in the legendary math battles. This time the main task of the competition is to calculate number of K-special numbers in the range [L, R] (i.e. L, L + 1, L + 2, ..., R).

A number X is said to be K-special if there exist K or more different digits,
such that X is divisible by those digits and those digits are present in the decimal representation of the number.
For example, number 48 is both 1 and 2 special, as it is divisible by digits 4 and 8. Note that no positive integer is divisible by number 0.
"""
import functools, math
# maps a number from 0-2520 to a bitmask of its factors
remToDivis = []
# lcm of 1, 2, ..., 9
for remainder in range(2521):
    mask = 0
    for d in range(1, 10):
        if remainder % d == 0:
            mask |= (1 << d)
    remToDivis.append(mask)

Q = int(input())
for _ in range(Q):
    L, R, K = map(int, input().split())
    strR = str(R)
    strL = str(L)
    diff = len(strR) - len(strL)
    strL = '0' * diff + strL
    def solveForBound(bound):
        up = str(bound)
        @functools.lru_cache(maxsize=None)
        cache = [
            [
                [
                    -1 for _ in range(1 << 10)
                ] for _ in range(2520)
            ] for _ in range(len(up))
        ]
        def dp(i, rem2520, tight, takenMask):
            if i == len(up):
                factors = remToDivis[rem2520]
                overlap = takenMask & factors
                if bin(overlap).count('1') >= K:
                    return 1
                return 0
            
            ub = int(up[i]) if tight else 9
            power = len(up) - i - 1
            resHere = 0
            for d in range(ub + 1): # we can use 0 as a digit safely even if we have already started the number yet, because it won't contribute to the answer in the base case since the factors mask cannot have 0 set
                ntight = tight and d == ub
                gainedRemainder = (d * 10**power) % 2520
                nr = (rem2520 + gainedRemainder) % 2520
                ntaken = takenMask | (1 << d)
                resHere += dp(i + 1, nr, ntight, ntaken)
            return resHere
        return dp(0, 0, True, 0)
    high = solveForBound(R)
    low = solveForBound(L - 1)
    answerForQuery = high - low
    print(answerForQuery)




    # FAIL, overcount
    # # generate all target bitmasks with exactly K bits set, could use gosper's hack or other methods to generate combos like itertools
    # targetBitmasks = []
    # for mask in range(2**10):
    #     cnt = bin(mask).count('1')
    #     if cnt != K:
    #         continue
    #     # We cannot have 0s since no number is divisible by 0
    #     if mask & 1:
    #         continue
    #     targetBitmasks.append(mask)
    
    # print(f'target bitmasks: {[bin(x)[2:] for x in targetBitmasks]}')

    # for targetMask in targetBitmasks:
    #     l = functools.reduce(math.lcm, targetMask, 1)

    #     def solveForBound(bound):
    #         @functools.lru_cache(maxsize=None)
    #         def dp(i, achievedMask, remainder):
    #             if i == len(bound):
    #                 return 1 if not remainder and achievedMask 
            
