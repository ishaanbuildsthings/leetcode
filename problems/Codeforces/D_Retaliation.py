def solve():
    n = int(input())
    A = list(map(int, input().split()))

    yNumerator = A[1] - 2 * A[0]
    yDenominator = (n - 1) - 2 * n
    if yDenominator == 0:
        print('NO')
        return
    y = yNumerator / yDenominator
    if y != int(y):
        print('NO')
        return
    x = A[0] - n * y
    if x != int(x):
        print('NO')
        return
    if x < 0 or y < 0:
        print('NO')
        return
    for i, v in enumerate(A):
        actual = ((i + 1) * x) + ((n - i) * y)
        if actual != v:
            print('NO')
            return
    print('YES')
t = int(input())
for _ in range(t):
    solve()