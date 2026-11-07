# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/compress-edges-potential-grow/template.py

# dsu = DSU(vals)
# vals: the elements (any values: numbers, strings, tuples, ...); everything works on their indices 0..n-1, and add(val) appends more
# potential: every element has a hidden number value[i]; unite(i, j, w) says value[j] - value[i] = w and diff(i, j)
# reads it back (for parity / two-colouring, swap + and - for ^ throughout)


class DSU:
    # O(n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0
        self.edges = [0] * n  # edges[root]: how many unites touched root's component, merging or not
        self.pot = [0] * n  # pot[i] = value[i] - value[par[i]] (0 at a root)

    # O(α(n)) amortized, effectively O(1): index of the representative of i's component (compresses fully, keeping pot right)
    def find(self, i):
        par, pot = self.par, self.pot
        path = []
        while par[i] != i:
            path.append(i)
            i = par[i]
        for x in reversed(path):  # nearest the root first, so its parent's pot is already relative to the root
            p = par[x]
            if p != i:
                pot[x] += pot[p]
                par[x] = i
        return i

    # (root of i, value[i] - value[root])
    def _rootAndWeight(self, i):
        r = self.find(i)
        return r, self.pot[i]

    # O(α(n)) amortized, merges the two components, False if i and j were already together
    # w: value[j] - value[i] = w. Already together: nothing changes (diff(i, j) == w says if this agrees)
    # either way it counts as an edge of the component (edgeCount)
    def unite(self, i, j, w):
        i, wi = self._rootAndWeight(i)
        j, wj = self._rootAndWeight(j)
        if i == j:
            self.edges[i] += 1
            return False
        w += wi - wj  # now value[j's root] - value[i's root]
        if self.sz[i] < self.sz[j]:
            i, j = j, i
            w = -w
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        if self.sz[i] > self.mx:
            self.mx = self.sz[i]
        self.edges[i] += self.edges[j] + 1
        self.pot[j] = w
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

    # O(n), the values of every element sitting in the same group as index i
    def elementsInGroup(self, i):
        rt = self.find(i)
        return [self.vals[j] for j in range(len(self.par)) if self.find(j) == rt]

    # O(α(n)) amortized, how many unites have touched i's component (merging or not): its edges, if each unite is an edge
    def edgeCount(self, i):
        return self.edges[self.find(i)]

    # O(α(n)) amortized, True if i's component has no cycle: exactly size - 1 edges
    def isTree(self, i):
        r = self.find(i)
        return self.edges[r] == self.sz[r] - 1

    # O(α(n)) amortized, value[j] - value[i] from the unites so far, None if i and j aren't together
    def diff(self, i, j):
        ri, wi = self._rootAndWeight(i)
        rj, wj = self._rootAndWeight(j)
        return wj - wi if ri == rj else None

    # O(1), adds a new element in its own component and returns its index
    def add(self, val):
        i = len(self.par)
        self.vals.append(val)
        self.par.append(i)
        self.sz.append(1)
        self.comps += 1
        if self.mx < 1:
            self.mx = 1
        self.edges.append(0)
        self.pot.append(0)
        return i
