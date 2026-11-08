# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rightmostIndexOf-rightmostIndexOfInRange/template.py
# @operations: countOccurrences getAll leftmostIndexOf leftmostIndexOfInRange pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rightmostIndexOf rightmostIndexOfInRange
# @data-structure-type: sqrt
# @complexities:
#   countOccurrences: sqrt(N)
#   getAll: N
#   leftmostIndexOf: sqrt(N)
#   leftmostIndexOfInRange: sqrt(N)
#   pointAdd: sqrt(N)
#   pointAssign: sqrt(N)
#   pointChmax: sqrt(N)
#   pointChmin: sqrt(N)
#   pointGet: 1
#   rangeAdd: sqrt(N)
#   rangeAssign: sqrt(N)
#   rightmostIndexOf: sqrt(N)
#   rightmostIndexOfInRange: sqrt(N)
#   build: N
# @memory:
#   layout: none
#   node: vals[1*N] cnt[1*N]
#   tags: add[1*sqrt(N)] asg[1*sqrt(N)]
#   other: none
#   note: sqrt(N) blocks; cnt[b] counts the block's stored values, and the block tag (assign, then add) is applied on read

from math import isqrt
from random import getrandbits

# "How many times does x appear in a[l..r]?" and "where is x's first / last copy (in a[l..r])?", with range add, range
# assign and point updates. 0-based, inclusive.
# Sqrt decomposition: each block keeps its stored values, a value -> count table of them, and one pending tag
# "value = (asg if assigned else stored) + add". A whole block answers a count from its table in O(1): look up
# x - add (or compare x to asg + add when the block is assigned). A partial block bakes its tag in, edits the few
# slots it covers, and patches its table one slot at a time. A first / last search skips every block whose table
# lacks x and scans only the first block that has it.


class SqrtOccurrences:
    __slots__ = ("n", "B", "vals", "cnt", "add", "asg", "salt")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        B = self.B = max(1, isqrt(n))
        nb = (n + B - 1) // B
        self.vals = list(arr)
        self.cnt = [{} for _ in range(nb)]
        salt = self.salt = getrandbits(62)  # cnt's keys are values salted with this, so no fixed input can make them collide
        for i, v in enumerate(arr):
            c = self.cnt[i // B]
            v ^= salt
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
            self.cnt[b] = {v ^ self.salt: hi - lo + 1}
        else:
            for i in range(lo, hi + 1):
                vals[i] += add
            salt = self.salt
            self.cnt[b] = {((k ^ salt) + add) ^ salt: c for k, c in self.cnt[b].items()}
        self.add[b] = 0
        self.asg[b] = None

    # O(1) -- a[i] = v inside an untagged block, keeping its table in sync
    def _set(self, b, i, v):
        c, salt = self.cnt[b], self.salt
        old = self.vals[i] ^ salt
        if c[old] == 1:
            del c[old]
        else:
            c[old] -= 1
        self.vals[i] = v
        v ^= salt
        c[v] = c.get(v, 0) + 1

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

    # O(sqrt N) -- a[i] += x for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return

        def tag(b):
            self.add[b] += x
        self._apply(l, r, tag, lambda v: v + x)

    # O(sqrt N) -- a[i] = x for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return

        def tag(b):
            self.asg[b] = x
            self.add[b] = 0
        self._apply(l, r, tag, lambda v: x)

    # O(sqrt N) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return 0
        B, res, salt = self.B, 0, self.salt
        for b in range(l // B, r // B + 1):
            lo, hi = self._range(b)
            add, asg = self.add[b], self.asg[b]
            if l <= lo and hi <= r:
                if asg is not None:
                    res += hi - lo + 1 if asg + add == x else 0
                else:
                    res += self.cnt[b].get((x - add) ^ salt, 0)
            else:
                vals = self.vals
                for i in range(max(l, lo), min(r, hi) + 1):
                    if (asg if asg is not None else vals[i]) + add == x:
                        res += 1
        return res

    # O(sqrt N) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        return self._search(0, self.n - 1, x, False)

    # O(sqrt N) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        return self._search(0, self.n - 1, x, True)

    # O(sqrt N) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < n, else
    # IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._search(l, r, x, False)

    # O(sqrt N) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < n, else
    # IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._search(l, r, x, True)

    # the first (rev: last) i in [l, r] with a[i] == x, or -1
    def _search(self, l, r, x, rev):
        if l > r:
            return -1
        B, vals, salt = self.B, self.vals, self.salt
        blocks = range(l // B, r // B + 1)
        for b in reversed(blocks) if rev else blocks:
            lo, hi = self._range(b)
            lo, hi = max(l, lo), min(r, hi)
            add, asg = self.add[b], self.asg[b]
            if asg is not None:
                if asg + add == x:
                    return hi if rev else lo
                continue
            want = x - add
            if want ^ salt not in self.cnt[b]:  # (a partial block too: x isn't anywhere in it)
                continue
            for i in range(hi, lo - 1, -1) if rev else range(lo, hi + 1):
                if vals[i] == want:
                    return i
        return -1

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        b = i // self.B
        asg = self.asg[b]
        return (asg if asg is not None else self.vals[i]) + self.add[b]

    # O(N) -- the whole array (each a[i] is O(1))
    def getAll(self):
        return [self.pointGet(i) for i in range(self.n)]

    # O(sqrt N) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        b = i // self.B
        self._push(b)
        self._set(b, i, val)

    # O(sqrt N) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(sqrt N) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(sqrt N) -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)
