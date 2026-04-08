from math import lcm
def solve():
    height, width, down, right = list(map(int, input().split()))
    down %= height
    right %= width
    rightCycle = (lcm(width, right) // right) if right else 1
    downCycle = (lcm(height, down) // down) if down else 1
    fullCycle = lcm(rightCycle, downCycle) * 2 # we take this many total moves (down and right) to return to 0,0
 
    if (fullCycle >= height * width) and (rightCycle >= width) and (downCycle >= height):
        print('YES')
    else:
        print('NO')
t = int(input())
for _ in range(t):
    solve()