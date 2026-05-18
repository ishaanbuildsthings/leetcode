n = int(input())
P = list(map(int, input().split()))
C = list(map(int, input().split()))


from bisect import bisect_left
from math import inf


m = int(input())
users = [] # holds (political tolerance, cultural tolernace, influence)

TPs = list(map(int, input().split()))
TCs = list(map(int, input().split()))
Ds = list(map(int, input().split()))

for i in range(m):
    users.append((TPs[i], TCs[i], Ds[i]))

news = []
for i in range(n):
    news.append((P[i], C[i]))
# holds (p, c) sorted
news.sort()

print(f'{users=}')

print(f'{news=}')

pfCMin = []
curr = inf
for p, c in news:
    curr = min(curr, c)
    pfCMin.append(curr)

# holds (p, c) sorted by C
news2 = sorted(news,key=lambda x: x[1])

pfPMin = []
curr = inf
for p, c in news2:
    curr = min(curr, p)
    pfPMin.append(curr)

# tells us if there is a news with np < p, and nc < c
def lessBoth(p, c):
    # rightmost tuple index with np < p
    rightmost = bisect_left(news, X, key=lambda t: t[0]) - 1
    if rightmost == -1:
        return False
    minC = pfCMin[rightmost]
    return minC < c


# smallest C when we have np < p
def minCforP(p, c):
    rightmost = bisect_left(news, X, key=lambda t: t[0]) - 1
    if rightmost == -1:
        return inf
    return pfCMin[rightmost]

# smallest P when we have nc < c
def minPForC(p, c):
    rightmost = bisect_left(news2, X, key=lambda t: t[1]) - 1
    if rightmost == -1:
        return inf
    return pfPMin[rightmost]

# for every p, what is its min C?

maxP = max(P)
pToMinC = [inf] * (maxP + 1)
for p, c in news:
    pToMinC[p] = min(pToMinC[p], c)

pSums = [0] * (max(P) + 1)
for p in range(maxP + 1):
    mnC = pToMinC[p]
    tot = mnC + p
    pSums[p] = tot


    

    