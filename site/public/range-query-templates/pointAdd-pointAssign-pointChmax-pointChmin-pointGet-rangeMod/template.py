# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeMod
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   rangeMod: log(N)*log(U) amortized
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: mx[2*N]
#   tags: none
#   other: none
#   note: mx[n:] holds the values, mx[1:n] the max of each node's subtree; there are no tags at all

# Range mod + point ops. All indices 0-based, ranges inclusive [l, r]. Requires a[i] >= 0 and mod >= 1.
# Mods don't compose into a single tag, so rangeMod walks down into every covering node whose max is still
# >= mod. Each value that actually changes at least halves, so the total work is amortized
# O((N + Q) logN logU); point writes can raise values again, which only adds logU of potential each.
class RangeModTree:
    __slots__ = ("n", "mx")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        mx = self.mx = [0] * n + list(arr)
        for i in range(n - 1, 0, -1):
            a, b = mx[i << 1], mx[i << 1 | 1]
            mx[i] = a if a > b else b

    # O(logN) -- recompute the maxes on leaf p's path to the root
    def _pull(self, p):
        mx = self.mx
        p >>= 1
        while p:
            a, b = mx[p << 1], mx[p << 1 | 1]
            mx[p] = a if a > b else b
            p >>= 1

    # amortized O(logN logU) -- a[i] %= mod for i in [l, r]
    def rangeMod(self, l, r, mod):
        mx, n = self.mx, self.n
        lo, hi = l + n, r + n + 1
        tops = []
        while lo < hi:
            if lo & 1:
                tops.append(lo)
                lo += 1
            if hi & 1:
                hi -= 1
                tops.append(hi)
            lo >>= 1
            hi >>= 1
        for top in tops:
            if mx[top] < mod:
                continue
            stack = [top]
            inner = []
            while stack:
                y = stack.pop()
                if mx[y] < mod:
                    continue
                if y >= n:
                    mx[y] %= mod
                else:
                    inner.append(y)
                    stack.append(y << 1)
                    stack.append(y << 1 | 1)
            # pre-order reversed puts every child before its parent
            for y in reversed(inner):
                a, b = mx[y << 1], mx[y << 1 | 1]
                mx[y] = a if a > b else b
        self._pull(l + n)
        self._pull(r + n)

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.mx[i + self.n]

    # O(logN) -- a[i] = v
    def pointAssign(self, i, v):
        p = i + self.n
        self.mx[p] = v
        self._pull(p)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        p = i + self.n
        self.mx[p] += delta
        self._pull(p)

    # O(logN) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        p = i + self.n
        if v > self.mx[p]:
            self.mx[p] = v
            self._pull(p)

    # O(logN) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        p = i + self.n
        if v < self.mx[p]:
            self.mx[p] = v
            self._pull(p)
