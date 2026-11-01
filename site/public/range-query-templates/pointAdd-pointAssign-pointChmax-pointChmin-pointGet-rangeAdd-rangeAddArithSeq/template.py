# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAddArithSeq/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAddArithSeq
# @data-structure-type: BIT
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAdd: log(N)
#   rangeAddArithSeq: log(N)
#   build: N
# @memory:
#   layout: none
#   node: c[1*N] s[1*N]
#   tags: none
#   other: none
#   note: two Fenwick trees over differences; a[i] = prefix(c, i) + i * prefix(s, i)

# Range add of an arithmetic sequence, point get. All indices 0-based, ranges inclusive [l, r].
# rangeAddArithSeq(l, r, start, step) adds start + (i - l) * step to a[i], which is the line
# (start - l * step) + i * step, so it is one difference update on c and one on s.
class ArithSeqBIT:
    __slots__ = ("n", "c", "s")

    # O(N) -- c is a linear Fenwick build over a[i] - a[i - 1]; s starts empty
    def __init__(self, arr):
        n = self.n = len(arr)
        c = self.c = [0] * (n + 1)
        self.s = [0] * (n + 1)
        prev = 0
        for i in range(1, n + 1):
            v = arr[i - 1]
            c[i] += v - prev
            prev = v
            j = i + (i & -i)
            if j <= n:
                c[j] += c[i]

    def _add(self, i, k, step):
        c, s, n = self.c, self.s, self.n
        i += 1
        while i <= n:
            c[i] += k
            s[i] += step
            i += i & -i

    # O(logN) -- a[l + j] += start + j * step for j in [0, r - l]
    def rangeAddArithSeq(self, l, r, start, step):
        k = start - l * step
        self._add(l, k, step)
        if r + 1 < self.n:
            self._add(r + 1, -k, -step)

    # O(logN) -- a[i] for i in [l, r] += v
    def rangeAdd(self, l, r, v):
        c, n = self.c, self.n
        i = l + 1
        while i <= n:
            c[i] += v
            i += i & -i
        i = r + 2
        while i <= n:
            c[i] -= v
            i += i & -i

    # O(logN) -- a[i]
    def pointGet(self, i):
        c, s = self.c, self.s
        k = coef = 0
        j = i + 1
        while j:
            k += c[j]
            coef += s[j]
            j &= j - 1
        return k + i * coef

    # O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    # i + lowbit(i) once complete), then one pass of running prefix sums
    def getAll(self):
        n = self.n
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
            out.append(k + i * coef)
        return out

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAdd(i, i, delta)

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAdd(i, i, val - self.pointGet(i))

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.rangeAdd(i, i, val - cur)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.rangeAdd(i, i, val - cur)
