# O(1) min # of moves to go from one position to another on an infinite chess board
def knightDistanceFullyInfiniteChessboard(x1, y1, x2, y2):
    x, y = abs(x2 - x1), abs(y2 - y1)
    x, y = max(x, y), min(x, y)

    if (x, y) == (1, 0):
        return 3
    if (x, y) == (2, 2):
        return 4

    moves = max(-(-x // 2), -(-(x + y) // 3))

    if moves % 2 != (x + y) % 2:
        moves += 1

    return moves



# O(1)
# CORNER IS BOUNDED, so one quarter of the graph is infinite
# corner is (0, 0)
# X and Y MUST be >= 0
def knightDistanceFromCorner(x, y):
    if (x, y) == (1, 1):
        return 4
    return knightDistanceFullyInfiniteChessboard(0, 0, x, y)

    
n = int(input())
for _ in range(n):
    x, y = map(int, input().split())
    diffX = x - 1
    diffY = y - 1
    dist = knightDistanceFromCorner(diffX, diffY)
    print(dist)