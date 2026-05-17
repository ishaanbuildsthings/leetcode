def solve():
    n, x1, x2, k = list(map(int, input().split()))

    d1 = max(x2,x1) - min(x2,x1) # 5, 10 with circle size 12
    d2 = n - d1

    if n <= 3:
        print(1)
        return
    # if they are equal we do not run
    # if d1 == d2:
    #     if d1 == 1:
    #         print(1)
    #         return
    #     tot = d1 + k
    #     print(tot)
    #     return

    minDist = min(d1, d2)
    tot = minDist + k
    print(tot)
t = int(input())
for _ in range(t):
    solve()




