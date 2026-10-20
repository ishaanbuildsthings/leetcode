# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeOrApply-rangeXorApply/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeOrApply rangeXorApply
# @data-structure-type: lazy-seg-tree
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeAndApply: log(N)
#   rangeOrApply: log(N)
#   rangeXorApply: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: val[1*N]
#   tags: AND[1*N] XOR[1*N]
#   other: none
#   note: each internal node holds one pending bit map x -> (x & AND) ^ XOR; val holds the leaf values

# Range and / or / xor + point ops, no range aggregates. All indices 0-based, ranges inclusive [l, r].
# Every update is a bit map (a, x): v -> (v & a) ^ x, and they compose into one:
#   and v -> (v, 0)    or v -> (~v, v)    xor v -> (-1, v)
# They don't commute (and then xor != xor then and), so the paths to l and r are pushed before tagging.
# Works for negative Python ints too (infinite two's complement).
class BitOpTree:
    __slots__ = ("n", "AND", "XOR", "val")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.AND = [-1] * n
        self.XOR = [0] * n
        self.val = list(arr)

    # apply (a, x) on top of whatever node y already holds
    def _apply(self, y, a, x):
        n = self.n
        if y >= n:
            val = self.val
            val[y - n] = (val[y - n] & a) ^ x
        else:
            AND, XOR = self.AND, self.XOR
            AND[y] &= a
            XOR[y] = (XOR[y] & a) ^ x

    # O(logN) -- push every pending map on leaf p's root-to-leaf path down to its children
    def _push(self, p):
        AND, XOR = self.AND, self.XOR
        apply = self._apply
        for h in range(p.bit_length() - 1, 0, -1):
            y = p >> h
            a, x = AND[y], XOR[y]
            if a != -1 or x:
                c = y << 1
                apply(c, a, x)
                apply(c | 1, a, x)
                AND[y] = -1
                XOR[y] = 0

    def _update(self, l, r, a, x):
        n = self.n
        l += n
        r += n
        self._push(l)
        self._push(r)
        r += 1
        apply = self._apply
        while l < r:
            if l & 1:
                apply(l, a, x)
                l += 1
            if r & 1:
                r -= 1
                apply(r, a, x)
            l >>= 1
            r >>= 1

    # O(logN) -- a[i] &= v for i in [l, r]
    def rangeAndApply(self, l, r, v):
        self._update(l, r, v, 0)

    # O(logN) -- a[i] |= v for i in [l, r]
    def rangeOrApply(self, l, r, v):
        self._update(l, r, ~v, v)

    # O(logN) -- a[i] ^= v for i in [l, r]
    def rangeXorApply(self, l, r, v):
        self._update(l, r, -1, v)

    # O(logN) -- a[i]: apply ancestors' maps bottom-up (deeper tags are older)
    def pointGet(self, i):
        AND, XOR = self.AND, self.XOR
        v = self.val[i]
        p = (i + self.n) >> 1
        while p:
            v = (v & AND[p]) ^ XOR[p]
            p >>= 1
        return v

    # O(logN) -- a[i] = v
    def pointAssign(self, i, v):
        self._push(i + self.n)
        self.val[i] = v

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self._push(i + self.n)
        self.val[i] += delta

    # O(logN) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        self._push(i + self.n)
        if v > self.val[i]:
            self.val[i] = v

    # O(logN) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        self._push(i + self.n)
        if v < self.val[i]:
            self.val[i] = v
