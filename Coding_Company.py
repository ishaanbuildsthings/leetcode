n, x = map(int, input().split())
arr = list(map(int, input().split()))
arr.sort()

from functools import lru_cache
MOD = 10**9 + 7
@lru_cache(maxsize=None)
def dp(i, currPenalty):
    if i == n:
        return 1
    resHere = 0
    for j in range(i, n):
        npen = currPenalty + 
    