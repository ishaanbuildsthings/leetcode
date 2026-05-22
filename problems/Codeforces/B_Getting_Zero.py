import collections
n = int(input())
A = list(map(int, input().split()))
MOD = 32768
adj = [[] for _ in range(32768)]
for num in range(MOD):
    out1 = (num + 1) % MOD
    out2 = (2 * num) % MOD
    adj[out1].append(num)
    adj[out2].append(num)
minDist = [None] * 32768
q = collections.deque()
q.append(0)
seen = {0}
steps = 0
while q:
    length = len(q)
    for _ in range(length):
        num = q.popleft()
        minDist[num] = steps
        for adjN in adj[num]:
            if adjN in seen:
                continue
            seen.add(adjN)
            q.append(adjN)
    steps += 1

res = []
for num in A:
    res.append(minDist[num])
print(*res)
