numHoses, numFriendPairs, maxWeight = map(int, input().split())

hosesW = list(map(int, input().split()))
hosesB = list(map(int, input().split()))

friends = []
for _ in range(numFriendPairs):
    x, y = map(int, input().split())
    friends.append((x, y)) # 1-indexed
g = [[] for _ in range(numHoses + 1)]
for a, b in friends:
    g[a].append(b)
    g[b].append(a)

# print(f'{maxWeight=}')

# print(friends)
# print(f'{g=}')

components = []
seen = [False] * (numHoses + 1)
def mark(node, bucket):
    seen[node] = True
    bucket.append(node)
    for adj in g[node]:
        if seen[adj]:
            continue
        mark(adj, bucket)
for node in range(1, numHoses + 1):
    if not seen[node]:
        b = []
        mark(node, b)
        components.append(b)
# print(f'{components=}')

dp = [0] * (maxWeight + 1) # dp[w] tells us the max beauty with weight w

for i in range(len(components)): # iterate on each component
    b = components[i]
    # print(f'bucket: {b}')
    compW = 0
    compB = 0
    for node in b:
        compW += hosesW[node-1]
        compB += hosesB[node-1]
    # print(f'{compW=}, {compB=}')
    for newWeight in range(maxWeight, 0, -1):
        # print(f'new weight = {newWeight} -------------')
        resHere = dp[newWeight]
        if newWeight - compW >= 0:
            prev = dp[newWeight-compW]
            ifTakeComp = prev + compB
            resHere = max(resHere, ifTakeComp)
            # print(f'res here when taking whole component: {resHere}')
        for node in b:
            # print(f'{node=}')
            nodeW = hosesW[node-1]
            nodeB = hosesB[node-1]
            if newWeight - nodeW >= 0:
                ifTakeNode = dp[newWeight-nodeW] + nodeB
                resHere = max(resHere, ifTakeNode)
        # print(f'final res here for weight: {resHere}')
        dp[newWeight] = resHere

print(max(dp))