# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/compress-values-members-grow/template.py
# @operations: add areUnioned componentMax componentMin componentSum elementsInGroup find groups largestSize numComponents roots size sizes unite
# @data-structure-type: dsu
# @complexities:
#   add: 1 amortized
#   areUnioned: α(N) amortized
#   componentMax: α(N) amortized
#   componentMin: α(N) amortized
#   componentSum: α(N) amortized
#   elementsInGroup: K
#   find: α(N) amortized
#   groups: N
#   largestSize: 1
#   numComponents: 1
#   roots: N
#   size: α(N) amortized
#   sizes: N*log(N)
#   unite: α(N) amortized
#   build: N
# @memory:
#   layout: none
#   node: par[1*N] sz[1*N]
#   tags: none
#   other: vals[1*N] csum[1*N] cmin[1*N] cmax[1*N] nxt[1*N]
#   note: K = the size of the group

# dsu = DSU(vals)
# vals: the elements (numbers: componentSum / Min / Max are over them); everything works on their indices 0..n-1, and
# add(val) appends more


class DSU:
    # O(n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0
        # at each root: the sum, min and max of its component's values
        self.csum = list(self.vals)
        self.cmin = list(self.vals)
        self.cmax = list(self.vals)
        self.nxt = list(range(n))  # each component's members linked in a circle: i -> nxt[i] -> ... -> i

    # O(α(n)) amortized, effectively O(1): index of the representative of i's component
    def find(self, i):
        par = self.par
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    # O(α(n)) amortized, merges the two components, False if i and j were already together
    def unite(self, i, j):
        i, j = self.find(i), self.find(j)
        if i == j:
            return False
        if self.sz[i] < self.sz[j]:
            i, j = j, i
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        if self.sz[i] > self.mx:
            self.mx = self.sz[i]
        self.csum[i] += self.csum[j]
        if self.cmin[j] < self.cmin[i]:
            self.cmin[i] = self.cmin[j]
        if self.cmax[j] > self.cmax[i]:
            self.cmax[i] = self.cmax[j]
        self.nxt[i], self.nxt[j] = self.nxt[j], self.nxt[i]  # (joins the two circles)
        return True

    # O(α(n)) amortized, True if i and j are in the same component
    def areUnioned(self, i, j):
        return self.find(i) == self.find(j)

    # O(α(n)) amortized, how many elements are in i's component
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
            groupsArr[self.find(i)].append(self.vals[i])
        return groupsArr

    # O(size of the group), the values of every element in the same group as index i, starting at i
    def elementsInGroup(self, i):
        vals, nxt = self.vals, self.nxt
        res = [vals[i]]
        j = nxt[i]
        while j != i:
            res.append(vals[j])
            j = nxt[j]
        return res

    # O(α(n)) amortized, the sum of the values in i's component
    def componentSum(self, i):
        return self.csum[self.find(i)]

    # O(α(n)) amortized, the smallest of the values in i's component
    def componentMin(self, i):
        return self.cmin[self.find(i)]

    # O(α(n)) amortized, the largest of the values in i's component
    def componentMax(self, i):
        return self.cmax[self.find(i)]

    # O(1), adds a new element in its own component and returns its index
    def add(self, val):
        i = len(self.par)
        self.vals.append(val)
        self.par.append(i)
        self.sz.append(1)
        self.comps += 1
        if self.mx < 1:
            self.mx = 1
        self.csum.append(val)
        self.cmin.append(val)
        self.cmax.append(val)
        self.nxt.append(i)
        return i
