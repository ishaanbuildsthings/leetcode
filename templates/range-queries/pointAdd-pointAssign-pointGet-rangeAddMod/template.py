# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod/template.py
# @operations: getAll pointAdd pointAssign pointGet rangeAddMod
# @data-structure-type: BIT
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointGet: log(N)
#   rangeAddMod: log(N)
#   build: N
# @memory:
#   layout: none
#   node: tree[1*N]
#   tags: none
#   other: none
#   note: one Fenwick tree over the differences d[i] = a[i] - a[i - 1], % MOD

# Range add (% MOD), point get. All indices 0-based, ranges inclusive [l, r]; values are kept in [0, mod).
class RangeAddBITMod:
    __slots__ = ("n", "tree", "mod")

    # O(N) -- linear Fenwick build over a[i] - a[i - 1]; mod: the modulus p
    def __init__(self, arr, mod=10**9 + 7):
        self.mod = mod
        n = self.n = len(arr)
        tree = self.tree = [0] * (n + 1)
        prev = 0
        for i in range(1, n + 1):
            v = arr[i - 1] % mod
            tree[i] = (tree[i] + v - prev) % mod
            prev = v
            j = i + (i & -i)
            if j <= n:
                tree[j] = (tree[j] + tree[i]) % mod

    def _add(self, i, v):
        tree, n, mod = self.tree, self.n, self.mod
        i += 1
        while i <= n:
            tree[i] = (tree[i] + v) % mod
            i += i & -i

    # O(logN) -- a[i] += v (% MOD) for i in [l, r]
    def rangeAddMod(self, l, r, v):
        v %= self.mod
        self._add(l, v)
        if r + 1 < self.n:
            self._add(r + 1, -v)

    # O(logN) -- a[i], in [0, mod)
    def pointGet(self, i):
        tree = self.tree
        s = 0
        i += 1
        while i:
            s += tree[i]
            i &= i - 1
        return s % self.mod

    # O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    # i + lowbit(i) once complete), then one pass of running prefix sums
    def getAll(self):
        n, mod = self.n, self.mod
        d = self.tree[:]
        for i in range(n, 0, -1):
            j = i + (i & -i)
            if j <= n:
                d[j] -= d[i]
        out, s = [], 0
        for i in range(1, n + 1):
            s += d[i]
            out.append(s % mod)
        return out

    # O(logN) -- a[i] += delta (% MOD)
    def pointAdd(self, i, delta):
        self.rangeAddMod(i, i, delta)

    # O(logN) -- a[i] = val (% MOD)
    def pointAssign(self, i, val):
        self.rangeAddMod(i, i, val - self.pointGet(i))
