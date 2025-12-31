import functools
n = int(input())
g = []
for _ in range(n):
    row = list(map(int, input().split()))
    g.append(row)

fmask = (1 << n) - 1

@functools.lru_cache(maxsize=None)
def score(mask):
    if mask == 0:
        return 0
    lsb = None
    scoreHere = 0
    for i in range(n):
        if mask & (1 << i):
            lsb = i
            break
    for j in range(lsb + 1, n):
        if mask & (1 << j):
            scoreHere += g[i][j]
    newmask = mask ^ (1 << lsb)
    return scoreHere + score(newmask)


# 1s are available rabbits
@functools.lru_cache(maxsize=None)
def dp(mask):
    if mask == 0:
        return 0 # all rabbits paired
    # choose a submask of 1s to put into a group
    resHere = 0
    submask = mask
    lsb = mask & -mask
    while submask:
        # 2x speedup, forcing a bit to be in the group
        if lsb & submask: 
        # unset the submask
            newMask = mask ^ submask
            scoreHere = score(submask) + dp(newMask)
            resHere = max(resHere, scoreHere)
        submask = (submask - 1) & mask
    return resHere

print(dp(fmask))

