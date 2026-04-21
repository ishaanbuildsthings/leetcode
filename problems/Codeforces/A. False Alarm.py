import sys
import math
input = sys.stdin.readline
 
t = int(input())
for _ in range(t):
    n, x = map(int, input().split())
    doors = list(map(int, input().split()))
    # print(n, x, doors)
 
    leftmostDoor = math.inf
    for i, door in enumerate(doors):
        if door == 1:
            leftmostDoor = i
            break
 
    rightmostDoor = -math.inf
    for i, door in enumerate(doors):
        if door == 1:
            rightmostDoor = i
 
 
    width = rightmostDoor - leftmostDoor + 1
    print('YES' if width <= x else 'NO')
 