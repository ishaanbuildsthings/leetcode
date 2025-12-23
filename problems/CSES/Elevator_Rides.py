import functools
n, maxElevator = map(int, input().split())
weights = list(map(int, input().split()))

# Bottom up O(n * 2^n) pull DP as we update dp[mask], bottom up lets us push and pull dp
fmask = (1 << n) - 1
dp = [(float('inf'), float('inf'))] * (fmask + 1) # min # of closed bags, weight in last bag, to pack this bitmask
dp[0] = (0, 0)

for mask in range(1, fmask + 1):
    # we care about all submasks with 1 fewer bit set, which are always smaller, so we can enumerate masks in order
    currBest = (float('inf'), float('inf'))
    for i in range(n):
        if not mask & (1 << i):
            continue
        submask = mask ^ (1 << i)
        prevBags, prevLastBagWeight = dp[submask]
        newSetup = (prevBags, prevLastBagWeight + weights[i]) if prevLastBagWeight + weights[i] <= maxElevator else (prevBags + 1, weights[i])
        currBest = min(currBest, newSetup)
    dp[mask] = currBest

print(dp[fmask][0] + 1)

# Bottom up O(n * 2^n) push DP as we update dp[mask+?],
# fmask = (1 << n) - 1
# dp = [(float('inf'), float('inf'))] * (fmask + 1) # min # of closed bags, weight in last bag, to pack this bitmask
# dp[0] = (0, 0)

# for mask in range(fmask):
#     for i in range(n):
#         if mask & (1 << i):
#             continue
#         newMask = mask | (1 << i)
#         prevBest, prevW = dp[mask]
#         newSetup = (prevBest, prevW + weights[i]) if prevW + weights[i] <= maxElevator else (prevBest + 1, weights[i])
#         dp[newMask] = min(dp[newMask], newSetup)

# print(dp[fmask][0] + 1)


# Top down, O(n * 2^n) pull DP, top down cannot be a push dp since we cannot update states above us in the recursive callstack, we can only pull from sub-states
# fmask = (1 << n) - 1
# @functools.lru_cache(maxsize=None)
# def dp(mask):
#     if mask == 0:
#         return (0, 0)
#     currBest = (float('inf'), float('inf'))
#     for i in range(n):
#         if not (1 << i) & mask:
#             continue
#         submask = mask ^ (1 << i)
#         nextBest, nextWeight = dp(submask)
#         newSetup = (nextBest, nextWeight + weights[i]) if nextWeight + weights[i] <= maxElevator else (nextBest + 1, weights[i])
#         currBest = min(currBest, newSetup)
#     return currBest

# print(dp(fmask)[0] + 1)
