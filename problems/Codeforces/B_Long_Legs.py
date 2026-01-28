def solve():
    a, b = map(int, input().split())
    res = float('inf')
    for legSize in range(1, 100000 + 1):
        fullA = a // legSize
        if fullA * legSize != a:
            fullA += 1
        fullB = b // legSize
        if fullB * legSize != b:
            fullB += 1
        res = min(res, fullA + fullB + legSize - 1)
    print(res)
t = int(input())
for _ in range(t):
    solve()