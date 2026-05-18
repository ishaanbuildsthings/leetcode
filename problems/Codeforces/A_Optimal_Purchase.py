import math
def solve():
    n, a, b = list(map(int, input().split()))
    Aonly = n * a
    bGroups = n // 3
    bCost = bGroups * b
    aRemain = n - (bGroups * 3)
    aCost = aRemain * a
    aAndB = aCost + bCost
    fullB = b * math.ceil(n / 3)
    print(min(Aonly, aAndB, fullB))

t = int(input())
for _ in range(t):
    solve()