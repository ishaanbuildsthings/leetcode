def solve():
    n = int(input())
    res = [None] * n
    for i in range(n):
        v = 2 * i + 1
        res[i] = v
    print(*res)
t = int(input())
for _ in range(t):
    solve()