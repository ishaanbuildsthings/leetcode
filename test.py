def solve():
    n, k = list(map(int, input().split()))
    arr = list(map(int, input().split()))
    tot = sum(arr)
    if tot % 2:
        print('YES')
        return
    if (k * n) % 2 == 0:
        print('YES')
        return
    print('NO')

t = int(input())
for _ in range(t):
    solve()