k = int(input())

# cache[r1][c1][r2][c2][stepsLeft]
cache = [[[[[None for _ in range(k + 1)] for _ in range(8)] for _ in range(8)] for _ in range(8)] for _ in range(8)]

# Odds that the starting point does NOT end at the ending point after that many steps
def dp(r1, c1, r2, c2, stepsLeft):
    cached = cache[r1][c1][r2][c2][stepsLeft]
    if cached is not None:
        return cached

    if stepsLeft == 0:
        res = int(r1 != r2 or c1 != c2)
        cache[r1][c1][r2][c2][stepsLeft] = res
        return res

    oddsHere = 0
    validNexts = 0
    for rDiff, cDiff in [[1,0],[-1,0],[0,1],[0,-1]]:
        nr = r1 + rDiff
        nc = c1 + cDiff
        if nr < 0 or nr == 8 or nc < 0 or nc == 8:
            continue
        validNexts += 1
        oddsHere += dp(nr, nc, r2, c2, stepsLeft - 1)

    res = oddsHere / validNexts
    cache[r1][c1][r2][c2][stepsLeft] = res
    return res

totalExpectation = 0

for endR in range(8):
    for endC in range(8):
        # need to find the total odds no robot ends up here, which is the multiplied chance
        totalOdds = 1
        for startR in range(8):
            for startC in range(8):
                totalOdds *= dp(startR, startC, endR, endC, k)
        totalExpectation += totalOdds

print(f"{totalExpectation:.6f}")
