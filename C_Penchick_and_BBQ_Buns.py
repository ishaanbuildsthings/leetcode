def solve(n):
    if n % 2 == 0:
        res = []
        bun = 1
        for i in range(n // 2):
            res.append(bun)
            res.append(bun)
            bun += 1
        print(*res)
        return
    
    if n < 27:
        print(-1)
        return
    
    res = [None] * n
    res[0] = 1
    res[9] = 1
    res[25] = 1
    res[10] = 2
    res[26] = 2
    bun = 3
    for i in range(n):
        if res[i] is None:
            res[i] = bun
            res[i + 1] = bun
            bun += 1
    
    print(*res)
    
    # if N is odd we aim to place a group of 3 with even gaps in between things

    # gaps between 2 adjacent are perfect squares
    # A _ _ A = distance 3
    # to have an even number of spots in the middle, the distance must be odd
    # odd distance can never be a perfect square unless dist is 1
    # but we can't ever place 3 with a distance of 1

    # so when we place an odd amount we have 2 smaller odd subproblems
    # A _ _ _ A _ _ _ _ _ A


t = int(input())
for _ in range(t):
    # print('==========')
    n = int(input()) # buns from 1 to n
    # print(f'{n=}')
    solve(n)


# 1 2 3 4 5 6 7 8 9
# X       X       X


# 2 * X^2 = Y^2 for some integers X and Y

# No because Y = X * root2

# X^2 + Y^2 = Z^2


# X^2 + Y^2 = Z^2 for some integers X Y and Z


# 3 4 5

# 9 16 25


# A < B < C

# (B-A) is a square
# C-B is a square
# C-A is a square

# 1 10 26

# # Any square that can be the sum of 2 squares, 25 = 9 + 16
# 0 25 169

# 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28
# X     Y            X        Y                                          X    Y


# 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27
# X                 X  Y                                             X Y


# 3 4 5

# 5 12 13

# 8 15 17

# 7 24 25

# 20 21 29




# 8 15 17

# 0 64 289
#  e  o


# 0 400 841



# 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
#      ^       ^         ^


# max square must be even


# min square must be even


# 1->1
# 3->9
# 5->25
# 7->49
# 9->81

# A _ B _ c

# both distance are even means A to C is even
# If A is 0 then C must be even
