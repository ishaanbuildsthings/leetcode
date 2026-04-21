def solve():
    x, y = list(map(int, input().split()))
    smallest = 2 * x
    if smallest >= y:
        print('NO')
        return
    for mult in range(2, 2000):
        nv = x * mult
        if nv >= y:
            break
        if y % nv != 0:
            print('YES')
            return
    print('NO')

t = int(input())
for _ in range(t):
    solve()