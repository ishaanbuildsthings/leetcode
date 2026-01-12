from functools import lru_cache

n = int(input())

l = 0
r = 10**36

def onesUsedLTEX(x):
    s = str(x)
    @lru_cache(maxsize=None)
    # lazy so used this dp that has onesUsed in state, can return (onesUsed, numWays) instead
    def dp(i, onesUsed, tight):
        if i == len(s):
            return onesUsed
        upper = int(s[i]) if tight else 9
        resHere = 0
        for nxt in range(upper + 1):
            ntight = tight and nxt == upper
            nones = onesUsed + (nxt == 1)
            resHere += dp(i + 1, nones, ntight)
        return resHere
    
    return dp(0, 0, True)

# find the largest number that uses <= n ones
res = None
while l <= r:
    m = (r + l) // 2
    result = onesUsedLTEX(m)
    if result <= n:
        res = m
        l = m + 1
    else:
        r = m - 1

print(res)

