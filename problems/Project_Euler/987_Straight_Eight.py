from functools import cache
from itertools import product
from math import perm, factorial

# this is going to take a list of available cards and how many straight-flushes were pre-taken
# we then need to get more straights (allowing straight-flushes) to reach 8
def solve(cardCountsByRank, flushesTaken):
    @cache
    def dp(lowCard, count1, count2, count3, count4, count5, acesLeft, straightsTaken):
        if lowCard == 11:
            return 1 if straightsTaken == 8 else 0
        res = 0
        # how many straights will we take
        for take in range(min(count1, count2, count3, count4, count5, 8 - straightsTaken) + 1):
            ways = (perm(count1, take) * perm(count2, take) * perm(count3, take) * perm(count4, take) * perm(count5, take) // factorial(take))
            nextAcesLeft = count1 - take if lowCard == 1 else acesLeft
            if lowCard == 9:
                nextCount5 = nextAcesLeft
            elif lowCard == 10:
                nextCount5 = None # doesn't matter can be whatever
            else:
                nextCount5 = cardCountsByRank[lowCard + 5]
            res += ways * dp(lowCard + 1, count2 - take, count3 - take, count4 - take, count5 - take, nextCount5, nextAcesLeft, straightsTaken + take)
        return res

    return dp(1, *cardCountsByRank[1:1+5], cardCountsByRank[1], flushesTaken)


STRAIGHTS = [
    None,
    (1, 2, 3, 4, 5),
    (2, 3, 4, 5, 6),
    (3, 4, 5, 6, 7),
    (4, 5, 6, 7, 8),
    (5, 6, 7, 8, 9),
    (6, 7, 8, 9, 10),
    (7, 8, 9, 10, 11),
    (8, 9, 10, 11, 12),
    (9, 10, 11, 12, 13),
    (10, 11, 12, 13, 1),
]

# give one suit, which combos of straight-flushes with that suit can we form?
# initially holds the empty combo, no straight flushes from this suit
straightFlushesForSuit = [()] # holds (i), (i, j), (i, j), ... which are tuples of up to size 2 indicating those straight flushes
for i in range(1, 11):
    straightFlushesForSuit.append((i,))
    for j in range(i + 1, 11):
        if not set(STRAIGHTS[i]) & set(STRAIGHTS[j]):
            straightFlushesForSuit.append((i, j))

outerCache = {} # we might pick an A-5 club flush and an A-5 heart flush in two separate ones, basically computing the same thing, we de-dupe here
res = 0
# we want to compute combos of mixed-suit straight flushes, that is what product does
# choice might look like ((3,), (), (1, 9), ())
for choice in product(straightFlushesForSuit, repeat=4):
    flushCount = sum(len(tup) for tup in choice)
    cardCountsByRank = [0] + [4] * 13
    for tup in choice:
        for low in tup:
            for rank in STRAIGHTS[low]:
                cardCountsByRank[rank] -= 1
    key = tuple(cardCountsByRank)
    if key in outerCache:
        ways = outerCache[key]
    else:
        ways = solve(key, flushCount)
        outerCache[key] = ways
    if flushCount % 2 == 1:
        res -= ways
    else:
        res += ways

print(res)