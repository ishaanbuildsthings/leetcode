from collections import Counter
n, k = map(int, input().split())
arr = list(map(int, input().split()))
c = Counter()
res = []
for r in range(n):
    c[arr[r]] += 1
    if r >= k:
        lost = arr[r - k]
        c[lost] -= 1
        if not c[lost]:
            del c[lost]
    if r + 1 >= k:
        res.append(len(c))
print(*res)