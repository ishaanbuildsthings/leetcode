from collections import deque
def solve():
    # print('-------')
    n = int(input())
    # print(f'{n=}')
    grid = []
    for _ in range(2):
        grid.append(input())
    # for x in grid:
    #     print(x)

    anyDot = any(grid[r][c] == '.' for r in range(2) for c in range(n))
    if not anyDot:
        return 0
    

    # 1 region can become 3
    # . . . O . . .
    # . . x . x . .
    # only in this case or the flip of it
    
    # 1 2 3 4 left
    res = 0
    for col in range(1, n - 1):
        if grid[0][col] == grid[0][col-1] == grid[0][col+1] == '.':
            # empty top, 2 on bottom
            if (grid[1][col-1] == grid[1][col+1] == 'x'):
                if grid[1][col] == '.':
                    res += 1
        if grid[1][col] == grid[1][col-1] == grid[1][col+1] == '.':
            # empty bottom, 2 on top
            if grid[0][col-1] == grid[0][col+1] == 'x':
                if grid[0][col] == '.':
                    res += 1
    return res

t = int(input())
for _ in range(t):
    ans = solve()
    print(ans)
