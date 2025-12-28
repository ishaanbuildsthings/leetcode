n = input()
strN = str(n)
maxSum = 9 * len(strN)

import functools

# We can do this trick to increment remainder as we slide (or just precompue d * pow10):  (remSoFar * 10 + digit) % s

res = 0
for digitSum in range(1, maxSum + 1):
    @functools.lru_cache(maxsize=None)
    def dp(i, remain, tight, currSum):
        if currSum > digitSum:
            return 0
        if i == len(strN):
            return 1 if (not remain and currSum == digitSum) else 0
        ub = 9 if not tight else int(strN[i])
        resHere = 0
        for d in range(ub + 1):
            ntight = tight and d == ub
            nsum = currSum + d
            power = len(strN) - i - 1
            remainderGain = d*(10**power) % digitSum
            newRemainder = (remain + remainderGain) % digitSum
            resHere += dp(i + 1, newRemainder, ntight, nsum)
        return resHere
    res += dp(0, 0, True, 0)
print(res)
        


