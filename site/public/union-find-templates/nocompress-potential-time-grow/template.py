# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/nocompress-potential-time-grow/template.py
# @operations: add areUnioned connectedAt diff elementsInGroup find firstConnectedTime groups largestSize numComponents roots size sizes uniteAUnderBWeighted uniteWeighted
# @data-structure-type: dsu-nocompress
# @complexities:
#   add: 1 amortized
#   areUnioned: log(N)
#   connectedAt: log(N)
#   diff: log(N)
#   elementsInGroup: N*log(N)
#   find: log(N)
#   firstConnectedTime: log(N)
#   groups: N*log(N)
#   largestSize: 1
#   numComponents: 1
#   roots: N
#   size: log(N)
#   sizes: N*log(N)
#   uniteAUnderBWeighted: log(N)
#   uniteWeighted: log(N)
#   build: N
# @memory:
#   layout: none
#   node: par[1*N] sz[1*N]
#   tags: none
#   other: vals[1*N] pot[1*N] tm[1*N]
#   note: uniteAUnderBWeighted skips union by size, so it can build a chain N deep: every log(N) above (and the N*log(N) of groups / elementsInGroup) holds only if you never call it, otherwise those calls are O(N) (O(N^2))

_NEVER = 1 << 62  # (the time of a root: it never got a parent)


# dsu = DSUNoCompress(vals)
# vals: the elements (any values: numbers, strings, tuples, ...); everything works on their indices 0..n-1, and add(val)
# appends more
# potential: every element has a hidden number value[i]; uniteWeighted(i, j, w) says value[j] - value[i] = w and diff(i,
# j)
# reads it back (for parity / two-colouring, swap + and - for ^ throughout)


class DSUNoCompress:
    # O(n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0
        self.pot = [0] * n  # pot[i] = value[i] - value[par[i]] (0 at a root)
        self.time = 0  # how many unites so far, failed ones too
        self.tm = [_NEVER] * n  # tm[i]: the unite (0, 1, 2, ...) that gave i its parent

    # O(log n), index of the representative of i's component; parents are never rewritten, so the forest records every
    # merge
    # only O(log n) if you never call uniteAUnderBWeighted: forced unions can build a chain, then this is O(n)
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

    # O(log n), merges the two components, returns (winner, loser): the new root and the old root now under it, or
    # None if they were already together
    # w: value[j] - value[i] = w. Already together: nothing changes (diff(i, j) == w says if this agrees)
    # each call is the next unite in time (0, 1, 2, ...), failed ones too
    # only O(log n) if you never call uniteAUnderBWeighted: forced unions can build a chain, then this is O(n)
    def uniteWeighted(self, i, j, w):
        t = self.time
        self.time += 1
        i, wi = self._rootAndWeight(i)
        j, wj = self._rootAndWeight(j)
        if i == j:
            return None
        w += wi - wj  # now value[j's root] - value[i's root]
        if self.sz[i] < self.sz[j]:
            i, j = j, i
            w = -w
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        if self.sz[i] > self.mx:
            self.mx = self.sz[i]
        self.pot[j] = w
        self.tm[j] = t
        return i, j

    # O(log n), forces a's root under b's root, False if already together
    # skips union by size, so these can build a chain n deep: then this, find, unite and every other call that
    # walks up is O(n); their O(log n) holds only if you never force unions
    # w: value[b] - value[a] = w
    def uniteAUnderBWeighted(self, a, b, w):
        t = self.time
        self.time += 1
        a, wa = self._rootAndWeight(a)
        b, wb = self._rootAndWeight(b)
        if a == b:
            return False
        w = wb - wa - w  # now value[a's root] - value[b's root]
        self.par[a] = b
        self.sz[b] += self.sz[a]
        self.comps -= 1
        if self.sz[b] > self.mx:
            self.mx = self.sz[b]
        self.pot[a] = w
        self.tm[a] = t
        return True

    # O(log n), True if i and j are in the same component
    # only O(log n) if you never call uniteAUnderBWeighted: forced unions can build a chain, then this is O(n)
    def areUnioned(self, i, j):
        return self.find(i) == self.find(j)

    # O(log n), how many elements are in i's component
    # only O(log n) if you never call uniteAUnderBWeighted: forced unions can build a chain, then this is O(n)
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
    # only O(n log n) if you never call uniteAUnderBWeighted: forced unions can build a chain, then this is O(n^2)
    def groups(self):
        n = len(self.par)
        groupsArr = [[] for _ in range(n)]
        for i in range(n):
            groupsArr[self.find(i)].append(self.vals[i])
        return groupsArr

    # O(n log n), the values of every element sitting in the same group as index i
    # only O(n log n) if you never call uniteAUnderBWeighted: forced unions can build a chain, then this is O(n^2)
    def elementsInGroup(self, i):
        rt = self.find(i)
        return [self.vals[j] for j in range(len(self.par)) if self.find(j) == rt]

    # O(log n), value[j] - value[i] from the unites so far, None if i and j aren't together
    # only O(log n) if you never call uniteAUnderBWeighted: forced unions can build a chain, then this is O(n)
    def diff(self, i, j):
        ri, wi = self._rootAndWeight(i)
        rj, wj = self._rootAndWeight(j)
        return wj - wi if ri == rj else None

    # O(log n), how many unites (failed ones too) it took for i and j to end up together: 0 if i == j, -1 if
    # they still aren't. Climbs from both ends, always moving the one that got its parent first
    # only O(log n) if you never call uniteAUnderBWeighted: forced unions can build a chain, then this is O(n)
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
    # only O(log n) if you never call uniteAUnderBWeighted: forced unions can build a chain, then this is O(n)
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
        self.pot.append(0)
        self.tm.append(_NEVER)
        return i
