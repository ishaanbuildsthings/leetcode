def solve():
    n = int(input())
    A = list(map(int, input().split()))
    ascColor = 0
    descColor = 0
    bothColor = 0
    for i, v in enumerate(A):
        desiredAsc = i + 1
        desiredDesc = n - i
        if v != desiredAsc and v != desiredDesc:
            bothColor += 1
        elif v != desiredAsc:
            ascColor += 1
        elif v != desiredDesc:
            descColor += 1

    turn = 1 # ascending turn
    while True:
        if turn == 1:
            turn ^= 1
            if not ascColor and not bothColor:
                print("First")
                break
            if ascColor:
                ascColor -= 1
                continue
            # only color both if there are still descending left
            if bothColor and not descColor:
                print("Tie")
                break
            if bothColor and descColor:
                bothColor -= 1
                continue
        elif turn == 0:
            turn ^= 1
            if not descColor and not bothColor:
                print("Second")
                break
            if descColor:
                descColor -= 1
                continue
            # only color both if there are still ascending left
            if bothColor and not ascColor:
                print("Tie")
                break
            if bothColor and ascColor:
                bothColor -= 1
                continue

t = int(input())
for _ in range(t):
    solve()


# 1 2 4 3
#     ^ ^

# v v v descend
# 2 3 1
# ^ ^ ^ ascend

# If both need all tiles colored, I will never color the last one because then you can go, so a Tie

# v   v     v descend
# 1 5 6 3 2 4
#   ^ ^ ^ ^ ^ ascend

# Always color tiles your opponent does not have

# 1 2   1 2 1 