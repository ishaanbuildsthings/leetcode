import math
n, forgot = map(int, input().split())
A = list(map(lambda x: int(x) - 1, input().split())) # i-th ball will bring A[i] a ball

class DSU:
    def __init__(self, n):
        self.parents = [i for i in range(n)] # maps a node to its representative
        self.sz = [1] * n # sizes of represenative components
    
    def find(self, x):
        # path compression
        while x != self.parents[x]:
            self.parents[x] = self.parents[self.parents[x]]
            x = self.parents[x]
        return x
        
    def union(self, a, b):
        p1 = self.find(a)
        p2 = self.find(b)
        if p1 == p2:
            return False
        s1 = self.sz[p1]
        s2 = self.sz[p2]
        if s1 <= s2:
            self.parents[p1] = p2
            self.sz[p2] += self.sz[p1]
        else:
            self.parents[p2] = p1
            self.sz[p1] += self.sz[p2]
        return True

dsu = DSU(n)
for fr, to in enumerate(A):
    dsu.union(fr, to)
roots = set(dsu.find(x) for x in range(n))
sizes = [dsu.sz[root] for root in roots]

frq = [0] * (n + 1) # how many components have that size
for sz in sizes:
    frq[sz] += 1

bundles = []
for pieceSize, pieceFrq in enumerate(frq):
    power = 0
    remain = pieceFrq
    while remain:
        lostPieces = min(2**power, remain)
        bundles.append(lostPieces * pieceSize)
        remain -= lostPieces
        power += 1

bs = 1
for b in bundles:
    bs |= bs << b

# if exact forgot is doable, our min lost gifts is k, else k+1
minLost = forgot if (1 << forgot) & bs else forgot + 1


# Maximum lost, for all even sized components we can lose exactly half, each time scoring two
# For all odd sized components, we can spend size//2 to lose twice that many, after that, an odd sized component can only let us lose 1 more

loseableDoubles = 0
oddComponentsThatCanLoseOneMore = 0
for sz, cnt in enumerate(frq):
    loseableDoublesPerPiece = sz // 2
    loseableDoubles += loseableDoublesPerPiece * cnt
    if sz % 2:
        oddComponentsThatCanLoseOneMore += cnt

actualLostDoubles = min(forgot, loseableDoubles)
res = 2 * actualLostDoubles
remainingForgot = forgot - actualLostDoubles
res += min(remainingForgot, oddComponentsThatCanLoseOneMore)
print(f'{minLost} {res}')