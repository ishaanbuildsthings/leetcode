x, y = map(int, input().split())
x -= 1
y -= 1
board = [
    [
        None for _ in range(8)
    ] for _ in range(8)
]
def backtrack(x, y, nextNum):
    board[y][x] = nextNum
    if nextNum == 64:
        return True

    options = [] # holds (adjacents, x, y)
    for xd, yd in [[1,2],[-1,2],[1,-2],[-1,-2],[2,1],[2,-1],[-2,1],[-2,-1]]:
        nx = x + xd
        ny = y + yd
        if nx < 0 or nx >= 8 or ny < 0 or ny >= 8:
            continue
        if board[ny][nx] is not None:
            continue
        adjacents = 0
        for xd2, yd2 in [[1,2],[-1,2],[1,-2],[-1,-2],[2,1],[2,-1],[-2,1],[-2,-1]]:
            nx2 = nx + xd2
            ny2 = ny + yd2
            if nx2 < 0 or nx2 >= 8 or ny2 < 0 or ny2 >= 8:
                continue
            if board[ny2][nx2] is not None:
                continue
            adjacents += 1
        options.append((adjacents, nx, ny))
    options.sort()
    for _, x2, y2 in options:
        if backtrack(x2, y2, nextNum + 1):
            return True
        
    board[y][x] = None

    return False

backtrack(x, y, 1)

for row in board:
    print(*row)

        