import math
n, m = map(int, input().split())
arr = list(map(int, input().split()))
queries = list(map(int, input().split()))
diffs = []
for i in range(n - 1):
    diff = abs(arr[i] - arr[i+1])
    diffs.append(diff)
gAllDiffs = 0
for v in diffs:
    gAllDiffs = math.gcd(gAllDiffs, v)
res = []
for q in queries:
    v1 = arr[0] + q
    res.append(math.gcd(v1, gAllDiffs))
print(*res)

