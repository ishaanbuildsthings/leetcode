# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/nocompress-merge-grow/template.py
# @operations: add areUnioned componentData elementsInGroup find groups largestSize numComponents parent roots size sizes unite
# @data-structure-type: dsu-nocompress
# @complexities:
#   add: 1 amortized
#   areUnioned: log(N)
#   componentData: log(N)
#   elementsInGroup: N*log(N)
#   find: log(N)
#   groups: N*log(N)
#   largestSize: 1
#   numComponents: 1
#   parent: 1
#   roots: N
#   size: log(N)
#   sizes: N*log(N)
#   unite: log(N)
#   build: N
# @memory:
#   layout: none
#   node: par[1*N] sz[1*N]
#   tags: none
#   other: vals[1*N] data[1*N]
#   note: data holds one Node per element

# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


def baseFn(v: RawVal, i: int) -> Node:
    # return (v, v)
    pass


# called once per merge: big is the bigger component's Node (on a tie, either one). Mutating big and returning it is fine, e.g.
# small-to-large: big |= small; return big (O(n log n) in total)
def combine(big: Node, small: Node) -> Node:
    # return (big[0] + small[0], max(big[1], small[1]))
    pass


# dsu = DSUNoCompress(vals, baseFn, combine)
# vals: the elements (any values: numbers, strings, tuples, ...); everything works on their indices 0..n-1, and add(val) appends more


class DSUNoCompress:
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

    # O(log n), index of the representative of i's component; parents are never rewritten, so the forest records every merge
    def find(self, i):
        par = self.par
        while par[i] != i:
            i = par[i]
        return i

    # O(log n), merges the two components, returns (winner, loser): the new root and the old root now under it, or
    # None if they were already together
    def unite(self, i, j):
        i, j = self.find(i), self.find(j)
        if i == j:
            return None
        if self.sz[i] < self.sz[j]:
            i, j = j, i
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        if self.sz[i] > self.mx:
            self.mx = self.sz[i]
        self.data[i] = self.combine(self.data[i], self.data[j])
        return i, j

    # O(1), i's parent pointer (i itself if it's a root): without path compression the pointers never change
    # once set, so you can walk them and keep your own data per pointer
    def parent(self, i):
        return self.par[i]

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

    # O(n log n), one list of values per component (no empty lists), e.g. vals [10, 20, 30, 40] with 0-2 and 1-3
    # united -> [[10, 30], [20, 40]]; components ordered by their smallest index, values in index order
    def groups(self):
        n = len(self.par)
        slot = [-1] * n  # slot[rt] = where root rt's list sits in groupsArr
        groupsArr = []
        for i in range(n):
            rt = self.find(i)
            if slot[rt] == -1:
                slot[rt] = len(groupsArr)
                groupsArr.append([])
            groupsArr[slot[rt]].append(self.vals[i])
        return groupsArr

    # O(n log n), the values of every element sitting in the same group as index i
    def elementsInGroup(self, i):
        rt = self.find(i)
        return [self.vals[j] for j in range(len(self.par)) if self.find(j) == rt]

    # O(log n), the Node of i's component: every member's baseFn, combined
    def componentData(self, i):
        return self.data[self.find(i)]

    # O(1), adds a new element in its own component and returns its index
    def add(self, val):
        i = len(self.par)
        self.vals.append(val)
        self.par.append(i)
        self.sz.append(1)
        self.comps += 1
        if self.mx < 1:
            self.mx = 1
        self.data.append(self.baseFn(val, i))
        return i
