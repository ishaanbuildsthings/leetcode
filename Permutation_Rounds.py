import math
MOD = 10**9 + 7
n = int(input())
A = list(map(int, input().split()))
A = [x-1 for x in A]
cycles = []
seen = [False] * n
for i, v in enumerate(A):
    if seen[i]:
        continue
    bucket = []
    curr = i
    while not seen[curr]:
        seen[curr] = True
        bucket.append(curr)
        curr = A[curr]
    cycles.append(bucket)
l = 1
for b in cycles:
    l = math.lcm(l, len(b))
print(l % MOD)