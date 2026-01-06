board = []
for _ in range(8):
    board.append(input())

cols = [False] * 8
majorDiag = set() # col - row hashes major diagonals
minorDiag = set() # col + row

def backtrack(r):
    if r == 8:
        return 1
    res = 0
    for c in range(8):
        if board[r][c] == '*':
            continue
        if cols[c]:
            continue
        if (c - r) in majorDiag:
            continue
        if (c + r) in minorDiag:
            continue
        cols[c] = True
        majorDiag.add(c - r)
        minorDiag.add(c + r)
        res += backtrack(r + 1)
        cols[c] = False
        majorDiag.remove(c - r)
        minorDiag.remove(c + r)
    return res

print(backtrack(0))
