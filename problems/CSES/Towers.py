n = int(input())
A = list(map(int, input().split()))
towers = []
for v in A:
    # find leftmost tower > v
    left = 0
    right = len(towers) - 1
    resI = None
    while left <= right:
        m = (left + right) // 2
        if towers[m] > v:
            resI = m
            right = m - 1
        else:
            left = m + 1
    if resI is None:
        towers.append(v)
    else:
        towers[resI] = v
print(len(towers))