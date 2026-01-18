
lengthToCount = [0]
for length in range(1, 20):
    lengthToCount.append(9 * (10**(length - 1)))

def solve(pos):
    pos -= 1 # convert to better indexing
    # we need to pass exactly pos digits, then we are at the right digit
    remainPass = pos
    highestFull = 0 # highest length of digits we fully pass
    for length in range(1, 20):
        full = lengthToCount[length]
        if full * length <= remainPass:
            remainPass -= full * length
            highestFull = length
            continue
    
    highWidth = highestFull + 1
    fulls = remainPass // highWidth
    remainPass -= fulls * highWidth

    start100 = 10**(highestFull)
    lastNumberPass = start100 + fulls - 1

    nextNum = lastNumberPass + 1
    if remainPass == len(str(nextNum)):
        return str(nextNum + 1)[0]
    return str(nextNum)[remainPass]


q = int(input())
for _ in range(q):
    pos = int(input()) # 1-indexed
    print(solve(pos))