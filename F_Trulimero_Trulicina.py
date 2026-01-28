from collections import deque
def solve():
    height, width, k = map(int, input().split())
    res = [[None for _ in range(width)] for _ in range(height)]
    cells = height * width
    frq = cells // k
    if width % k != 0:
        number = 1
        for r in range(height):
            for c in range(width):
                res[r][c] = number
                number = ((number + 1) % (k + 1))
                if not number:
                    number = 1
        for row in res:
            print(*row)
        return
    
    for r in range(height):
        if r % 2 == 0:
            for c in range(width):
                res[r][c] = (c % k) + 1
        else:
            for c in range(width):
                res[r][c] = ((c + 1) % k) + 1
    for row in res:
        print(*row)
    
t = int(input())
for _ in range(t):
    solve()