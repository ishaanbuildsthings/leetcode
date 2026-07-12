# dsu = RollbackDSU(arr)
# takes an array of values (can be array of strings, tuples, etc) since everything operates on indices

class RollbackDSU:
    # O(n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0
        self._stk = []

    # O(log n), no path compression, so depth is bounded by union by size alone
    def find(self, i):
        par = self.par
        while par[i] != i:
            i = par[i]
        return i

    # O(log n), merges the two components, False if i and j were already together
    # either way it records a frame, so it always takes exactly one rollback to undo
    def unite(self, i, j):
        i, j = self.find(i), self.find(j)
        if i == j:
            self._stk.append(None)
            return False
        if self.sz[i] < self.sz[j]:
            i, j = j, i
        self._stk.append((i, j, self.mx))
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        self.mx = max(self.mx, self.sz[i])
        return True

    # O(1), undoes the single most recent unite, whether or not that unite merged anything
    # a unite that returned False changed nothing, so its rollback changes nothing, but it
    # still counts: k rollbacks always undo the last k unites
    # IndexError if you roll back more unites than you made
    def rollback(self):
        frame = self._stk.pop()
        if frame is None:
            return
        i, j, mx = frame
        self.par[j] = j
        self.sz[i] -= self.sz[j]
        self.comps += 1
        self.mx = mx

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