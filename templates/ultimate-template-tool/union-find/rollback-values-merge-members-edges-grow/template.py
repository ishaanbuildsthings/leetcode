# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/rollback-values-merge-members-edges-grow/template.py

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
# vals: the elements (numbers: componentSum / Min / Max are over them); everything works on their indices 0..n-1, and add(val) appends more


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
        self.nxt = list(range(n))  # each component's members linked in a circle: i -> nxt[i] -> ... -> i
        self.edges = [0] * n  # edges[root]: how many unites touched root's component, merging or not
        self.stk = []  # one frame per unite, so rollback can undo it

    # O(log n), index of the representative of i's component; parents are never rewritten, so any unite can be undone
    def find(self, i):
        par = self.par
        while par[i] != i:
            i = par[i]
        return i

    # O(log n), merges the two components, False if i and j were already together
    # either way it counts as an edge of the component (edgeCount)
    # either way it records a frame, so it always takes exactly one rollback to undo
    def unite(self, i, j):
        i, j = self.find(i), self.find(j)
        if i == j:
            self.edges[i] += 1
            self.stk.append(i)  # (an int frame: only the edge count to undo)
            return False
        if self.sz[i] < self.sz[j]:
            i, j = j, i
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
        self.nxt[i], self.nxt[j] = self.nxt[j], self.nxt[i]  # (joins the two circles)
        self.edges[i] += self.edges[j] + 1
        return True

    # O(1), undoes the most recent unite, whether or not it merged anything: k rollbacks always undo the last
    # k unites (an add is never undone); IndexError if you roll back more unites than you made
    def rollback(self):
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
        self.nxt[i], self.nxt[j] = self.nxt[j], self.nxt[i]  # (the same swap splits them again)
        self.edges[i] -= self.edges[j] + 1

    # O(1), a point to roll back to later: how many unites can be undone right now
    def checkpoint(self):
        return len(self.stk)

    # O(1) per unite undone, undoes every unite made since checkpoint() returned k
    def rollbackTo(self, k):
        while len(self.stk) > k:
            self.rollback()

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
        self.data.append(self.baseFn(val, i))
        self.nxt.append(i)
        self.edges.append(0)
        return i
