from math import lcm, gcd
def solve():
    afrq, bfrq, cfrq, m = list(map(int,input().split()))

    a = (m//afrq)
    b = (m//bfrq)
    # print(f'all b is: {b}')
    c = (m//cfrq)

    # sub a,b a,c.  b,c

    AB = (m//lcm(afrq, bfrq))

    AC = (m//lcm(afrq, cfrq))

    BC = (m//lcm(bfrq,cfrq))
    # print(f'days with at least bc: {BC}')

    ABC = (m//lcm(lcm(afrq,bfrq),cfrq))

    pureA = a - AB - AC + ABC
    # print(f'{pureA=}')
    halfA = (AB-ABC) + (AC-ABC)
    fullA = ABC

    alice = (6*pureA) + (3*halfA) + (2*fullA)

    pureB = b - BC - AB + ABC
    # print(f'{pureB=}')
    halfB = (AB-ABC) + (BC-ABC)
    fullB = ABC

    bob = (6*pureB) + (3*halfB) + (2*fullB)

    pureC = c - AC - BC + ABC
    halfC = (AC-ABC)+(BC-ABC)
    fullC = ABC

    carol = (6*pureC) + (3*halfC) + (2*fullC)

    print(f'{alice} {bob} {carol}')

t = int(input())
for _ in range(t):
    solve()