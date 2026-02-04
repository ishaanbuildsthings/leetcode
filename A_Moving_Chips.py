def solve():
    n = int(input())
    A = list(map(int, input().split()))
    res = 0
    f = A.index(1)
    lst = 0
    for i, v in enumerate(A):
        if v:
            lst = i
    for i in range(f, lst + 1):
        if not A[i]:
            res += 1
    print(res)
    return
    seen = 1
    for i in range(f + 1, n):
        if A[i] == 0:
            continue
        else:
            dist = i - f
            moves = dist - seen
            res += moves
        seen += 1
    print(res)
t = int(input())
for _ in range(t):
    solve()