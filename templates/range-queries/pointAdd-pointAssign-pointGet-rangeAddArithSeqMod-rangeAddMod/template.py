# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddArithSeqMod-rangeAddMod/template.py
# @operations: getAll pointAdd pointAssign pointGet rangeAddArithSeqMod rangeAddMod
# @data-structure-type: BIT
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointGet: log(N)
#   rangeAddArithSeqMod: log(N)
#   rangeAddMod: log(N)
#   build: N
# @memory:
#   layout: none
#   node: c[1*N] s[1*N]
#   tags: none
#   other: none
#   note: two Fenwick trees over differences, everything % MOD; a[i] = prefix(c, i) + i * prefix(s, i)

# Range add of an arithmetic sequence % MOD, point get. All indices 0-based, ranges inclusive [l, r].
# Values are kept in [0, mod).
class ArithSeqBITMod:
    __slots__ = ("n", "c", "s", "mod")

    # O(N)
    def __init__(self, arr, mod=10**9 + 7):
        self.mod = mod
        n = self.n = len(arr)
        c = self.c = [0] * (n + 1)
        self.s = [0] * (n + 1)
        prev = 0
        for i in range(1, n + 1):
            v = arr[i - 1] % mod
            c[i] = (c[i] + v - prev) % mod
            prev = v
            j = i + (i & -i)
            if j <= n:
                c[j] = (c[j] + c[i]) % mod

    def _add(self, i, k, step):
        c, s, n, mod = self.c, self.s, self.n, self.mod
        i += 1
        while i <= n:
            c[i] = (c[i] + k) % mod
            s[i] = (s[i] + step) % mod
            i += i & -i

    # O(logN) -- a[l + j] += start + j * step (% MOD) for j in [0, r - l]; needs 0 <= l <= r < n, else IndexError
    def rangeAddArithSeqMod(self, l, r, start, step):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAddArithSeqMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        mod = self.mod
        k = (start - l * step) % mod
        self._add(l, k, step % mod)
        if r + 1 < self.n:
            self._add(r + 1, -k, -step)

    # O(logN) -- a[i] for i in [l, r] += v (% MOD); needs 0 <= l <= r < n, else IndexError
    def rangeAddMod(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAddMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c, n, mod = self.c, self.n, self.mod
        v %= mod
        i = l + 1
        while i <= n:
            c[i] = (c[i] + v) % mod
            i += i & -i
        i = r + 2
        while i <= n:
            c[i] = (c[i] - v) % mod
            i += i & -i

    # O(logN) -- a[i], in [0, mod); needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        c, s = self.c, self.s
        k = coef = 0
        j = i + 1
        while j:
            k += c[j]
            coef += s[j]
            j &= j - 1
        return (k + i * coef) % self.mod

    # O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    # i + lowbit(i) once complete), then one pass of running prefix sums
    def getAll(self):
        n, mod = self.n, self.mod
        c, s = self.c[:], self.s[:]
        for i in range(n, 0, -1):
            j = i + (i & -i)
            if j <= n:
                c[j] -= c[i]
                s[j] -= s[i]
        out = []
        k = coef = 0
        for i in range(n):
            k += c[i + 1]
            coef += s[i + 1]
            out.append((k + i * coef) % mod)
        return out

    # O(logN) -- a[i] += delta (% MOD); needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAddMod(i, i, delta)

    # O(logN) -- a[i] = val (% MOD); needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.rangeAddMod(i, i, val - self.pointGet(i))
