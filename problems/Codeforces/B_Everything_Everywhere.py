import math
def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    res = 0
    for i in range(n - 1):
        diff = abs(arr[i] - arr[i + 1])
        g = math.gcd(arr[i], arr[i + 1])
        if diff == g:
            res += 1
    print(res)

t = int(input())
for _ in range(t):
    solve()