t = int(input())
for _ in range(t):
    board = []
    height, width = map(int, input().split())
    for r in range(height):
        board.append(input())
    # print(f'{board}')

    if board[0][0] == board[-1][-1]:
        print("YES")
        continue
    if board[-1][0] == board[0][-1]:
        print("YES")
        continue
    
    # top row is same colors
    if board[0][0] == board[0][-1]:
        r1 = set([x for x in board[0]])
        if len(r1) > 1:
            print("YES")
            continue
        rn = set([x for x in board[-1]])
        if len(rn) > 1:
            print("YES")
            continue
        print("NO")
        continue
    
    # left column
    c1 = set()
    for r in range(height):
        c1.add(board[r][0])
    if len(c1) > 1:
        print("YES")
        continue
    
    cn = set()
    for r in range(height):
        cn.add(board[r][-1])
    if len(cn) > 1:
        print("YES")
        continue
    
    print("NO")

    
    # print(f'{r1=}')

# # if we have opposite corners the same color, we win
# # if we do not, we must have (or rotated)

# W.         W



# B          B


# if one of the rows (or columns) has a differing bit in between, we can flip it

# winnable:

# WWBW
# BBWB
# WWBB
# BBBB