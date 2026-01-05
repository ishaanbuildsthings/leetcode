n = int(input())
A = list(map(int, input().split()))
seen = set()
l = r = res = 0
while r < n:
    gained = A[r]
    while gained in seen:
        lost = A[l]
        seen.remove(lost)
        l += 1
    seen.add(gained)
    res = max(res, r - l + 1)
    r += 1
print(res)