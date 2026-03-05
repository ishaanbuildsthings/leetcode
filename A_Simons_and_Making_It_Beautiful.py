t = int(input())
for _ in range(t):
    n = int(input())
    p = list(map(int, input().split()))
    mx = max(p)
    for i in range(n):
        if p[i] == mx:
            p[0], p[i] = p[i], p[0]
            break
    print(*p)

