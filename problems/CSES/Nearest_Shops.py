from collections import deque

numCities, numRoads, numShops = map(int, input().split())
shops = set(list(map(lambda x: int(x) - 1, input().split())))
roads = []
g = [[] for _ in range(numCities)]
for _ in range(numRoads):
    a, b = map(int, input().split())
    a -= 1
    b -= 1
    g[a].append(b)
    g[b].append(a)

"""
  7
  |
2-0-1-3
|_____|

4-5

6

8

Shops = [1, 3, 4, 6]

Unclaimed = 8
"""

q = deque([(node, node) for node in range(numCities) if node in shops]) # holds (nodeWeAreCurrentlyAt, sourceNode)
seen = [True if node in shops else False for node in range(numCities)]
minDist = [-1] * numCities # min dist to ANY shop (will be 0 for source nodes)
claimed = [-1] * numCities
steps = 0
while q:
    length = len(q)
    for _ in range(length):
        node, src = q.popleft()
        claimed[node] = src
        minDist[node] = steps
        for adj in g[node]:
            if seen[adj]:
                continue
            seen[adj] = True
            q.append((adj, src))
    steps += 1

minFromOtherShop = [float('inf')] * numCities # minFromOtherShop[shop] tells us the minimum distance to another shop (only useful for nodes that contain a shop, otherwise undefined behavior)

for node1 in range(numCities):
    for node2 in g[node1]:
        if claimed[node1] != claimed[node2]: # voronoi border
            # claimed[node1] shop could reach claimed[node2] via this path
            pathDist = minDist[node1] + 1 + minDist[node2]
            minFromOtherShop[claimed[node1]] = min(minFromOtherShop[claimed[node1]], pathDist)
            minFromOtherShop[claimed[node2]] = min(minFromOtherShop[claimed[node2]], pathDist)

res = [-1] * numCities
for i in range(numCities):
    if not i in shops:
        res[i] = minDist[i]
    else:
        res[i] = minFromOtherShop[i] if minFromOtherShop[i] != float('inf') else -1

print(*res)



