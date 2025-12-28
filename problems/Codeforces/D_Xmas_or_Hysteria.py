import math
T = int(input())
for _ in range(T):
    n, m = map(int, input().split())
    arr = list(map(int, input().split()))
    arr = sorted([(v, i + 1) for i, v in enumerate(arr)]) # holds (value, original 1-index)

    # at least one elf will die per battle
    # min battles is half
    minBattles = math.ceil(n / 2)
    mostSurvive = n - minBattles

    if mostSurvive < m:
        print('-1')
        continue

    battles = []
    
    if m:
        # only 1...n/2 ranges of surviving elves are doable with this strategy:

        # 1 2 3 4 5 6 [7 8] [ 9 10 ]

        # pick the M biggest elves to survive, they will kill M eleves
        # the remaining elves need to die, we will use the smallest ones for those

        # first the leftover elves kill each other, including the largest remainder elf
        leftover = n - (2 * m)
        for i in range(leftover):
            value, original1Index = arr[i]
            nextElfValue, next1Index = arr[i+1]
            battles.append([original1Index, next1Index])
        
        for i in range(n - 1, n - 1 - m, -1):
            bigElf, big1Index = arr[i]
            middleElf, middle1Index = arr[i-m]
            battles.append([big1Index, middle1Index])
        
    else:
        # if m is 0, we might still be able to kill all elves. but a case like [1, 2, 100] we cannot
        # lets keep throwing large elf bodies at it until we're hopefully about to kill it, but don't kill it yet
        # then we have some ordered set of elves [1, 3, 9, 11, 1000*] except that last elf doesn't actually have 1000 hp, it has <=11
        # now we just do 1->3 3->9 9->11 11->1000 and the last battle double kills
        currDamage = 0
        theKillerElf = None
        biggestElf, biggestElfIndex = arr[-1]
        for i in range(len(arr) - 2, -1, -1):
            currDamage += arr[i][0]
            if currDamage >= biggestElf:
                theKillerElf = i
                break
        # We couldn't even kill the biggest elf
        if theKillerElf is None:
            print(-1)
            continue

        for i in range(theKillerElf):
            smallElf, smallElfIndex = arr[i]
            nextElf, nextElfIndex = arr[i+1]
            battles.append([smallElfIndex, nextElfIndex])
        for i in range(theKillerElf, n - 1):
            middleElf, middleElfIndex = arr[i]
            battles.append([middleElfIndex, biggestElfIndex])
        
    print(len(battles))
    for i in range(len(battles)):
        print(*battles[i])


    

    