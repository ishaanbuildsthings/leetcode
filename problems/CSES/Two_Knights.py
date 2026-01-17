N = int(input())

# total # of ways is n^2 choose 2

for n in range(1, N + 1):
    total = n**2 * (n**2 - 1) // 2

    # any rectnagles like this lose 2:
    # X X X
    # X X X

    heights = n - 1
    widths = n - 2
    rects = heights * widths
    lost = rects * 4

    print(max(0,total - lost))