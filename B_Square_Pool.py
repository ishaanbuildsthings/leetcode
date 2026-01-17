t = int(input())
for _ in range(t):
    # print('====')
    n, s = map(int, input().split())
    res = 0
    for _ in range(n):
        dx, dy, x, y = map(int, input().split())
        # print(f'ball is at: {x} {y}')
        # if we are on upright diag
        if x == y:
            # we must launch up right or down left
            if dx == dy == 1:
                res += 1
                continue
            elif dx == dy == -1:
                res += 1
                continue
        if x + y == s:
            # go up left or down right
            if dx == 1 and dy == -1:
                res += 1
            elif dx == -1 and dy == 1:
                res += 1
        
        # print(f'res now: {res}')
    print(res)