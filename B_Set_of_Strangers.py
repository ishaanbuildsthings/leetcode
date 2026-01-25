t = int(input())
for _ in range(t):
    h, w = map(int, input().split())
    board = []
    for r in range(h):
        row = list(map(int, input().split()))
        board.append(row)
    
    # print(board)

    uniq = set()
    
    touching = [False] * (h * w + 1)
    for r in range(h):
        for c in range(w):
            uniq.add(str(board[r][c]))
            for rd, cd in [[1,0],[-1,0],[0,1],[0,-1]]:
                nr = r + rd
                nc = c + cd
                if nr < 0 or nr == h or nc < 0 or nc == w:
                    continue
                if board[nr][nc] == board[r][c]:
                    touching[board[r][c]] = True

    
    # print(f'{touching=}')
    twos = sum(touching)
    ones = len(uniq) - twos
    if twos:
        score = ((twos - 1) * 2) + ones
    else:
        score = ones - 1
    print(score)
