# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAddArithSeqMod
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeAddArithSeqMod: log(N)
#   build: N
# @memory:
#   layout: none
#   node: c[1*N] s[1*N]
#   tags: none
#   other: none
#   note: two Fenwick trees over differences, everything mod p; a[i] = prefix(c, i) + i * prefix(s, i)

# Range add of an arithmetic sequence mod p, point get. All indices 0-based, ranges inclusive [l, r].
# Values are kept in [0, mod). pointChmax / pointChmin compare those stored residues.
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

    # O(logN) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    def rangeAddArithSeqMod(self, l, r, start, step):
        mod = self.mod
        k = (start - l * step) % mod
        self._add(l, k, step % mod)
        if r + 1 < self.n:
            self._add(r + 1, -k, -step)

    # O(logN) -- a[i] for i in [l, r] += v (mod p)
    def rangeAdd(self, l, r, v):
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

    # O(logN) -- a[i], in [0, mod)
    def pointGet(self, i):
        c, s = self.c, self.s
        k = coef = 0
        j = i + 1
        while j:
            k += c[j]
            coef += s[j]
            j &= j - 1
        return (k + i * coef) % self.mod

    # O(logN) -- a[i] += delta (mod p)
    def pointAdd(self, i, delta):
        self.rangeAdd(i, i, delta)

    # O(logN) -- a[i] = val (mod p)
    def pointAssign(self, i, val):
        self.rangeAdd(i, i, val - self.pointGet(i))

    # O(logN) -- a[i] = max(a[i], val), comparing residues; val should be in [0, mod)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.rangeAdd(i, i, val - cur)

    # O(logN) -- a[i] = min(a[i], val), comparing residues; val should be in [0, mod)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.rangeAdd(i, i, val - cur)
