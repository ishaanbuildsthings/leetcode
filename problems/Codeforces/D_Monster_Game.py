import bisect

def countLte(sortedArr, x):
    return bisect.bisect_right(sortedArr, x)


def largestIndexLTE(sortedArr, x):
    left = 0
    right = len(sortedArr) - 1
    best = -1
    while left <= right:
        mid = (left + right) // 2
        if sortedArr[mid] <= x:
            best = mid
            left = mid + 1
        else:
            right = mid - 1
    return best


def solve():
    n = int(input())
    swordStrengths = list(map(int, input().split()))
    swordStrengths.sort()
    strikes = list(map(int, input().split()))

    # difficulty X means we lose some amount of swords
    interesting = set()
    for sword in swordStrengths:
        interesting.add(str(sword))
        interesting.add(str(sword+1))
        interesting.add(str(sword-1))
    interesting.add('0')
    
    req = []
    cur = 0
    for v in strikes:
        cur += v
        req.append(cur)
    
    totalStrikes = sum(strikes)
    res = 0
    values = sorted(list(int(x) for x in interesting))
    for v in values:
        # difficulty is v
        # we lose swords < v
        swordsLost = countLte(swordStrengths, v - 1)
        remain = n - swordsLost
        largest = largestIndexLTE(req, remain)
        if largest == -1:
            continue
        beaten = largest + 1
        score = beaten * v
        res = max(res, score)
    
    print(res)



    

t = int(input())
for _ in range(t):
    solve()