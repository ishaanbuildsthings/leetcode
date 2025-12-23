height, width = map(int, input().split())
MOD = 10**9 + 7

fmask = (1 << height) - 1

# A mask represents filled tiles from the previous column, so 1001 might look like this:

# <> 1
# ^  0
# v  0
# <> 1

# We need to, for a given mask, see the next transitions we can arrive to. Our future mask # of ways will be the sum of previous cases it came from.
# I used a DFS to generate the next transitions. I used ndp because we are updating masks in a seemingly random order so this felt safer.
# ndp needs to reset to [0, 0, ...] not just duplicate the dp.

# We can preserve just two allocated arrays and swap them like this:
# The only “avoid ndp” options

# Keep two arrays and swap references (still an ndp, but no copying):

# dp = [0]*(1<<h); dp[0]=1
# ndp = [0]*(1<<h)
# for _ in range(w):
#     for i in range(1<<h): ndp[i]=0
#     ...
#     dp, ndp = ndp, dp

def getValidNextMasks(mask):
    validNextMasks = []

    def generate(rowI, currentNextMask):
        if rowI == height:
            validNextMasks.append(currentNextMask)
            return
        # can't place a tile here if this row was taken from the previous column
        if mask & (1 << rowI):
            return generate(rowI + 1, currentNextMask)
        generate(rowI + 1, currentNextMask | (1 << rowI)) # place a left-right tile
        if rowI < height - 1 and mask & (1 << rowI + 1) == 0:
            generate(rowI + 2, currentNextMask) # place an up-down tile
    
    generate(0, 0)
    return validNextMasks

transitions = [getValidNextMasks(mask) for mask in range(fmask + 1)]

dp = [0] * (fmask + 1) # number of ways to reach the previous column with that bitmask being filled
dp[0] = 1

for column in range(1, width + 1):
    ndp = [0] * (fmask + 1)
    for currentBlocked in range(fmask + 1):
        for nextMask in transitions[currentBlocked]:
            ndp[nextMask] += dp[currentBlocked]
            if ndp[nextMask] >= MOD:
                ndp [nextMask] -= MOD
    dp = ndp


print(dp[0])
    
