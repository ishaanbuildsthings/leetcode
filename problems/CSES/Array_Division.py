n, k = map(int, input().split())
A = list(map(int, input().split()))
l = max(A)
r = sum(A)
res = None

while l <= r:
    m = (r + l) // 2
    divides = 0
    curr = 0
    for v in A:
        if curr + v > m:
            divides += 1
            curr = v
        else:
            curr += v
    if divides + 1 > k:
        l = m + 1
    else:
        res = m
        r = m - 1
print(res)
