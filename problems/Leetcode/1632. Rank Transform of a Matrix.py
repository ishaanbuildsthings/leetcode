# dsu = DSU(arr)
# takes an array of values (can be array of strings, tuples, etc) since everything operates on indices

class DSU:
    # O(n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0

    # O(1), index of the representative of i's component
    def find(self, i):
        par = self.par
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    # O(1), merges the two components, False if i and j were already together
    def unite(self, i, j):
        i, j = self.find(i), self.find(j)
        if i == j:
            return False
        if self.sz[i] < self.sz[j]:
            i, j = j, i
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        self.mx = max(self.mx, self.sz[i])
        return True

    # O(1), True if i and j are in the same component
    def areUnioned(self, i, j):
        return self.find(i) == self.find(j)

    # O(1), how many elements are in i's component
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

    # O(n), groupsArr[rt] = list of values whose root is rt, [] if rt is not a root
    def groups(self):
        n = len(self.par)
        groupsArr = [[] for _ in range(n)]
        for i in range(n):
            rt = self.find(i)
            groupsArr[rt].append(self.vals[i])
        return groupsArr

    # O(n), the values of every element sitting in the same group as index i
    def elementsInGroup(self, i):
        rt = self.find(i)
        return [self.vals[j] for j in range(len(self.par)) if self.find(j) == rt]


class Solution:
    def matrixRankTransform(self, matrix: List[List[int]]) -> List[List[int]]:
        height = len(matrix)
        width = len(matrix[0])

        uniq = set()
        groups = defaultdict(list) # maps val -> [(r, c), ...]
        for r in range(height):
            for c in range(width):
                v = matrix[r][c]
                groups[v].append((r, c))
                uniq.add(v)
        vals = sorted(uniq)
        
        res = []
        for r in range(height):
            res.append([None] * width)
        
        rowmx = defaultdict(int)
        colmx = defaultdict(int)

        for v in vals:
            # each value wants to be the previous smallest value in that row or col, +1
            wants = [] # holds (r, c, wantedVal)
            byRow = defaultdict(list) # maps r -> [c, ...]
            byCol = defaultdict(list) 
            for r, c in groups[v]:
                minr = 1 + rowmx[r]
                minc = 1 + colmx[c]
                wanted = max(minr, minc)
                wants.append((r, c, wanted))
                byRow[r].append(c)
                byCol[c].append(r)
            dsu = DSU(wants)
            rcToIdx = {}
            for i, (r, c, _) in enumerate(wants):
                rcToIdx[r, c] = i
            for r, bucket in byRow.items():
                for i in range(1, len(bucket)):
                    c = bucket[i]
                    idx = rcToIdx[r, c]
                    pidx = rcToIdx[r, bucket[i - 1]]
                    dsu.unite(idx, pidx)
            for c, bucket in byCol.items():
                for i in range(1, len(bucket)):
                    r = bucket[i]
                    idx = rcToIdx[r, c]
                    pidx = rcToIdx[bucket[i - 1], c]
                    dsu.unite(idx, pidx)
            grouped = dsu.groups()
            for group in grouped:
                if not group: continue
                mx = -inf
                for r, c, wanted in group:
                    mx = max(mx, wanted)
                for r, c, wanted in group:
                    res[r][c] = mx
                    rowmx[r] = mx
                    colmx[c] = mx
        return res
            


                





        