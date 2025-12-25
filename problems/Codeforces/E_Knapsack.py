W = int(input())
counts = [0] + list(map(int, input().split()))

# we need to know the most blocks we can take for certain remainders.
# Claim is that the max remainder we need to consider is 8*840 - 1. Why not a larger remainder? Any sum >= 8*840 necessarily has a block of 840 fully formable by one number type.
# We could subtract that full block and have dp[remainder - 840] + 1 already capture that case.
# What is the lower bound on the remainders we need to consider? Not sure but I tried 839 and it got WA. Seems hard to prove a lower bound.

dp = [-float('inf')] * (8 * 840) # dp[remainder] is the most blocks we can get with that remainder (total weight can exceed W)
dp[0] = 0

# Update best blocks table before and after considering this weight
for weight in range(1, 9):
    count = counts[weight]
    perBlock = 840 // weight
    mostRemainderQuantityTakeable = min(count, perBlock - 1)

    ndp = [-float('inf')] * (8 * 840)
    ndp[0] = 0
    
    # If we took this many remainder here
    for takeRemainder in range(mostRemainderQuantityTakeable + 1): # at most 840
        takenWeight = takeRemainder * weight
        piecesLeft = count - takeRemainder
        blocksAvailable = piecesLeft // perBlock

        for prevRemainder in range(8 * 840):
            newRemainder = takenWeight + prevRemainder
            if newRemainder >= 8 * 840: break
            ndp[newRemainder] = max(ndp[newRemainder], dp[prevRemainder] + blocksAvailable)
    
    dp = ndp

res = 0
for remainder in range(8 * 840):
    mostBlocksWeCanMake = dp[remainder]
    mostBlocksWeCanTakeUnderW = (W - remainder) // 840
    usedBlocks = min(mostBlocksWeCanMake, mostBlocksWeCanTakeUnderW)
    totalWeight = usedBlocks * 840 + remainder
    res = max(res, totalWeight)

print(res)


