# @operations: countOccurrences pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign
# @data-structure-type: sqrt
# @complexities:
#   countOccurrences: sqrt(N)
#   pointAdd: sqrt(N)
#   pointAssign: sqrt(N)
#   pointChmax: sqrt(N)
#   pointChmin: sqrt(N)
#   pointGet: 1
#   rangeAdd: sqrt(N)
#   rangeAssign: sqrt(N)
#   build: N
# @memory:
#   layout: none
#   node: vals[1*N] cnt[1*N]
#   tags: add[1*sqrt(N)] asg[1*sqrt(N)]
#   other: none
#   note: sqrt(N) blocks; cnt[b] counts the block's stored values, and the block tag (assign, then add) is applied on read

from math import isqrt

# "How many times does x appear in a[l..r]?" with range add, range assign and point updates. 0-based, inclusive.
# Sqrt decomposition: each block keeps its stored values, a value -> count table of them, and one pending tag
# "value = (asg if assigned else stored) + add". A whole block answers a count from its table in O(1): look up
# x - add (or compare x to asg + add when the block is assigned). A partial block bakes its tag in, edits the few
# slots it covers, and patches its table one slot at a time.


class SqrtOccurrences:
    __slots__ = ("n", "B", "vals", "cnt", "add", "asg")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        B = self.B = max(1, isqrt(n))
        nb = (n + B - 1) // B
        self.vals = list(arr)
        self.cnt = [{} for _ in range(nb)]
        for i, v in enumerate(arr):
            c = self.cnt[i // B]
            c[v] = c.get(v, 0) + 1
        self.add = [0] * nb
        self.asg = [None] * nb  # None = not assigned

    def _range(self, b):
        return b * self.B, min(self.n, (b + 1) * self.B) - 1

    # O(sqrt N) -- bake block b's tag into its stored values and clear it
    def _push(self, b):
        add, asg = self.add[b], self.asg[b]
        if not add and asg is None:
            return
        lo, hi = self._range(b)
        vals = self.vals
        if asg is not None:
            v = asg + add
            for i in range(lo, hi + 1):
                vals[i] = v
            self.cnt[b] = {v: hi - lo + 1}
        else:
            for i in range(lo, hi + 1):
                vals[i] += add
            self.cnt[b] = {k + add: c for k, c in self.cnt[b].items()}
        self.add[b] = 0
        self.asg[b] = None

    # O(1) -- a[i] = v inside an untagged block, keeping its table in sync
    def _set(self, b, i, v):
        c = self.cnt[b]
        old = self.vals[i]
        if c[old] == 1:
            del c[old]
        else:
            c[old] -= 1
        c[v] = c.get(v, 0) + 1
        self.vals[i] = v

    # whole blocks get a tag; the partial ends are pushed and edited slot by slot
    def _apply(self, l, r, tag, edit):
        B = self.B
        for b in range(l // B, r // B + 1):
            lo, hi = self._range(b)
            if l <= lo and hi <= r:
                tag(b)
            else:
                self._push(b)
                for i in range(max(l, lo), min(r, hi) + 1):
                    self._set(b, i, edit(self.vals[i]))

    # O(sqrt N) -- a[i] += x for i in [l, r]
    def rangeAdd(self, l, r, x):
        if l > r:
            return

        def tag(b):
            self.add[b] += x
        self._apply(l, r, tag, lambda v: v + x)

    # O(sqrt N) -- a[i] = x for i in [l, r]
    def rangeAssign(self, l, r, x):
        if l > r:
            return

        def tag(b):
            self.asg[b] = x
            self.add[b] = 0
        self._apply(l, r, tag, lambda v: x)

    # O(sqrt N) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        if l > r:
            return 0
        B, res = self.B, 0
        for b in range(l // B, r // B + 1):
            lo, hi = self._range(b)
            add, asg = self.add[b], self.asg[b]
            if l <= lo and hi <= r:
                if asg is not None:
                    res += hi - lo + 1 if asg + add == x else 0
                else:
                    res += self.cnt[b].get(x - add, 0)
            else:
                vals = self.vals
                for i in range(max(l, lo), min(r, hi) + 1):
                    if (asg if asg is not None else vals[i]) + add == x:
                        res += 1
        return res

    # O(1) -- a[i]
    def pointGet(self, i):
        b = i // self.B
        asg = self.asg[b]
        return (asg if asg is not None else self.vals[i]) + self.add[b]

    # O(sqrt N) -- a[i] = val
    def pointAssign(self, i, val):
        b = i // self.B
        self._push(b)
        self._set(b, i, val)

    # O(sqrt N) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(sqrt N) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(sqrt N) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
