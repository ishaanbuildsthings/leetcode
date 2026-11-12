# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/rollback-merge-members-potential/template.py
# @operations: areUnioned checkpoint componentData diff elementsInGroup find groups largestSize numComponents rollbackLastUnion rollbackTo roots size sizes uniteWeighted
# @data-structure-type: dsu-rollback
# @complexities:
#   areUnioned: log(N)
#   checkpoint: 1
#   componentData: log(N)
#   diff: log(N)
#   elementsInGroup: K
#   find: log(N)
#   groups: N*log(N)
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
#   other: vals[1*N] data[1*N] nxt[1*N] pot[1*N]
#   note: K = the size of the group; plus the undo stack: one small frame per unite not yet undone, holding a copy of the bigger Node; data holds one Node per element

# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


def baseFn(v: RawVal, i: int) -> Node:
    # return (v, v)
    pass


# called once per merge: big is the bigger component's Node (on a tie, either one). Don't mutate big: rollback keeps the
# old
# Node to put it back, so return a new one
def combine(big: Node, small: Node) -> Node:
    # return (big[0] + small[0], max(big[1], small[1]))
    pass


# dsu = RollbackDSU(vals, baseFn, combine)
# vals: the elements (any values: numbers, strings, tuples, ...); everything works on their indices 0..n-1 potential:
# every element has a hidden number value[i]; uniteWeighted(i, j, w) says value[j] - value[i] = w and diff(i, j) reads
# it back (for parity / two-colouring, swap + and - for ^ throughout)


class RollbackDSU:
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
    # w: value[j] - value[i] = w. Already together: nothing changes (diff(i, j) == w says if this agrees) either way it
    # records a frame, so it always takes exactly one rollbackLastUnion to undo
    def uniteWeighted(self, i, j, w):
        i, wi = self._rootAndWeight(i)
        j, wj = self._rootAndWeight(j)
        if i == j:
            self.stk.append(None)
            return False
        w += wi - wj  # now value[j's root] - value[i's root]
        if self.sz[i] < self.sz[j]:
            i, j = j, i
            w = -w
        self.stk.append((i, j, self.mx, self.data[i]))
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        if self.sz[i] > self.mx:
            self.mx = self.sz[i]
        self.data[i] = self.combine(self.data[i], self.data[j])
        self.nxt[i], self.nxt[j] = self.nxt[j], self.nxt[i]  # (joins the two circles)
        self.pot[j] = w
        return True

    # O(1), undoes the most recent unite, whether or not it merged anything: k calls always undo the last
    # k unites; IndexError if there's no unite left to undo
    def rollbackLastUnion(self):
        frame = self.stk.pop()
        if frame is None:
            return
        i, j, mx, data = frame
        self.par[j] = j
        self.sz[i] -= self.sz[j]
        self.comps += 1
        self.mx = mx
        self.data[i] = data
        self.nxt[i], self.nxt[j] = self.nxt[j], self.nxt[i]  # (the same swap splits them again)
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

    # O(size of the group), the values of every element in the same group as index i, starting at i
    def elementsInGroup(self, i):
        vals, nxt = self.vals, self.nxt
        res = [vals[i]]
        j = nxt[i]
        while j != i:
            res.append(vals[j])
            j = nxt[j]
        return res

    # O(log n), the Node of i's component: every member's baseFn, combined
    def componentData(self, i):
        return self.data[self.find(i)]

    # O(log n), value[j] - value[i] from the unites so far, None if i and j aren't together
    def diff(self, i, j):
        ri, wi = self._rootAndWeight(i)
        rj, wj = self._rootAndWeight(j)
        return wj - wi if ri == rj else None
