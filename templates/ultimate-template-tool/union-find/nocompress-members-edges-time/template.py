# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/nocompress-members-edges-time/template.py
# @operations: areUnioned connectedAt edgeCount elementsInGroup find firstConnectedTime groups isTree largestSize numComponents roots size sizes unite uniteAUnderB
# @data-structure-type: dsu-nocompress
# @complexities:
#   areUnioned: log(N)
#   connectedAt: log(N)
#   edgeCount: log(N)
#   elementsInGroup: K
#   find: log(N)
#   firstConnectedTime: log(N)
#   groups: N*log(N)
#   isTree: log(N)
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
#   other: vals[1*N] nxt[1*N] edges[1*N] tm[1*N]
#   note: K = the size of the group; uniteAUnderB skips union by size, so it can build a chain N deep: every log(N) above (and the N*log(N) of groups) holds only if you never call it, otherwise those calls are O(N) (O(N^2))

_NEVER = 1 << 62  # (the time of a root: it never got a parent)


# dsu = DSUNoCompress(vals)
# vals: the elements (any values: numbers, strings, tuples, ...); everything works on their indices 0..n-1


class DSUNoCompress:
    # O(n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0
        self.nxt = list(range(n))  # each component's members linked in a circle: i -> nxt[i] -> ... -> i
        self.edges = [0] * n  # edges[root]: how many unites touched root's component, merging or not
        self.time = 0  # how many unites so far, failed ones too
        self.tm = [_NEVER] * n  # tm[i]: the unite (0, 1, 2, ...) that gave i its parent

    # O(log n), index of the representative of i's component; parents are never rewritten, so the forest records every
    # merge only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def find(self, i):
        par = self.par
        while par[i] != i:
            i = par[i]
        return i

    # O(log n), merges the two components, returns (winner, loser): the new root and the old root now under it, or
    # None if they were already together either way it counts as an edge of the component (edgeCount) each call is the
    # next unite in time (0, 1, 2, ...), failed ones too only O(log n) if you never call uniteAUnderB: forced unions can
    # build a chain, then this is O(n)
    def unite(self, i, j):
        t = self.time
        self.time += 1
        i, j = self.find(i), self.find(j)
        if i == j:
            self.edges[i] += 1
            return None
        if self.sz[i] < self.sz[j]:
            i, j = j, i
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        if self.sz[i] > self.mx:
            self.mx = self.sz[i]
        self.nxt[i], self.nxt[j] = self.nxt[j], self.nxt[i]  # (joins the two circles)
        self.edges[i] += self.edges[j] + 1
        self.tm[j] = t
        return i, j

    # O(log n), forces a's root under b's root, False if already together
    # skips union by size, so these can build a chain n deep: then this, find, unite and every other call that walks up
    # is O(n); their O(log n) holds only if you never force unions
    def uniteAUnderB(self, a, b):
        t = self.time
        self.time += 1
        a, b = self.find(a), self.find(b)
        if a == b:
            self.edges[a] += 1
            return False
        self.par[a] = b
        self.sz[b] += self.sz[a]
        self.comps -= 1
        if self.sz[b] > self.mx:
            self.mx = self.sz[b]
        self.nxt[b], self.nxt[a] = self.nxt[a], self.nxt[b]  # (joins the two circles)
        self.edges[b] += self.edges[a] + 1
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

    # O(log n), how many unites have touched i's component (merging or not): its edges, if each unite is an edge
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def edgeCount(self, i):
        return self.edges[self.find(i)]

    # O(log n), True if i's component has no cycle: exactly size - 1 edges
    # only O(log n) if you never call uniteAUnderB: forced unions can build a chain, then this is O(n)
    def isTree(self, i):
        r = self.find(i)
        return self.edges[r] == self.sz[r] - 1

    # O(log n), how many unites (failed ones too) it took for i and j to end up together: 0 if i == j, -1 if
    # they still aren't. Climbs from both ends, always moving the one that got its parent first only O(log n) if you
    # never call uniteAUnderB: forced unions can build a chain, then this is O(n)
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
