import math

def solve():
    n, tagCost = map(int, input().split())
    prices = list(map(int, input().split()))
    res = float('-inf')
    mx = max(prices)

    if (mx == 1):
        print(n)
        return

    frq = [0] * (mx + 1)
    for v in prices:
        frq[v] += 1

    pf = []
    curr = 0
    for v in range(mx + 1):
        curr += frq[v]
        pf.append(curr)
    
    def rangeCount(l, r):
        if not l:
            return pf[r]
        return pf[r] - pf[l - 1]

    for x in range(2, mx + 1):
        maxCeilPrice = math.ceil(mx / x)
        resHere = 0
        for ceilPrice in range(1, maxCeilPrice + 1):
            # which original price tags yield this ceiling price when divided by X?
            L = (x * ceilPrice) - x + 1 # say x=10 and we have price 30, lowest is 291
            R = (x * ceilPrice) # R can be at most 300
            R = min(R, mx)
            # print(f'{L=} {R=} {x=} {ceilPrice=}')
            tagsInRange = rangeCount(L, R) # how many tags get remapped to ceilPrice
            avail = frq[ceilPrice]
            printed = 0
            if tagsInRange > avail:
                printed = tagsInRange - avail
            resHere -= tagCost * printed
            resHere += ceilPrice * tagsInRange
        res = max(res, resHere)
    
    print(res)



            

t = int(input())
for _ in range(t):
    solve()