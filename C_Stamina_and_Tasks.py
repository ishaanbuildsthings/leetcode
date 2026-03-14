def solve():
    n = int(input())
    c = []
    p = []
    for _ in range(n):
        ci, pi = list(map(int, input().split()))
        c.append(ci)
        p.append(pi)
    # print('-------')
    # print(f'{c=}')
    # print(f'{p=}')

    suff = [0] * n # max suffix score
    suff[-1] = c[-1]

    # print(f'{suff=}')
    

    for i in range(n - 2, -1, -1):
        scoreRight = suff[i + 1]
        scoreRightIfTake = (1-(p[i]/100)) * scoreRight
        scoreIfTake = c[i] + scoreRightIfTake
        suff[i] = max(scoreIfTake, scoreRight)

        # print(f'suff now: {suff}')

    print(f"{suff[0]:.10f}")


t = int(input())
for _ in range(t):
    solve()