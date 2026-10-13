n = int(input())

def solve():
    a, b, c = map(int, input().split())
    first = pow(b, c, 10**9 + 6)
    second = pow(a, first, 10**9 + 7)
    print(second)

for _ in range(n):
    solve()