from functools import cache

t = int(input())
for _ in range(t):
    n, segsInversion = map(int, input().split())
    segs = (n * (n + 1) // 2) - n
    segsNoInversion = segs - segsInversion

    choice = {} # maps state -> increasing block
    # really this is a prev type of thing, what the previous state took to get here
    placeDescents = set()

    @cache
    def dp(size, segsWithNoInversions):
        if segsWithNoInversions < 0:
            return False
        # base case, no inversions means we will place a final decreasing segment
        if segsWithNoInversions == 0:
            placeDescents.add((size, segsWithNoInversions))
            choice[(size, segsWithNoInversions)] = size
            return True
        
        for increased in range(1, size + 1):
            noInversions = (increased * (increased + 1) // 2) - increased
            if dp(size - increased, segsWithNoInversions - noInversions):
                choice[(size, segsWithNoInversions)] = increased
                return True
            
        return False
    
    if(dp(n, segsNoInversion)) == False:
        print('0')
        continue
    
    res = [None] * n
    i = 0 # where we will insert the increasing block
    currSize = n
    currNoInversion = segsNoInversion
    while i < n:
        tup = (currSize, currNoInversion)
        nextPick = choice[tup]
        # we picked some segment of size X with no inversions
        # it must be placed from i...i+x-1
        numbersPlacedSoFar = i
        minPlaced = n - numbersPlacedSoFar + 1
        newMax = minPlaced - 1
        newMin = newMax - nextPick + 1
        placing = newMin

        # descend on the last block if 
        if tup in placeDescents:
            placing = newMax

        for j in range(i, i + nextPick):
            res[j] = placing
            if tup in placeDescents:
                placing -= 1
            else:
                placing += 1
        
        currSize -= nextPick
        inverted = (nextPick * (nextPick + 1) // 2) - nextPick
        currNoInversion -= inverted
        
        i = i + nextPick
    
    print(*res)

    
    # n=5

    # 4 5
    # i=2
