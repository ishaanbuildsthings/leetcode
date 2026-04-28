def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    res = 0
    for v in arr:
        if v != 1:
            res += v
    if 1 not in arr:
        print(res)
        return
    # can we put every 1 paired with something
    if arr[-1] != 1:
        print(res)
        return
    
    print(1 + res)

t = int(input())
for _ in range(t):
    solve()