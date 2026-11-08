# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/rollback-values-merge-edges-potential/template.py
# @operations: areUnioned checkpoint componentData componentMax componentMin componentSum diff edgeCount elementsInGroup find groups isTree largestSize numComponents rollbackLastUnion rollbackTo roots size sizes uniteWeighted
# @data-structure-type: dsu-rollback
# @complexities:
#   areUnioned: log(N)
#   checkpoint: 1
#   componentData: log(N)
#   componentMax: log(N)
#   componentMin: log(N)
#   componentSum: log(N)
#   diff: log(N)
#   edgeCount: log(N)
#   elementsInGroup: N*log(N)
#   find: log(N)
#   groups: N*log(N)
#   isTree: log(N)
#   largestSize: 1
#   numComponents: 1
#   rollbackLastUnion: 1
#   rollbackTo: 1 amortized
#   roots: N
#   size: log(N)
#   sizes: N*log(N)
#   uniteWeighted: log(N)
#   build: N
# @memory:
#   layout: none
#   node: par[1*N] sz[1*N]
#   tags: none
#   other: vals[1*N] csum[1*N] cmin[1*N] cmax[1*N] data[1*N] edges[1*N] pot[1*N]
#   note: plus the undo stack: one small frame per unite not yet undone, holding a copy of the bigger Node; data holds one Node per element

# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


def baseFn(v: RawVal, i: int) -> Node:
    # return (v, v)
    pass


# called once per merge: big is the bigger component's Node (on a tie, either one). Don't mutate big: rollback keeps the old
# Node to put it back, so return a new one
def combine(big: Node, small: Node) -> Node:
    # return (big[0] + small[0], max(big[1], small[1]))
    pass


# dsu = RollbackDSU(vals, baseFn, combine)
# vals: the elements (numbers: componentSum / Min / Max are over them); everything works on their indices 0..n-1
# potential: every element has a hidden number value[i]; uniteWeighted(i, j, w) says value[j] - value[i] = w and diff(i, j)
# reads it back (for parity / two-colouring, swap + and - for ^ throughout)


class RollbackDSU:
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
        self.edges = [0] * n  # edges[root]: how many unites touched root's component, merging or not
        self.pot = [0] * n  # pot[i] = value[i] - value[par[i]] (0 at a root)
        self.stk = []  # one frame per unite, so rollback can undo it

    # O(log n), index of the representative of i's component; parents are never rewritten, so any unite can be undone
    def find(self, i):
        par = self.par
        while par[i] != i:
            i = par[i]
        return i

    # (root of i, value[i] - value[root])
    def _rootAndWeight(self, i):
        par, pot = self.par, self.pot
        w = 0
        while par[i] != i:
            w += pot[i]
            i = par[i]
        return i, w

    # O(log n), merges the two components, False if i and j were already together
    # w: value[j] - value[i] = w. Already together: nothing changes (diff(i, j) == w says if this agrees)
    # either way it counts as an edge of the component (edgeCount)
    # either way it records a frame, so it always takes exactly one rollbackLastUnion to undo
    def uniteWeighted(self, i, j, w):
        i, wi = self._rootAndWeight(i)
        j, wj = self._rootAndWeight(j)
        if i == j:
            self.edges[i] += 1
            self.stk.append(i)  # (an int frame: only the edge count to undo)
            return False
        w += wi - wj  # now value[j's root] - value[i's root]
        if self.sz[i] < self.sz[j]:
            i, j = j, i
            w = -w
        self.stk.append((i, j, self.mx, self.cmin[i], self.cmax[i], self.data[i]))
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
        self.edges[i] += self.edges[j] + 1
        self.pot[j] = w
        return True

    # O(1), undoes the most recent unite, whether or not it merged anything: k calls always undo the last
    # k unites; IndexError if there's no unite left to undo
    def rollbackLastUnion(self):
        frame = self.stk.pop()
        if type(frame) is int:
            self.edges[frame] -= 1
            return
        i, j, mx, lo, hi, data = frame
        self.par[j] = j
        self.sz[i] -= self.sz[j]
        self.comps += 1
        self.mx = mx
        self.csum[i] -= self.csum[j]
        self.cmin[i] = lo
        self.cmax[i] = hi
        self.data[i] = data
        self.edges[i] -= self.edges[j] + 1
        self.pot[j] = 0

    # O(1), a point to roll back to later: how many unites can be undone right now
    def checkpoint(self):
        return len(self.stk)

    # O(1) per unite undone, undoes every unite made since checkpoint() returned k
    def rollbackTo(self, k):
        while len(self.stk) > k:
            self.rollbackLastUnion()

    # O(log n), True if i and j are in the same component
    def areUnioned(self, i, j):
        return self.find(i) == self.find(j)

    # O(log n), how many elements are in i's component
    def size(self, i):
        return self.sz[self.find(i)]

    # O(1), how many components exist right now
    def numComponents(self):
        return self.comps

    # O(1), size of the biggest component, restored by rollback
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
            groupsArr[self.find(i)].append(self.vals[i])
        return groupsArr

    # O(n log n), the values of every element sitting in the same group as index i
    def elementsInGroup(self, i):
        rt = self.find(i)
        return [self.vals[j] for j in range(len(self.par)) if self.find(j) == rt]

    # O(log n), the sum of the values in i's component
    def componentSum(self, i):
        return self.csum[self.find(i)]

    # O(log n), the smallest of the values in i's component
    def componentMin(self, i):
        return self.cmin[self.find(i)]

    # O(log n), the largest of the values in i's component
    def componentMax(self, i):
        return self.cmax[self.find(i)]

    # O(log n), the Node of i's component: every member's baseFn, combined
    def componentData(self, i):
        return self.data[self.find(i)]

    # O(log n), how many unites have touched i's component (merging or not): its edges, if each unite is an edge
    def edgeCount(self, i):
        return self.edges[self.find(i)]

    # O(log n), True if i's component has no cycle: exactly size - 1 edges
    def isTree(self, i):
        r = self.find(i)
        return self.edges[r] == self.sz[r] - 1

    # O(log n), value[j] - value[i] from the unites so far, None if i and j aren't together
    def diff(self, i, j):
        ri, wi = self._rootAndWeight(i)
        rj, wj = self._rootAndWeight(j)
        return wj - wi if ri == rj else None
