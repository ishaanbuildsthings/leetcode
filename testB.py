def solve():
    n, k = list(map(int, input().split()))
    arr = list(map(int, input().split()))
    pos = list(map(int, input().split()))[0]
    pos -= 1

    # print('------')
    # print(f'{arr=}')
    # print(f'{pos=}')

    req = arr[pos]

    if all(x == req for x in arr):
        print(0)
        return
    
    # find the latest different one from req, we must flip that
    # now repeat
    # if we need 6 flips left and 8 flips right we just combine, so take the max
    # include ourself in the flipping calculation

    earliestDiff = arr.index(req ^ 1)
    leftScore = 0
    if earliestDiff < pos:
        leftScore = 1
        newBad = req
        for j in range(earliestDiff, pos + 1):
            if arr[j] == newBad:
                newBad ^= 1
                leftScore += 1
    
    latestDiff = None
    for i in range(n - 1, -1, -1):
        if arr[i] == req ^ 1:
            latestDiff = i
            break

    rightScore = 0
    if latestDiff > pos:
        rightScore = 1
        newBad = req
        for j in range(latestDiff, pos - 1, -1):
            if arr[j] == newBad:
                newBad ^= 1
                rightScore += 1
    
    print(max(leftScore, rightScore))

    

t = int(input())
for _ in range(t):
    solve()