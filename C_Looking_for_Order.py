from array import array

x, y = map(int, input().split())
n = int(input())
bags = []
for _ in range(n):
    a, b = map(int, input().split())
    bags.append((a, b))

fmask = (1 << n) - 1

INF = 10**9
dp = array('q', [INF]) * (fmask + 1) # dp[mask] tells us the minimum cost to reach this configuration
dp[0] = 0
prev = array('i', [-1]) * (fmask + 1) # maps a state to the ideal previous state, must use backwards logic not forwards logic (nextState) because we are using push DP

# Forward reconstruction with nextState[mask] is fragile because:
# multiple different previous masks can lead to the same newMask
# and you’re overwriting nextState[mask] based on improvements to future states, not based on whether mask ends up on the optimal path

prevChoice = array('I', [0]) * (fmask + 1)

def dist(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return dx*dx + dy*dy

home = (x, y)

homeDist = [dist(home, bags[i]) for i in range(n)]
pairDist = [[0]*n for _ in range(n)]
for i in range(n):
    for j in range(n):
        pairDist[i][j] = dist(bags[i], bags[j])


for mask in range(fmask):
    if dp[mask] >= INF: # fast prune (maybe needed for python), not every state is reachable following the pick least unset bit rule
        continue
    lusb = None
    for offset in range(n):
        if mask & (1 << offset): continue
        lusb = offset
        break
    # if the least unset bit gets placed alone
    newmask = mask | (1 << lusb)
    placeAloneDist = 2 * homeDist[lusb] + dp[mask]
    if placeAloneDist < dp[newmask]:
        dp[newmask] = placeAloneDist
        prev[newmask] = mask
        prevChoice[newmask] = 1 << lusb # the choice we optimally took to get here

    # if the least unset bit gets placed with another
    for offset in range(lusb + 1, n):
        if mask & (1 << offset): continue
        newMask = mask | (1 << lusb) | (1 << offset)
        d1 = homeDist[lusb]
        d2 = homeDist[offset]
        d3 = pairDist[lusb][offset]
        if d1 + d2 + d3 + dp[mask] < dp[newMask]:
            dp[newMask] = d1 + d2 + d3 + dp[mask]
            prev[newMask] = mask    
            prevChoice[newMask] = 1 << lusb | 1 << offset

print(dp[fmask])
resArr = []
currMask = fmask
while currMask != 0:
    resArr.append(0) # we are at the handbag
    prevMask = prev[currMask]
    prevChoices = prevChoice[currMask]
    for i in range(n):
        if prevChoices & (1 << i):
            resArr.append(i + 1)
    currMask = prevMask
resArr.append(0) # return to bag
print(*resArr)