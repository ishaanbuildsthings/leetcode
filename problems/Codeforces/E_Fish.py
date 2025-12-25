# Bottom up push DP
# n = int(input())
# mat = []
# for _ in range(n):
#     mat.append(list(map(float, input().split())))

# fmask = (1 << n) - 1 # all dead

# dp = [0] * fmask # chance of ever entering this state
# dp[0] = 1 # guaranteed we reach this state

# for mask in range(fmask):
#     odds = 0
#     dead = bin(mask).count('1')
#     alive = n - dead
#     if alive == 1:
#         continue
#     pairs = alive * (alive - 1) // 2
#     chanceToPickPair = 1 / pairs
#     for newToDie in range(n):
#         if mask & (1 << newToDie): continue # cannot already be dead
#         for activeKiller in range(n):
#             if activeKiller == newToDie: continue
#             if mask & (1 << activeKiller): continue # cannot already be dead
#             newMask = mask | (1 << newToDie)
#             dp[newMask] += dp[mask] * chanceToPickPair * mat[activeKiller][newToDie]

# res = []
# for fish in range(n):
#     mask = (1 << fish) ^ (fmask)
#     res.append(dp[mask])
# print(" ".join(f"{x:.6f}" for x in res))



# Top down pull DP
from functools import lru_cache

n = int(input())
mat = [list(map(float, input().split())) for _ in range(n)]

fmask = (1 << n) - 1

@lru_cache(maxsize=None)
def dp(deadMask):
    if deadMask == 0:
        return 1.0

    res = 0.0
    for newlyDead in range(n):
        if not (deadMask & (1 << newlyDead)):
            continue
        prevMask = deadMask ^ (1 << newlyDead)

        prevAliveMask = fmask ^ prevMask
        prevAliveCount = bin(prevAliveMask).count("1")
        prevPairs = prevAliveCount * (prevAliveCount - 1) / 2.0

        killProb = 0.0
        for activeKiller in range(n):
            if activeKiller != newlyDead and (prevAliveMask & (1 << activeKiller)):
                killProb += mat[activeKiller][newlyDead]

        res += dp(prevMask) * (killProb / prevPairs)

    return res

ans = []
for fish in range(n):
    deadMask = fmask ^ (1 << fish)
    ans.append(dp(deadMask))

print(" ".join(f"{x:.6f}" for x in ans))
