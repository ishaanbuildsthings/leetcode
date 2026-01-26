n = int(input())
board = []
for _ in range(n):
    row = input()
    board.append(row)
freeRow = set()
freeCol = set()
for r in range(n):
    for c in range(n):
        if board[r][c] == '.':
            freeRow.add(r)
            freeCol.add(c)
if len(freeRow) < n and len(freeCol) < n:
    print(-1)
    exit()

ans = []
if len(freeRow) == n:
    for r in range(n):
        for c in range(n):
            if board[r][c] == '.':
                ans.append((r, c))
                break
elif len(freeCol) == n:
    for c in range(n):
        for r in range(n):
            if board[r][c] == '.':
                ans.append((r, c))
                break

for a, b in ans:
    print(f'{a+1} {b+1}')
