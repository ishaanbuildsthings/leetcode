# we can move right, up, or down
fmax = lambda a, b: a if a > b else b
fmin = lambda a, b: a if a < b else b
from collections import defaultdict

def solve():
    n, Ax, Ay, Bx, By = map(int, input().split())
    xs = list(map(int, input().split()))
    ys = list(map(int, input().split()))
    
    uniqXs = set()
    for x in xs:
        uniqXs.add(str(x))
    uniqXs.add(str(Bx))

    xTop = defaultdict(lambda: float('-inf'))
    xBot = defaultdict(lambda: float('inf'))
    # xTop = {} # maps a string(x) -> highest y
    # xBot = {} # maps a string(x) -> lowest y

    for i in range(n):
        x = str(xs[i])
        y = ys[i]
        xTop[x] = fmax(y, xTop[x])
        xBot[x] = fmin(y, xBot[x])
    xTop[str(Bx)] = fmax(xTop[str(Bx)], By)
    xBot[str(Bx)] = fmin(xBot[str(Bx)], By)

    allXs = sorted(list(int(x) for x in uniqXs))
    # we are at Ax, Ay right now
    up = 0 # min to reach the highest y
    down = 0 # min to reach lowest y
    prevX = Ax
    prevHigh = Ay
    prevLow = Ay

    for x in allXs:
        high = xTop[str(x)]
        low = xBot[str(x)]
        height = high - low # width between
        right = x - prevX

        # up to up is we step right, go down then up
        newUp = up + right + abs(prevHigh - low) + height

        # down to up is we step right, go down then up
        newUp = fmin(newUp, down + right + abs(prevLow - low) + height)

        # down to down is step right, gp up then low
        newDown = down + right + abs(prevLow - high) + height

        # up to down is step right, find high
        newDown = fmin(newDown, up + right + abs(prevHigh - high) + height)

        up = newUp
        down = newDown
    

        prevX = x
        prevHigh = high
        prevLow = low
    
    print(min(up, down))
    


t = int(input())
for _ in range(t):
    solve()





