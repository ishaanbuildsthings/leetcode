def solve():
    n = int(input())
    ws = list(map(int, input().split()))
    frq = [0] * 3
    for v in ws:
        frq[v] += 1
    res = 0
    bottle = min(frq[1], frq[2])
    res += bottle
    frq[1] -= bottle
    frq[2] -= bottle

    res += frq[1] // 3
    frq[1] = frq[1] % 3
    res += frq[2] // 3
    frq[2] = frq[2] % 3
    res += frq[0]
    print(res)
t = int(input())
for _ in range(t):
    solve()