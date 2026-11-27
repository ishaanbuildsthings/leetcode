from math import gcd, lcm
t = int(input())

def solve():
    l, a, b = map(int, input().split())
    g1 = gcd(a, l)
    g2 = gcd(b, l)
    # print(f'{l=} {a=} {b=} {g1=} {g2=}')
    LCM = lcm(g1, g2)

    # print(f'{LCM=}')
    print(l // LCM)
for _ in range(t):
    solve()