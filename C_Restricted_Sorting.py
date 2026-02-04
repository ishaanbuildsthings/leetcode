def solve():
    n = int(input())
    A = list(map(int, input().split()))

    # print('============')
    # print(f'{A=}')
    if (A == sorted(A)):
        # print(f'equals sorted')
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
        bottle = max(A[i] - mn, mx - A[i])
        res = min(res, bottle)

    print(res)
    return

t = int(input())
for _ in range(t):
    solve()