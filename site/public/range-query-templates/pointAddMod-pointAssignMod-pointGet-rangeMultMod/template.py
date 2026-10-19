# @operations: pointAddMod pointAssignMod pointGet rangeMultMod
# @data-structure-type: seg-tree
# @complexities:
#   pointAddMod: log(N)
#   pointAssignMod: log(N)
#   pointGet: log(N)
#   rangeMultMod: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: tree[1*N]
#   tags: tree[1*N]
#   other: none
#   note: tree[n:] holds the values, tree[1:n] holds each node's pending rangeMultMod tag (no aggregates); leaves count as node data, internal nodes as tags

# rangeMultMod + point ops with no range aggregates. All indices 0-based, ranges inclusive [l, r].
# rangeMultMod composes with itself in any order, so a range update only tags the O(logN) covering nodes and
# pointGet folds the tags on the leaf-to-root path. Only pointAssignMod-style overwrites need to push those
# tags off the path first, because they must not be re-applied to the new value.
class RangeMultModTree:
    __slots__ = ("n", "tree", "mod")

    # O(N)
    def __init__(self, arr, mod=10**9 + 7):
        self.mod = mod
        n = self.n = len(arr)
        self.tree = [1] * n + [v % mod for v in arr]

    # O(logN) -- a[i] = a[i] * m (mod p) for i in [l, r]
    def rangeMultMod(self, l, r, m):
        tree, mod = self.tree, self.mod
        m %= mod
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                tree[l] = tree[l] * m % mod
                l += 1
            if r & 1:
                r -= 1
                tree[r] = tree[r] * m % mod
            l >>= 1
            r >>= 1

    # O(logN) -- move the tags on i's root-to-leaf path down, so nothing above i is pending
    def _push(self, p):
        tree, mod = self.tree, self.mod
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            t = tree[x]
            if t != 1:
                y = x << 1
                tree[y] = tree[y] * t % mod
                tree[y | 1] = tree[y | 1] * t % mod
                tree[x] = 1

    # O(logN) -- a[i], in [0, mod)
    def pointGet(self, i):
        tree, mod = self.tree, self.mod
        p = i + self.n
        a = tree[p]
        p >>= 1
        while p:
            t = tree[p]
            a = a * t % mod
            p >>= 1
        return a

    # O(logN) -- a[i] = val
    def pointAssignMod(self, i, val):
        p = i + self.n
        self._push(p)
        self.tree[p] = val % self.mod

    # O(logN) -- a[i] += delta
    def pointAddMod(self, i, delta):
        p = i + self.n
        self._push(p)
        self.tree[p] = (self.tree[p] + delta) % self.mod
