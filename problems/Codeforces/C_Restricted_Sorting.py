def solve():
    n = int(input())
    A = list(map(int, input().split()))

    if (A == sorted(A)):
        print(-1)
        return

    s = sorted(A)
    mx = max(A)
    mn = min(A)
    if A == s:
        print(-1)
        return

    res = float('inf')
    for i in range(n):
        if A[i] == s[i]:
            continue
        farA = max(mx - A[i], A[i] - mn)
        farS = max(mx - s[i], s[i] - mn)
        bottle = min(farA, farS)
        res = min(res, bottle)
        # bottle = max(A[i] - mn, mx - A[i])
        # res = min(res, bottle)

    print(res)
    return

t = int(input())
for _ in range(t):
    solve()