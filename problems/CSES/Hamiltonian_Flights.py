import functools

cities, flights = map(int, input().split())
g = [[] for _ in range(cities)]
for _ in range(flights):
    a, b = map(int, input().split())
    g[a-1].append(b-1)

fmask = (1 << (cities)) - 1
MOD = 10**9 + 7

dp = [[0] * (cities) for _ in range(fmask + 1)] # dp[mask][currNode] is the # of ways to be in that state, as we iterate
dp[1][0] = 1 # we start at node 0 and our visited mask is 1, there is 1 way also

for mask in range(2, fmask + 1):
    for prevNode in range(cities - 1):
        if not (1 << prevNode) & mask: continue
        for arriveNode in g[prevNode]:
            if not (1 << arriveNode) & mask: continue
            prevMask = mask ^ (1 << arriveNode)
            prevWays = dp[prevMask][prevNode]
            dp[mask][arriveNode] += prevWays
            dp[mask][arriveNode] %= MOD

print(dp[fmask][cities-1])


# Top down version, TLEs
# @functools.lru_cache(maxsize=None)
# def dp(mask, currNode):
#     if mask == fmask:
#         return 1 if currNode == cities else 0
#     resHere = 0
#     for adj in g[currNode]:
#         if (1 << adj) & mask: continue
#         resHere += dp(mask | (1 << adj), adj)
#         resHere %= MOD
#     return resHere

# print(dp(3, 1))
        