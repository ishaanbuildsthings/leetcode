from collections import deque
numCourses, numReqs = map(int, input().split())
g = [[] for _ in range(numCourses)] # g[requirement] = list of courses that require this
indeg = [0] * numCourses
for _ in range(numReqs):
    a, b = map(int, input().split())
    a -= 1
    b -= 1
    indeg[b] += 1
    g[a].append(b)

q = deque([node for node in range(numCourses) if indeg[node] == 0])
res = []
while q:
    node = q.popleft()
    res.append(node)
    for nxt in g[node]:
        indeg[nxt] -= 1
        if indeg[nxt] == 0:
            q.append(nxt)
if len(res) != numCourses:
    print('IMPOSSIBLE')
else:
    print(*[x + 1 for x in res])