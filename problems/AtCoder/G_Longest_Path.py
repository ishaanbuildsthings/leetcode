from collections import deque
N, M = map(int, input().split())
g = [[] for _ in range(N)]
indeg = [0] * N
for _ in range(M):
    a, b = map(int, input().split())
    g[a-1].append(b-1)
    indeg[b-1] += 1


q = deque([node for node in range(N) if indeg[node] == 0])
dp = [0] * N

while q:
    popped = q.popleft()
    for adj in g[popped]:
        indeg[adj] -= 1
        if indeg[adj] == 0:
            q.append(adj)
        dp[adj] = max(dp[adj], dp[popped] + 1)

print(max(dp))

