# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeAssign-rangeReplace-rangeSum-rightmostIndexOf-rightmostIndexOfInRange/letters.py
# @operations: countOccurrences getAll leftmostIndexOf leftmostIndexOfInRange pointAssign pointGet rangeAssign rangeReplace rightmostIndexOf rightmostIndexOfInRange
# @data-structure-type: lazy-seg-tree
# @complexities:
#   countOccurrences: U*log(N)
#   getAll: N*log(N)
#   leftmostIndexOf: U*log(N)
#   leftmostIndexOfInRange: U*log(N)
#   pointAssign: U*log(N)
#   pointGet: log(N)
#   rangeAssign: U*log(N)
#   rangeReplace: U*log(N)
#   rightmostIndexOf: U*log(N)
#   rightmostIndexOfInRange: U*log(N)
#   build: N*U
# @memory:
#   layout: pow2-iterative
#   node: t[4*N] cnt[2*N*U] sm[4*N]
#   tags: mp[2*N*U]
#   other: none
#   note: U = valHi - valLo + 1 (every value ever in the array is in [valLo, valHi]); each tag is a whole map old value -> new value, so a push costs O(U); a map is kept only while pending (handed down, its memory is reused), so mp is far below 2*N*U in practice

# Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
# operations that make sense on characters are listed.
# Lazy seg tree whose tag is a value map (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r]
# into y, and rangeAssign(l, r, v) sets a[l..r] = v, in O(U log N), U = valHi - valLo + 1: good when the values are
# few (911G: 1..100). A pending tag is a map old value -> new value for the whole segment, so any mix of changes
# composes into one map. Each node also keeps how many times each value appears below it and its sum, for
# countOccurrences / where x first / last appears / rangeSum. All indices 0-based, ranges inclusive [l, r]; searches
# return -1 when nothing qualifies.

class ValueMapSeg:
    # leaves t[cap + i] hold a[i] - valLo (-1: padding past n); mp[k]: node k's pending map for its children (None: none)
    # cnt[k][v]: how many leaves below internal node k hold v (its own map already applied)
    __slots__ = ("n", "cap", "U", "valLo", "t", "mp", "cnt", "sm")

    # O(N*U) -- arr: the initial array (a list); every value it will ever hold must be in [valLo, valHi]
    def __init__(self, arr, valLo, valHi):
        n = self.n = len(arr)
        self.valLo, self.U = ord(valLo), ord(valHi) - ord(valLo) + 1
        cap = self.cap = 1 << max(0, (n - 1).bit_length())
        self.t = [-1] * (2 * cap)
        for i, v in enumerate(arr):
            self.t[cap + i] = self._off(v)
        self.mp = [None] * cap
        self.cnt = [None] * cap
        self.sm = [0] * (2 * cap)
        for i in range(n):
            self.sm[cap + i] = self.t[cap + i] + self.valLo
        for k in range(cap - 1, 0, -1):
            self._pull(k)

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
        self.sm[k] = o + self.valLo
        k >>= 1
        while k:
            self._pull(k)
            k >>= 1

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

    # O(U*logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a = ord(x) - self.valLo
        if not 0 <= a < self.U:
            return 0
        res = 0
        for k in self._cover(l, r):
            res += self._count(k, a)
        return res

    # O(U*logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        return self._find(x, 0, self.n - 1, True)

    # O(U*logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        return self._find(x, 0, self.n - 1, False)

    # O(U*logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._find(x, l, r, True)

    # O(U*logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._find(x, l, r, False)

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
                self.sm[k] = self.t[k] + self.valLo
            return
        m = self.mp[k]
        self.mp[k] = g[:] if m is None else [g[v] for v in m]
        c, new = self.cnt[k], [0] * self.U
        for v in range(self.U):
            if c[v]:
                new[g[v]] += c[v]
        self.cnt[k] = new
        lo = self.valLo
        self.sm[k] = sum((v + lo) * w for v, w in enumerate(new) if w)

    def _applyRep(self, k, a, b):  # every a in node k's segment becomes b
        if k >= self.cap:
            if self.t[k] == a:
                self.t[k] = b
                self.sm[k] = b + self.valLo
            return
        m = self.mp[k]
        if m is None:
            m = self.mp[k] = list(range(self.U))
        self.mp[k] = [b if v == a else v for v in m]
        c = self.cnt[k]
        self.sm[k] += (b - a) * c[a]
        c[b] += c[a]
        c[a] = 0

    def _push(self, k):  # hand node k's pending map to its children
        g = self.mp[k]
        if g is not None:
            self._applyMap(2 * k, g)
            self._applyMap(2 * k + 1, g)
            self.mp[k] = None

    def _pull(self, k):  # recompute internal node k from its children (k has no pending map)
        if 2 * k >= self.cap:
            c = [0] * self.U
            for j in (2 * k, 2 * k + 1):
                if self.t[j] >= 0:
                    c[self.t[j]] += 1
            self.cnt[k] = c
        else:
            self.cnt[k] = [p + q for p, q in zip(self.cnt[2 * k], self.cnt[2 * k + 1])]
        self.sm[k] = self.sm[2 * k] + self.sm[2 * k + 1]

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
        for h in range(1, self.cap.bit_length()):
            if (l >> h) << h != l:
                self._pull(l >> h)
            if (r >> h) << h != r:
                self._pull((r - 1) >> h)

    def _count(self, k, a):  # how many a's in node k's segment (its own map applied)
        return int(self.t[k] == a) if k >= self.cap else self.cnt[k][a]

    def _find(self, x, l, r, left):  # the first (left) / last i in [l, r] with a[i] == x, or -1
        a = ord(x) - self.valLo
        if not 0 <= a < self.U:
            return -1
        return self._walk(1, 0, self.cap - 1, l, r, a, left)

    def _walk(self, k, nl, nr, l, r, a, left):
        if r < nl or nr < l or not self._count(k, a):
            return -1
        if k >= self.cap:
            return nl
        self._push(k)
        m = (nl + nr) >> 1
        kids = ((2 * k, nl, m), (2 * k + 1, m + 1, nr))
        for c, cl, cr in (kids if left else kids[::-1]):
            res = self._walk(c, cl, cr, l, r, a, left)
            if res != -1:
                return res
        return -1
