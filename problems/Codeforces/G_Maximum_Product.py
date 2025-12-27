a, b = map(int, input().split())
n = len(str(b))

strA = str(a)
strB = str(b)
diff = len(strB) - len(strA)
strA = '0' * diff + strA

cacheLoose = [
    [
        None for _ in range(2)
    ] for _ in range(n)
] # cacheLoose[i][started]

# nxtDigit[i][started][tightHigh][tightLow]
nxtDigit = [
    [
        [
            [
                None for _ in range(2)
            ] for _ in range(2)
        ] for _ in range(2)
    ] for _ in range(n)
]

# We can be loose in both directions
# Loose in one direction (implies we are exactly tight in the other direction, no cache needed since this is a stick graph)
# Tight in both directions (shared prefix, again no cache needed because we can only enter into this state from 1 upstream node)
def dp(i, started, tightHigh, tightLow):
    # base case
    if i == n:
        return 1

    # memo case
    if not tightHigh and not tightLow:
        if cacheLoose[i][started] is not None:
            return cacheLoose[i][started]
    
    ub = 9 if not tightHigh else int(strB[i])
    lb = 0 if not tightLow else int(strA[i])
    largestProduct = -1 # 0 should be allowed and we need to set the digit
    for d in range(lb, ub + 1):
        newTightHigh = tightHigh and d == ub
        newTightLow = tightLow and d == lb
        newStarted = started or d != 0
        nextResult = (d if newStarted else 1) * dp(i + 1, newStarted, newTightHigh, newTightLow)
        if nextResult > largestProduct:
            largestProduct = nextResult
            nxtDigit[i][started][tightHigh][tightLow] = d

    if not tightHigh and not tightLow:
        cacheLoose[i][started] = largestProduct
    return largestProduct

dp(0, 0, 1, 1)

i = 0
started = 0
tightHigh = 1
tightLow = 1
resArr = []
while i < n:
    pickedDigit = nxtDigit[i][started][tightHigh][tightLow]
    resArr.append(pickedDigit)
    started = started or int(pickedDigit != 0)
    tightHigh = tightHigh and int(pickedDigit == int(strB[i]))
    tightLow = tightLow and int(pickedDigit == int(strA[i]))
    i += 1

print(int(''.join(str(x) for x in resArr)))