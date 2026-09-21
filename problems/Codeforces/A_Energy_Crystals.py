import sys

def solve(x):
    if x == 1:
        return print(3)
        # return 3
    # print(f'solving for {x}')
    crystals = [0, 0, 0]
    steps = 0
    while True:
        # print(f'{crystals=}')
        if max(crystals) == min(crystals) == x:
            print(steps)
            return
        if max(crystals) > x:
            print('FAIL')
            return
        crystals.sort()
        if crystals[0] == 0:
            if crystals[1] == 0:
                crystals[0] = 1
            else:
                crystals[0] = min(crystals[1] * 2 + 1, x)
            steps += 1
            continue
        # print(f'crystals after sort: {crystals}')
        # set the smallest to be equal to the middle times 2 if its even

        # 1 2 3 can become 5 2 3
        if crystals[1] % 2 == 0:
            crystals[0] = min(crystals[1] * 2 + 1, x)
            steps += 1
            continue
        else:
            # 1 3 3 can become 7 3 3
            crystals[0] = min(crystals[1] * 2 + 1, x)
            steps += 1
            continue



input = sys.stdin.readline

t = int(input())
for _ in range(t):
    x = int(input())
    result = solve(x)
    # result = solve(14)
    # break
    # print(result)