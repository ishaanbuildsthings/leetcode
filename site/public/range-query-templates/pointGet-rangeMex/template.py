# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeMex/template.py
# @operations: pointGet rangeMex
# @data-structure-type: persistent
# @complexities:
#   pointGet: 1
#   rangeMex: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)]
#   tags: none
#   other: root[1*N] arr[1*N]
#   note: persistent seg tree over the values 0..N+1; version p holds each value's last index before p, and the mex of a[l..r] is the first value whose last index is < l

# Static array; rangeMex(l, r) = smallest integer >= 0 not in a[l..r] (0-indexed, inclusive), online.
# rangeMex: a persistent seg tree over the values 0..N+1; version p holds, per value, its last index before p (-1 if
# none). The mex of a[l..r] is the first value whose last index in version r + 1 is < l.


class PersistentMex:
    __slots__ = ("arr", "n", "root", "ML", "MR", "MN")

    # O(N log N) -- arr: the initial array (a list), 0-indexed
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        self._buildMex()

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]

    # O(logN) -- smallest integer >= 0 that is not in a[l..r]
    def rangeMex(self, l, r):
        return self._mexFrom(l, r, 0)

    # persistent seg tree over the values 0..n+1: version p holds, per value, its last index before p (-1: none)
    def _buildMex(self):
        n = self.n
        self.ML, self.MR, self.MN = [0], [0], [-1]  # node 0 = the empty tree (every last index -1)
        self.root = root = [0] * (n + 1)
        for i, v in enumerate(self.arr):
            root[i + 1] = self._mexSet(root[i], v, i) if 0 <= v <= n + 1 else root[i]

    # O(logN) -- copy of node with value v's last index set to i
    def _mexSet(self, node, v, i):
        ML, MR, MN = self.ML, self.MR, self.MN
        path = []
        nl, nh = 0, self.n + 1
        while nl != nh:
            mid = (nl + nh) >> 1
            if v <= mid:
                path.append((node, True))
                node, nh = ML[node], mid
            else:
                path.append((node, False))
                node, nl = MR[node], mid + 1
        cur = len(MN)
        ML.append(0), MR.append(0), MN.append(i)
        for old, left in reversed(path):
            lc, rc = (cur, MR[old]) if left else (ML[old], cur)
            cur = len(MN)
            ML.append(lc), MR.append(rc), MN.append(min(MN[lc], MN[rc]))
        return cur

    # O(logN) -- smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    def _mexFrom(self, l, r, s):
        ML, MR, MN = self.ML, self.MR, self.MN
        stack = [(self.root[r + 1], 0, self.n + 1)]
        while stack:
            t, nl, nh = stack.pop()
            if nh < s or MN[t] >= l:  # nothing allowed here, or every value here is in a[l..r]
                continue
            if not t:  # no value here was ever seen
                return max(nl, s)
            if nl == nh:
                return nl
            mid = (nl + nh) >> 1
            stack.append((MR[t], mid + 1, nh))
            stack.append((ML[t], nl, mid))
        return self.n + 2  # (unreachable: the n + 2 values 0..n+1 can't all be in a[l..r])
