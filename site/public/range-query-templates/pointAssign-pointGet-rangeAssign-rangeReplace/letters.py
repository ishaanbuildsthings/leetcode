# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAssign-pointGet-rangeAssign-rangeReplace/letters.py
# @operations: getAll pointAssign pointGet rangeAssign rangeReplace
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N*log(N)
#   pointAssign: U*log(N)
#   pointGet: log(N)
#   rangeAssign: U*log(N)
#   rangeReplace: U*log(N)
#   build: N*U
# @memory:
#   layout: pow2-iterative
#   node: t[4*N]
#   tags: mp[2*N*U]
#   other: none
#   note: U = valHi - valLo + 1 (every value ever in the array is in [valLo, valHi]); each tag is a whole map old value -> new value, so a push costs O(U); a map is kept only while pending (handed down, its memory is reused), so mp is far below 2*N*U in practice

# Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
# operations that make sense on characters are listed.
# Lazy seg tree whose tag is a value map (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r]
# into y, and rangeAssign(l, r, v) sets a[l..r] = v, in O(U log N), U = valHi - valLo + 1: good when the values are
# few (911G: 1..100). A pending tag is a map old value -> new value for the whole segment, so any mix of changes
# composes into one map. All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies.

class ValueMapSeg:
    # leaves t[cap + i] hold a[i] - valLo (-1: padding past n); mp[k]: node k's pending map for its children (None: none)
    __slots__ = ("n", "cap", "U", "valLo", "t", "mp")

    # O(N*U) -- arr: the initial array (a list); every value it will ever hold must be in [valLo, valHi]
    def __init__(self, arr, valLo, valHi):
        n = self.n = len(arr)
        self.valLo, self.U = ord(valLo), ord(valHi) - ord(valLo) + 1
        cap = self.cap = 1 << max(0, (n - 1).bit_length())
        self.t = [-1] * (2 * cap)
        for i, v in enumerate(arr):
            self.t[cap + i] = self._off(v)
        self.mp = [None] * cap

    # O(1) -- the length of the array
    def size(self):
        return self.n

    # O(logN) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        k = self.cap + i
        v = self.t[k]
        k >>= 1
        while k:  # (a map higher up is newer: apply them bottom-up)
            if self.mp[k] is not None:
                v = self.mp[k][v]
            k >>= 1
        return chr(v + self.valLo)

    # O(U*logN) -- a[i] = v; needs valLo <= v <= valHi; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        o, k = self._off(v), self.cap + i
        for h in range(self.cap.bit_length() - 1, 0, -1):
            self._push(k >> h)
        self.t[k] = o

    # O(U*logN) -- every a[i] == x with l <= i <= r becomes y; needs valLo <= y <= valHi; needs 0 <= l <= r < size(),
    # else IndexError
    def rangeReplace(self, l, r, x, y):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeReplace: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b = self._off(y)
        a = ord(x) - self.valLo
        if 0 <= a < self.U and a != b:
            self._update(l, r, lambda k: self._applyRep(k, a, b))

    # O(U*logN) -- a[l..r] = v; needs valLo <= v <= valHi; needs 0 <= l <= r < size(), else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        o = self._off(v)
        self._update(l, r, lambda k: self._applyMap(k, [o] * self.U))

    # O(N log N) -- the whole current array
    def getAll(self):
        return [self.pointGet(i) for i in range(self.n)]

    # ---- internals ----

    def _off(self, v):  # v's index into a map
        o = ord(v) - self.valLo
        if not 0 <= o < self.U:
            raise ValueError(f"value {v} is outside [valLo, valHi]")
        return o

    def _applyMap(self, k, g):  # node k's segment goes through map g (newer than anything below k)
        if k >= self.cap:
            if self.t[k] >= 0:
                self.t[k] = g[self.t[k]]
            return
        m = self.mp[k]
        self.mp[k] = g[:] if m is None else [g[v] for v in m]

    def _applyRep(self, k, a, b):  # every a in node k's segment becomes b
        if k >= self.cap:
            if self.t[k] == a:
                self.t[k] = b
            return
        m = self.mp[k]
        if m is None:
            m = self.mp[k] = list(range(self.U))
        self.mp[k] = [b if v == a else v for v in m]

    def _push(self, k):  # hand node k's pending map to its children
        g = self.mp[k]
        if g is not None:
            self._applyMap(2 * k, g)
            self._applyMap(2 * k + 1, g)
            self.mp[k] = None

    def _pushAbove(self, l, r):  # push every map above the leaves l..r - 1 (offset by cap) down to them
        for h in range(self.cap.bit_length() - 1, 0, -1):
            if (l >> h) << h != l:
                self._push(l >> h)
            if (r >> h) << h != r:
                self._push((r - 1) >> h)

    def _cover(self, l, r):  # the nodes that exactly cover a[l..r], every map above them pushed
        l, r = l + self.cap, r + self.cap + 1
        self._pushAbove(l, r)
        out = []
        while l < r:
            if l & 1:
                out.append(l)
                l += 1
            if r & 1:
                r -= 1
                out.append(r)
            l >>= 1
            r >>= 1
        return out

    def _update(self, l, r, apply):
        l, r = l + self.cap, r + self.cap + 1
        self._pushAbove(l, r)
        a, b = l, r
        while a < b:
            if a & 1:
                apply(a)
                a += 1
            if b & 1:
                b -= 1
                apply(b)
            a >>= 1
            b >>= 1
