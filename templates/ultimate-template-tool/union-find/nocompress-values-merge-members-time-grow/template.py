# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/nocompress-values-merge-members-time-grow/template.py
# @operations: add areUnioned componentData componentMax componentMin componentSum connectedAt elementsInGroup find firstConnectedTime groups largestSize numComponents roots size sizes unite uniteAUnderB
# @data-structure-type: dsu-nocompress
# @complexities:
#   add: 1 amortized
#   areUnioned: log(N)
#   componentData: log(N)
#   componentMax: log(N)
#   componentMin: log(N)
#   componentSum: log(N)
#   connectedAt: log(N)
#   elementsInGroup: K
#   find: log(N)
#   firstConnectedTime: log(N)
#   groups: N*log(N)
#   largestSize: 1
#   numComponents: 1
#   roots: N
#   size: log(N)
#   sizes: N*log(N)
#   unite: log(N)
#   uniteAUnderB: log(N)
#   build: N
# @memory:
#   layout: none
#   node: par[1*N] sz[1*N]
#   tags: none
#   other: vals[1*N] csum[1*N] cmin[1*N] cmax[1*N] data[1*N] nxt[1*N] tm[1*N]
#   note: K = the size of the group; uniteAUnderB skips union by size, so it can build a chain N deep: every log(N) above (and the N*log(N) of groups) holds only if you never call it, otherwise those calls are O(N) (O(N^2)); data holds one Node per element

_NEVER = 1 << 62  # (the time of a root: it never got a parent)


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


# dsu = DSUNoCompress(vals, baseFn, combine)
# vals: the elements (numbers: componentSum / Min / Max are over them); everything works on their indices 0..n-1, and
# add(val) appends more


class DSUNoCompress:
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
        self.time = 0  # how many unites so far, failed ones too
        self.tm = [_NEVER] * n  # tm[i]: the unite (0, 1, 2, ...) that gave i its parent

    # O(log n), index of the representative of i's component; parents are never rewritten, so the forest records every
    # merge
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def find(self, i):
        par = self.par
        while par[i] != i:
            i = par[i]
        return i

    # O(log n), merges the two components, returns (winner, loser): the new root and the old root now under it, or
    # None if they were already together
    # each call is the next unite in time (0, 1, 2, ...), failed ones too
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def unite(self, i, j):
        t = self.time
        self.time += 1
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
        self.csum[i] += self.csum[j]
        if self.cmin[j] < self.cmin[i]:
            self.cmin[i] = self.cmin[j]
        if self.cmax[j] > self.cmax[i]:
            self.cmax[i] = self.cmax[j]
        self.data[i] = self.combine(self.data[i], self.data[j])
        self.nxt[i], self.nxt[j] = self.nxt[j], self.nxt[i]  # (joins the two circles)
        self.tm[j] = t
        return i, j

    # O(log n), forces a's root under b's root, False if already together
    # skips union by size, so these can build a chain n deep: then this, find, unite and every other call that
    # walks up is O(n); their O(log n) holds only if you never force unions
    # combine gets b's component's Node first here, even when it's the smaller one
    def uniteAUnderB(self, a, b):
        t = self.time
        self.time += 1
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        self.par[a] = b
        self.sz[b] += self.sz[a]
        self.comps -= 1
        if self.sz[b] > self.mx:
            self.mx = self.sz[b]
        self.csum[b] += self.csum[a]
        if self.cmin[a] < self.cmin[b]:
            self.cmin[b] = self.cmin[a]
        if self.cmax[a] > self.cmax[b]:
            self.cmax[b] = self.cmax[a]
        self.data[b] = self.combine(self.data[b], self.data[a])
        self.nxt[b], self.nxt[a] = self.nxt[a], self.nxt[b]  # (joins the two circles)
        self.tm[a] = t
        return True

    # O(log n), True if i and j are in the same component
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def areUnioned(self, i, j):
        return self.find(i) == self.find(j)

    # O(log n), how many elements are in i's component
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
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
    # only O(n log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n^2)
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
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def componentSum(self, i):
        return self.csum[self.find(i)]

    # O(log n), the smallest of the values in i's component
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def componentMin(self, i):
        return self.cmin[self.find(i)]

    # O(log n), the largest of the values in i's component
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def componentMax(self, i):
        return self.cmax[self.find(i)]

    # O(log n), the Node of i's component: every member's baseFn, combined
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def componentData(self, i):
        return self.data[self.find(i)]

    # O(log n), how many unites (failed ones too) it took for i and j to end up together: 0 if i == j, -1 if
    # they still aren't. Climbs from both ends, always moving the one that got its parent first
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def firstConnectedTime(self, i, j):
        if self.find(i) != self.find(j):
            return -1
        par, tm = self.par, self.tm
        last = -1
        while i != j:
            if tm[i] < tm[j]:
                last = max(last, tm[i])
                i = par[i]
            else:
                last = max(last, tm[j])
                j = par[j]
        return last + 1

    # O(log n), were i and j together after the first t unites
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def connectedAt(self, i, j, t):
        f = self.firstConnectedTime(i, j)
        return f != -1 and f <= t

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
        self.tm.append(_NEVER)
        return i
