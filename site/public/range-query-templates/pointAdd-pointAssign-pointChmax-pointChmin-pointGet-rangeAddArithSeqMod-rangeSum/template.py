# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAddArithSeqMod rangeSum
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAddArithSeqMod: log(N)
#   rangeSum: log(N)
#   build: N
# @memory:
#   layout: pow2-iterative
#   node: sum[4*N] length[4*N] sumIdx[4*N]
#   tags: lazyConst[4*N] lazyIdx[4*N]
#   other: none
#   note: each tag is a pending line const + idx*i (mod p); arrays are 2*size, size the next power of two >= n
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/lazy/ArithmeticProgressionSTWithMod.py

class APSegTreeMod:
    """
    Iterative segment tree: range arithmetic-progression add, range sum, all mod MOD.

    Lazy tag: (constPart, idxPart) means "add constPart + idxPart * i to every
    underlying position i". Tags compose by addition, so no pushdown-before-
    compose dance is needed.

    Per-node metadata (length, sumIdx) is precomputed at construction to
    avoid any range arithmetic in the hot path.

    start and step may be negative; they get reduced into [0, MOD).

    Public operations:
      APSegTreeMod(n) or APSegTreeMod(list)   O(n)
      rangeAddArithSeqMod(l, r, start, step)           O(log n)
      rangeSum(l, r)                          O(log n)
      pointGet(i)                           O(log n)
      pushAllDown()                           O(n)  -- call before batch leafValue reads
      leafValue(i)                            O(1)  -- only valid after pushAllDown
    """

    def __init__(self, data, mod=10**9 + 7):
        self.MOD = mod

        if isinstance(data, int):
            self.n = data
            initial = None
        else:
            self.n = len(data)
            initial = data

        self.size = 1
        while self.size < max(self.n, 1):
            self.size *= 2
        self.H = self.size.bit_length() - 1

        doubleSize = 2 * self.size
        self.sum = [0] * doubleSize
        self.lazyConst = [0] * doubleSize
        self.lazyIdx = [0] * doubleSize
        self.length = [0] * doubleSize
        self.sumIdx = [0] * doubleSize

        for i in range(self.size):
            self.length[self.size + i] = 1
            self.sumIdx[self.size + i] = i % mod
        for node in range(self.size - 1, 0, -1):
            self.length[node] = (self.length[2 * node] + self.length[2 * node + 1]) % mod
            self.sumIdx[node] = (self.sumIdx[2 * node] + self.sumIdx[2 * node + 1]) % mod

        if initial is not None:
            for i in range(self.n):
                self.sum[self.size + i] = initial[i] % mod
            for i in range(self.size - 1, 0, -1):
                self.sum[i] = (self.sum[2 * i] + self.sum[2 * i + 1]) % mod

    def _applyNode(self, node, constPart, idxPart):
        mod = self.MOD
        self.sum[node] = (self.sum[node] + constPart * self.length[node] + idxPart * self.sumIdx[node]) % mod
        self.lazyConst[node] = (self.lazyConst[node] + constPart) % mod
        self.lazyIdx[node] = (self.lazyIdx[node] + idxPart) % mod

    def _pushDown(self, node):
        c = self.lazyConst[node]
        d = self.lazyIdx[node]
        if c or d:
            self._applyNode(2 * node, c, d)
            self._applyNode(2 * node + 1, c, d)
            self.lazyConst[node] = 0
            self.lazyIdx[node] = 0

    def _pushToRoot(self, i):
        for s in range(self.H, 0, -1):
            self._pushDown(i >> s)

    def _recomputeToRoot(self, i):
        mod = self.MOD
        i >>= 1
        while i > 0:
            c = self.lazyConst[i]
            d = self.lazyIdx[i]
            baseSum = self.sum[2 * i] + self.sum[2 * i + 1]
            self.sum[i] = (baseSum + c * self.length[i] + d * self.sumIdx[i]) % mod
            i >>= 1

    def rangeAddArithSeqMod(self, l, r, start, step):
        if l > r:
            return
        mod = self.MOD
        constPart = (start - step * l) % mod
        idxPart = step % mod
        l0 = l + self.size
        r0 = r + self.size
        self._pushToRoot(l0)
        self._pushToRoot(r0)
        lIdx = l0
        rIdx = r0 + 1
        while lIdx < rIdx:
            if lIdx & 1:
                self._applyNode(lIdx, constPart, idxPart)
                lIdx += 1
            if rIdx & 1:
                rIdx -= 1
                self._applyNode(rIdx, constPart, idxPart)
            lIdx >>= 1
            rIdx >>= 1
        self._recomputeToRoot(l0)
        self._recomputeToRoot(r0)

    def rangeSum(self, l, r):
        if l > r:
            return 0
        l0 = l + self.size
        r0 = r + self.size
        self._pushToRoot(l0)
        self._pushToRoot(r0)
        result = 0
        lIdx = l0
        rIdx = r0 + 1
        while lIdx < rIdx:
            if lIdx & 1:
                result += self.sum[lIdx]
                lIdx += 1
            if rIdx & 1:
                rIdx -= 1
                result += self.sum[rIdx]
            lIdx >>= 1
            rIdx >>= 1
        return result % self.MOD

    def pointGet(self, i):
        return self.rangeSum(i, i)

    def pushAllDown(self):
        for node in range(1, self.size):
            c = self.lazyConst[node]
            d = self.lazyIdx[node]
            if c or d:
                self._applyNode(2 * node, c, d)
                self._applyNode(2 * node + 1, c, d)
                self.lazyConst[node] = 0
                self.lazyIdx[node] = 0

    def leafValue(self, i):
        return self.sum[i + self.size]

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAddArithSeqMod(i, i, delta, 0)

    # a[i] = val
    def pointAssign(self, i, val):
        self.rangeAddArithSeqMod(i, i, val - self.pointGet(i), 0)

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.rangeAddArithSeqMod(i, i, val - cur, 0)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.rangeAddArithSeqMod(i, i, val - cur, 0)