# import functools

# MOD = 10**9 + 7

# def deleteBit(mask, pos): # pos is 0-indexed from LSB
#     low = mask & ((1 << pos) - 1)
#     high = mask >> (pos + 1)
#     return low | (high << pos)

# fmax = lambda x, y: x if x > y else y
# fmin = lambda x, y: x if x < y else y

# t = int(input())
# for _ in range(t):
#     n, maxPileSize = map(int, input().split())
#     k = int(input())

#     goodIds = sorted(map(lambda x: int(x) - 1, input().split()))

#     if maxPileSize == 1:
#         print(1)
#         continue

#     fmask = (1 << n) - 1

#     @functools.lru_cache(maxsize=None)
#     def dp(numPiles, remainingBoard, isAlice):
#         if numPiles == 1:
#             return remainingBoard + 1
#         res = 1 if isAlice else 2
#         fn = fmax if isAlice else fmin
#         for bit in goodIds:
#             if bit + 1 > numPiles:
#                 break
#             newBoard = deleteBit(remainingBoard, bit)
#             res = fn(res, dp(numPiles - 1, newBoard, not isAlice))
#         return res
    
#     res = 0
#     for config in range(fmask + 1):
#         res += dp(n, config, True)
#         res %= MOD
#     print(res)


import functools

MOD = 10**9 + 7

fmax = lambda x, y: x if x > y else y
fmin = lambda x, y: x if x < y else y

def deleteBit(mask, pos): # pos is 0-indexed from LSB
    low = mask & ((1 << pos) - 1)
    high = mask >> (pos + 1)
    return low | (high << pos)

t = int(input())
for _ in range(t):
    n, maxPileSize = map(int, input().split())
    k = int(input())

    goodIds = sorted(map(lambda x: int(x) - 1, input().split()))

    if maxPileSize == 1:
        print(1)
        continue

    fmask = (1 << n) - 1

    dpCache = []
    for numPiles in range(n + 1):
        dpCache.append([[-1] * (1 << numPiles) for _ in range(2)])

    def dp(numPiles, remainingBoard, isAlice):
        cached = dpCache[numPiles][isAlice][remainingBoard]
        if cached != -1:
            return cached
        if numPiles == 1:
            val = remainingBoard + 1
            dpCache[numPiles][isAlice][remainingBoard] = val
            return val
        res = 1 if isAlice == 1 else 2
        fn = fmax if isAlice == 1 else fmin
        for bit in goodIds:
            if bit + 1 > numPiles:
                break
            newBoard = deleteBit(remainingBoard, bit)
            res = fn(res, dp(numPiles - 1, newBoard, 1 - isAlice))
        dpCache[numPiles][isAlice][remainingBoard] = res
        return res
    
    res = 0
    for config in range(fmask + 1):
        res += dp(n, config, 1)
        res %= MOD
    print(res)
