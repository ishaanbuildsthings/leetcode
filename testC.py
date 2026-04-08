from math import lcm
def solve():
    height, width, down, right = list(map(int, input().split()))
    down %= height
    right %= width
    # print('------')
    # print(f'{height=}')
    # print(f'{width=}')
    # print(f'{down=}')
    # print(f'{right=}')

    # we must enumerate all rows
    enumerateRows = (height == 1)
    if down:
        upLcm = lcm(height, down)
        upLcm //= down
        if upLcm >= height:
            enumerateRows = True
    

    enumerateCols = (width == 1)
    if right:
        rightLcm = lcm(width, right)
        rightLcm //= right
        if rightLcm >= width:
            enumerateCols = True
    
    if not enumerateRows or not enumerateCols:
        print('NO')
        return
    
    enumerateAll = False
    allLcm = lcm(height, width)
    if 2 * allLcm < (height * width):
        print('NO')
        return
    
    print('YES')


t = int(input())
for _ in range(t):
    solve()