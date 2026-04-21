from math import inf
def solve():
    # print('----')
    n = int(input())
    grid = []
    grid.append(input())
    grid.append(input())
    # print(f'{grid=}')

    prevPaired = 0
    RB = inf
    BR = inf
    for i in range(n):
        up = grid[0][i]
        down = grid[1][i]

        if up == down:
            npaired = prevPaired
            nrb = prevPaired + 1
            nbr = prevPaired + 1

        elif up == 'R' and down == 'B':
            npaired = 1 + prevPaired
            npaired = min(npaired, RB)
            nrb = prevPaired
            nbr = prevPaired + 2

        elif up == 'B' and down == 'R':
            npaired = 1 + prevPaired
            npaired = min(npaired, BR)
            nbr = prevPaired
            nrb = prevPaired + 2

        prevPaired = npaired
        RB = nrb
        BR = nbr
        
    print(prevPaired)

t = int(input())
for _ in range(t):
    solve()