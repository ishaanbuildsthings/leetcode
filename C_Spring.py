from math import lcm
def solve():
    # print('======')
    a, b, c, m = map(int, input().split())

    # how many days everyone goes
    daysAllGo = m // (lcm(lcm(a, b), c))
    # print(f'{daysAllGo=}')

    # days a and b go, but not c
    abLcm = lcm(a, b)
    abOnly = (m // abLcm) - daysAllGo

    acLcm = lcm(a, c)
    acOnly = (m // acLcm) - daysAllGo

    bcLcm = lcm(b, c)
    bcOnly = (m // bcLcm) - daysAllGo

    # print(f'{abOnly=} {acOnly=}')

    # how many days are ONLY a
    # days a goes
    # minus ab and ac days
    # plus abc
    aonly = (m // a) - abOnly - acOnly - daysAllGo
    # print(f'{aonly=}')
    bonly = (m // b) - abOnly - bcOnly - daysAllGo
    conly = (m // c) - bcOnly - acOnly - daysAllGo

    aAnswer = (aonly * 6) + (abOnly * 3) + (acOnly * 3) + (daysAllGo * 2)
    bAnswer = (bonly * 6) + (abOnly * 3) + (bcOnly * 3) + (daysAllGo * 2)
    cAnswer = (conly * 6) + (acOnly * 3) + (bcOnly * 3) + (daysAllGo * 2)

    # print(f'{aAnswer=}')
    print(f'{aAnswer} {bAnswer} {cAnswer}')

t = int(input())
for _ in range(t):
    solve()