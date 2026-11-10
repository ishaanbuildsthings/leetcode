# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/compress-merge-members/template.py
# @operations: areUnioned componentData elementsInGroup find groups largestSize numComponents roots size sizes unite
# @data-structure-type: dsu
# @complexities:
#   areUnioned: α(N) amortized
#   componentData: α(N) amortized
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
#   other: vals[1*N] data[1*N] nxt[1*N]
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
# vals: the elements (any values: numbers, strings, tuples, ...); everything works on their indices 0..n-1


class DSU:
    # O(n), every element starts in its own component
    def __init__(self, vals, baseFn, combine):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0
        self.baseFn, self.combine = baseFn, combine
        self.data = [baseFn(v, i) for i, v in enumerate(self.vals)]  # data[root]: the Node of root's component
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
        self.data[i] = self.combine(self.data[i], self.data[j])
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

    # O(α(n)) amortized, the Node of i's component: every member's baseFn, combined
    def componentData(self, i):
        return self.data[self.find(i)]
