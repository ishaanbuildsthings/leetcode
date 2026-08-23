# dsu = DSUNoCompress(arr)
# takes an array of values (can be array of strings, tuples, etc) since everything operates on indices

class DSUNoCompress:
    # O(n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0

    # O(log n), index of the representative of i's component, parents left untouched
    def find(self, i):
        par = self.par
        while par[i] != i:
            i = par[i]
        return i

    # O(log n), merges the two components, returns (winner, loser) or None if already together
    def unite(self, i, j):
        i, j = self.find(i), self.find(j)
        if i == j:
            return None
        if self.sz[i] < self.sz[j]:
            i, j = j, i
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        self.mx = max(self.mx, self.sz[i])
        return i, j

    # O(log n), forces a's root under b's root, False if already together
    # skips union by size, so depth can degrade to O(n) and every walk with it
    def uniteAUnderB(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        self.par[a] = b
        self.sz[b] += self.sz[a]
        self.comps -= 1
        self.mx = max(self.mx, self.sz[b])
        return True

    # O(log n), True if i and j are in the same component
    def areUnioned(self, i, j):
        return self.find(i) == self.find(j)

    # O(log n), how many elements are in i's component
    def size(self, i):
        return self.sz[self.find(i)]

    # O(1), how many components exist right now
    def numComponents(self):
        return self.comps

    # O(1), size of the biggest component, maintained in unite
    def largestSize(self):
        return self.mx

    # O(n), one index per component: the representative each member's find returns
    def roots(self):
        return [i for i in range(len(self.par)) if self.par[i] == i]

    # O(n log n), the sizes of all components, biggest first, e.g. [4, 2, 1]
    def sizes(self):
        return sorted((self.sz[i] for i in range(len(self.par)) if self.par[i] == i), reverse=True)

    # O(n log n), groupsArr[rt] = list of values whose root is rt, [] if rt is not a root
    def groups(self):
        n = len(self.par)
        groupsArr = [[] for _ in range(n)]
        for i in range(n):
            rt = self.find(i)
            groupsArr[rt].append(self.vals[i])
        return groupsArr

    # O(n log n), the values of every element sitting in the same group as index i
    def elementsInGroup(self, i):
        rt = self.find(i)
        return [self.vals[j] for j in range(len(self.par)) if self.find(j) == rt]
import sys
n, m, q = map(int, input().split())
dsu = DSUNoCompress(list(range(n + 1)))
upTime = [float('inf')] * (n + 1)
for time in range(1, m + 1):
    a, b = map(int, input().split())
    # print(f'{a=} {b=} for road')
    if dsu.areUnioned(a, b):
        continue
    aSz = dsu.size(a)
    bSz = dsu.size(b)
    if aSz >= bSz:
        a, b = b, a
    # a goes under b
    aRt = dsu.find(a)
    dsu.uniteAUnderB(a, b)
    upTime[aRt] = time
# print('-----')
out = []
for i in range(q):
    a, b = map(int, input().split())
    # print(f'{a=} {b=} for query')
    if not dsu.areUnioned(a, b):
        out.append(-1)
        continue
    aptr = a
    bptr = b
    resHere = 0
    while aptr != bptr:
        aTime = upTime[aptr]
        bTime = upTime[bptr]
        # print(f'{aTime=} {bTime=}')
        if aTime <= bTime:
            aptr = dsu.par[aptr]
            resHere = max(resHere, aTime)
        else:
            bptr = dsu.par[bptr]
            resHere = max(resHere, bTime)
    out.append(resHere)

sys.stdout.write('\n'.join(map(str, out)))
        
        
