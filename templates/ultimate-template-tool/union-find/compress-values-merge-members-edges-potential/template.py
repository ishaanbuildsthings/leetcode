# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/compress-values-merge-members-edges-potential/template.py
# @operations: areUnioned componentData componentMax componentMin componentSum diff edgeCount elementsInGroup find groups isTree largestSize numComponents roots size sizes uniteWeighted
# @data-structure-type: dsu
# @complexities:
#   areUnioned: α(N) amortized
#   componentData: α(N) amortized
#   componentMax: α(N) amortized
#   componentMin: α(N) amortized
#   componentSum: α(N) amortized
#   diff: α(N) amortized
#   edgeCount: α(N) amortized
#   elementsInGroup: K
#   find: α(N) amortized
#   groups: N
#   isTree: α(N) amortized
#   largestSize: 1
#   numComponents: 1
#   roots: N
#   size: α(N) amortized
#   sizes: N*log(N)
#   uniteWeighted: α(N) amortized
#   build: N
# @memory:
#   layout: none
#   node: par[1*N] sz[1*N]
#   tags: none
#   other: vals[1*N] csum[1*N] cmin[1*N] cmax[1*N] data[1*N] nxt[1*N] edges[1*N] pot[1*N]
#   note: K = the size of the group; data holds one Node per element

# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


def baseFn(v: RawVal, i: int) -> Node:
    # return (v, v)
    pass


# called once per merge: big is the bigger component's Node (on a tie, either one). Mutating big and returning it is
# fine, e.g.
# small-to-large: big |= small; return big (O(n log n) in total)
def combine(big: Node, small: Node) -> Node:
    # return (big[0] + small[0], max(big[1], small[1]))
    pass


# dsu = DSU(vals, baseFn, combine)
# vals: the elements (numbers: componentSum / Min / Max are over them); everything works on their indices 0..n-1
# potential: every element has a hidden number value[i]; uniteWeighted(i, j, w) says value[j] - value[i] = w and diff(i,
# j)
# reads it back (for parity / two-colouring, swap + and - for ^ throughout)


class DSU:
    # O(n), every element starts in its own component
    def __init__(self, vals, baseFn, combine):
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
        self.baseFn, self.combine = baseFn, combine
        self.data = [baseFn(v, i) for i, v in enumerate(self.vals)]  # data[root]: the Node of root's component
        self.nxt = list(range(n))  # each component's members linked in a circle: i -> nxt[i] -> ... -> i
        self.edges = [0] * n  # edges[root]: how many unites touched root's component, merging or not
        self.pot = [0] * n  # pot[i] = value[i] - value[par[i]] (0 at a root)

    # O(α(n)) amortized, effectively O(1): index of the representative of i's component (compresses fully, keeping pot
    # right)
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
    def uniteWeighted(self, i, j, w):
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
        self.csum[i] += self.csum[j]
        if self.cmin[j] < self.cmin[i]:
            self.cmin[i] = self.cmin[j]
        if self.cmax[j] > self.cmax[i]:
            self.cmax[i] = self.cmax[j]
        self.data[i] = self.combine(self.data[i], self.data[j])
        self.nxt[i], self.nxt[j] = self.nxt[j], self.nxt[i]  # (joins the two circles)
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

    # O(α(n)) amortized, the Node of i's component: every member's baseFn, combined
    def componentData(self, i):
        return self.data[self.find(i)]

    # O(α(n)) amortized, how many unites have touched i's component (merging or not): its edges, if each unite is an
    # edge
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
