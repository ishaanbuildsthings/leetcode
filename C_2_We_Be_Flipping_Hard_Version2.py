from math import inf
def solve():
    # print('=======')
    n = int(input())
    A = list(map(int, input().split()))

    pfAbs = []
    curr = 0
    for v in A:
        curr += abs(v)
        pfAbs.append(curr)
    
    suff = [0] * n
    curr = 0
    for i in range(n - 1, -1, -1):
        curr += A[i]
        suff[i] = curr
    
    bestIdx = None
    maxTot = sum(A)

    for i in range(n):
        if A[i] < 0:
            continue
        sacSum = -1 * A[i]
        pfGain = pfAbs[i - 1] if i else 0
        suffGain = suff[i + 1] if i + 1 < n else 0
        total = sacSum + pfGain + suffGain
        if total > maxTot:
            bestIdx = i
            maxTot = total

    if bestIdx is None:
        print(0)
        return

    # print(f'{bestIdx=}')   

    ops = [bestIdx]
    flips = 1
    for i in range(bestIdx -1, -1, -1):
        v = A[i]
        if v < 0:
            if flips % 2:
                continue
            else:
                flips += 1
                ops.append(i)
        else:
            if flips % 2:
                flips += 1
                ops.append(i)
            else:
                continue
    ops.sort()
    

    flipped = [False] * n
    for op in ops:
        flipped[op] = True
    
    # flip the smallest positive
    # walk left until we hit another positive, find that
    # in-between, flip negs in ascending order
    smallestPos = None
    for i in range(n):
        if flipped[i] and A[i] > 0:
            smallestPos = i
            break
    
    # print(f'smallest pos i: {smallestPos}')

    prevPos = [None] * n
    latestPos = None
    for i in range(n):
        prevPos[i] = latestPos
        if A[i] > 0 and flipped[i]:
            latestPos = i
    
    nextPos = [None] * n
    earlyPos = None
    for i in range(n - 1, -1, -1):
        nextPos[i] = earlyPos
        if A[i] > 0 and flipped[i]:
            earlyPos = i
    
    # print(f'{prevPos=}')
    # print(f'{nextPos=}')

    res = []
    currI = smallestPos
    while currI is not None and currI < bestIdx:
        # print(f'curr I loop at: {currI} and prev pos is: {prevPos[currI]}')
        res.append(currI)
        # print(f'{res=}')
        left = -1 if prevPos[currI] is None else prevPos[currI]
        # print(f'left is: {left + 1}, walking up to currI')
        for j in range(left + 1, currI):
            if flipped[j]:
                res.append(j)
        currI = nextPos[currI]

        # print(f'final res this loop is: {res}')
    
    res.append(bestIdx)
    print(len(res))


    print(*[x + 1 for x in res])

        
    
    # for any negative, as long as there is a smaller positive on the right, we sacrifice
    
    # we can take pfSum + -val + suffSum

    # then loop backwards

    # if positive but odd flips on the right, we must flip
    # if negative but even flips on the right, we must flip

t = int(input())
for _ in range(t):
    solve()