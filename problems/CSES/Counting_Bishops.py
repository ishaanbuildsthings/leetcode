n, k = map(int, input().split())
MOD = 10**9 + 7
def color(r, c):
    if (r + c) % 2 == 0:
        return 0
    return 1

# length of diagonals
blacks = []
whites = []

for c in range(n):
    colorHere = color(0, c)
    arr = blacks if colorHere == 1 else whites
    downRightLength = n - c
    arr.append(downRightLength)
for r in range(1, n):
    colorHere = color(r, 0)
    arr = blacks if colorHere == 1 else whites
    downRightLength = n - r
    arr.append(downRightLength)
blacks.sort()
whites.sort()

mx = len(blacks) + len(whites)
if k > mx:
    print('0')
    exit()


def solveFor(arr):

    ways = [0] * (k + 1) # ways to place this many bishops in these cell colors
    ways[0] = 1

    for i in range(len(arr)):
        # place nothing
        nways = ways[:]
        for prevPlaced in range(k):
            spotsLeft = arr[i] - prevPlaced
            if spotsLeft < 0:
                continue
            gain = ways[prevPlaced] * spotsLeft
            nways[prevPlaced + 1] += gain
            nways[prevPlaced + 1] %= MOD
        ways = nways
    
    return ways

        
    
    return dp


blackConvolution = solveFor(blacks)
whiteConvolution = solveFor(whites)
res = 0
for placeBlack in range(k + 1):
    placeWhite = k - placeBlack
    waysBlack = blackConvolution[placeBlack]
    waysWhite = whiteConvolution[placeWhite]
    res += (waysBlack * waysWhite)
    res %= MOD

print(res)


