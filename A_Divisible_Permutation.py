
def solve():
    n = int(input())
    res = []
    if n % 2 == 0:
        start = n // 2
        tot = n + 1
        for i in range(n // 2):
            res.append(start)
            res.append(tot - start)
            start -= 1
        print(*res)
        return
    
    start = (n//2) + 1
    res.append(start)
    tot = n + 1
    start -= 1
    for i in range(n // 2):
        res.append(start)
        res.append(tot - start)
        start -= 1
    print(*res)





t = int(input())
for _ in range(t):
    solve()
