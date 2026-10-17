import math
t = int(input())

def solve():
    n, k = map(int, input().split())

    if k < math.sqrt(n):
        print("IMPOSSIBLE")
        return
    
    res = []
    remain = n
    goingUp = n - k + 1
    while remain:
        take = min(remain, k)
        for i in range(take):
            res.append(goingUp + i)
        goingUp -= take
        goingUp = max(goingUp, 1)
        remain -= take
    
    print(*res)
                


for _ in range(t):
    solve()