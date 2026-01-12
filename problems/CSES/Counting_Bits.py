n = int(input())

from functools import lru_cache

s = str(bin(n)[2:])

# Solution 1, put the # of 1s used in the state

# @lru_cache(maxsize=None)
# def dp(i, tight, onesUsed):
#     if i == len(s):
#         return onesUsed
#     upper = int(s[i]) if tight else 1
#     resHere = 0
#     for nxt in range(upper + 1):
#         ntight = tight and nxt == upper
#         nones = onesUsed + (nxt == 1)
#         resHere += dp(i + 1, ntight, nones)
#     return resHere

# print(dp(0, True, 0))

# Solution 2, return # of ways, all ones used inside the DP
@lru_cache(maxsize=None)
def dp(i, tight):
    if i == len(s):
        return (1, 0) # ways, ones used

    resWays = 0
    resOnes = 0
    upper = int(s[i]) if tight else 1
    for nxt in range(upper + 1):
        ntight = tight and nxt == upper
        nxtWays, nxtOnes = dp(i + 1, ntight)
        resWays += nxtWays
        resOnes += nxtOnes
        if nxt == 1:
            resOnes += nxtWays
    return resWays, resOnes

_, ans = dp(0, True)
print(ans)



# Solution 3 DOES NOT WORK, we cannot update a globalres variable because that update would need to run every node in the tree, but caching makes it so we don't do that update each time
# even with returning the # of valid ways for a given node in the DAG, that node can be entered multiple times and thus its contribution should be counted multiples times
# globalres = 0

# @lru_cache(maxsize=None)
# def dp(i, tight):
#     global globalres
#     if i == len(s):
#         return 1
#     upper = int(s[i]) if tight else 1
#     waysHere = 0
#     for nxt in range(upper + 1):
#         ntight = tight and nxt == upper
#         nxtWays = dp(i + 1, ntight)
#         if nxt == 1:
#             globalres += nxtWays
#         waysHere += nxtWays
#     return waysHere

# dp(0, True)
# print(globalres)