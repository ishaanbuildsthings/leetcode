# O(1) min # of moves to go from one position to another on an infinite chess board

def knightDistance(x1: int, y1: int, x2: int, y2: int) -> int:
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