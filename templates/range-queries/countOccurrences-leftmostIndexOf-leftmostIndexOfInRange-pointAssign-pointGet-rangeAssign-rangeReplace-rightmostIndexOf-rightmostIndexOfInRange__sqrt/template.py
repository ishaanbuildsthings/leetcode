# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeAssign-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange__sqrt/template.py
# @operations: countOccurrences getAll leftmostIndexOf leftmostIndexOfInRange pointAssign pointGet rangeAssign rangeReplace rightmostIndexOf rightmostIndexOfInRange
# @data-structure-type: sqrt
# @letters: same
# @complexities:
#   countOccurrences: sqrt(N)
#   getAll: N
#   leftmostIndexOf: sqrt(N)
#   leftmostIndexOfInRange: sqrt(N)
#   pointAssign: 1 amortized
#   pointGet: 1 amortized
#   rangeAssign: sqrt(N) amortized
#   rangeReplace: sqrt(N) amortized
#   rightmostIndexOf: sqrt(N)
#   rightmostIndexOfInRange: sqrt(N)
#   build: N
# @memory:
#   layout: none
#   node: cls[1*N] par[2*N] val[2*N] cnt[2*N] where[1*N]
#   tags: none
#   other: none
#   note: blocks of about sqrt(N) values; each block's values are classes joined by a union-find (union by size, path halving: O(alpha), counted as O(1)); where maps each value in the block to its class; values are hashed, so any values work

from math import isqrt

# Blocks whose values form a union-find of classes (mass change, CF 911G, in O(sqrt N)): the array is cut into blocks
# of about sqrt(N) values. Inside a block equal values form a class, and the classes are joined by a union-find:
# rangeReplace(l, r, x, y) on a whole block renames x's class to y, or joins it into y's, in O(1); rangeAssign joins
# every class. Only the (at most two) partly covered blocks are touched value by value. Any values work (each block
# hashes them). a[i] and a[i] = v are O(1) amortized. All indices 0-based, ranges inclusive [l, r]; searches return -1
# when nothing qualifies.
class _Block:
    # a run of the array: cls[k] is the class of its k-th value. Classes form a union-find (par);
    # a root class holds its value (val) and how many of the block's values are in it (cnt). where: value -> root class
    __slots__ = ("cls", "par", "val", "cnt", "where")

    def __init__(self, vals):
        self.build(vals)

    def build(self, vals):  # O(len) -- the classes from scratch
        where, par, val, cnt, cls = {}, [], [], [], []
        for v in vals:
            c = where.get(v)
            if c is None:
                c = where[v] = len(par)
                par.append(c)
                val.append(v)
                cnt.append(0)
            cnt[c] += 1
            cls.append(c)
        self.cls, self.par, self.val, self.cnt, self.where = cls, par, val, cnt, where

    def __len__(self):
        return len(self.cls)

    def find(self, c):  # c's root class (path halving)
        par = self.par
        while par[c] != c:
            par[c] = par[par[c]]
            c = par[c]
        return c

    def get(self, k):  # the k-th value
        return self.val[self.find(self.cls[k])]

    def values(self):  # every value, in order
        out = [self.val[self.find(c)] for c in self.cls]
        return out

    def count(self, x):  # how many x's
        c = self.where.get(x)
        return self.cnt[c] if c is not None else 0

    def replace(self, x, y):  # O(1) -- every x becomes y: x's class is renamed, or joined to y's
        cx = self.where.pop(x, None)
        if cx is None:
            return
        cy = self.where.get(y)
        if cy is None:
            self.val[cx] = y
            self.where[y] = cx
            return
        if self.cnt[cx] > self.cnt[cy]:  # (union by size)
            cx, cy = cy, cx
        self.par[cx] = cy
        self.cnt[cy] += self.cnt[cx]
        self.val[cy] = y
        self.where[y] = cy

    def assignAll(self, v):  # every value becomes v: every class joined into one (O(1) amortized: each join removes one)
        roots = list(self.where.values())
        r = max(roots, key=lambda c: self.cnt[c])
        for c in roots:
            if c != r:
                self.par[c] = r
                self.cnt[r] += self.cnt[c]
        self.val[r] = v
        self.where = {v: r}

    def assign(self, k, v):  # O(1) amortized -- the k-th value becomes v (a class of its own if v is new here)
        c = self.find(self.cls[k])
        old = self.val[c]
        if old == v:
            return
        self.cnt[c] -= 1
        if not self.cnt[c]:
            del self.where[old]
        d = self.where.get(v)
        if d is None:
            d = self.where[v] = len(self.par)
            self.par.append(d)
            self.val.append(v)
            self.cnt.append(0)
        self.cnt[d] += 1
        self.cls[k] = d
        if len(self.par) > 2 * len(self.cls) + 8:  # (many dead classes: start over, paid for by the assigns)
            self.build(self.values())


class SqrtReplace:
    __slots__ = ("blocks", "n", "B")

    # O(N) -- arr: the initial array (a list)
    def __init__(self, arr):
        self._fill(list(arr))

    # O(1) -- the length of the array
    def size(self):
        return self.n

    # O(N) -- the whole current array
    def getAll(self):
        out = []
        for b in self.blocks:
            out += b.values()
        return out

    # O(1) amortized) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        b, k = self._locate(i)
        return b.get(k)

    # O(1) amortized) -- a[i] = v; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        b, k = self._locate(i)
        b.assign(k, v)

    # O(sqrt(N)) amortized -- every a[i] == x with l <= i <= r becomes y; needs 0 <= l <= r < size(), else IndexError
    def rangeReplace(self, l, r, x, y):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeReplace: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        if x == y:
            return
        for b, lo, hi, full, _ in self._span(l, r):
            if full:
                b.replace(x, y)
            else:
                for k in range(lo, hi + 1):
                    if b.get(k) == x:
                        b.assign(k, y)

    # O(sqrt(N)) amortized -- a[l..r] = v; needs 0 <= l <= r < size(), else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        for b, lo, hi, full, _ in self._span(l, r):
            if full:
                b.assignAll(v)
            else:
                for k in range(lo, hi + 1):
                    b.assign(k, v)

    # O(sqrt(N)) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        res = 0
        for b, lo, hi, full, _ in self._span(l, r):
            res += b.count(x) if full else sum(b.get(k) == x for k in range(lo, hi + 1))
        return res

    # O(sqrt(N)) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        return self._find(0, self.n - 1, x, True)

    # O(sqrt(N)) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        return self._find(0, self.n - 1, x, False)

    # O(sqrt(N)) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._find(l, r, x, True)

    # O(sqrt(N)) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._find(l, r, x, False)

    # ---- internals ----

    @staticmethod
    def _idealB(n):
        return max(1, isqrt(n))

    def _fill(self, vals):  # blocks of about _idealB values holding vals
        n = self.n = len(vals)
        B = self.B = self._idealB(n)
        self.blocks = [_Block(vals[s:s + B]) for s in range(0, n, B)]

    def _locate(self, i):  # (block, position in it) of a[i]
        return self.blocks[i // self.B], i % self.B

    def _span(self, l, r):  # (block, lo, hi, whole, start) for each block meeting a[l..r]: positions lo..hi of it,
        B = self.B  # whether that is all of it, and the index of its first value
        for j in range(l // B, r // B + 1):
            b, start = self.blocks[j], j * B
            lo, hi = max(l - start, 0), min(r - start, len(b) - 1)
            yield b, lo, hi, lo == 0 and hi == len(b) - 1, start

    def _find(self, l, r, x, left):  # the first (left) / last i in [l, r] with a[i] == x, or -1
        spans = list(self._span(l, r)) if l <= r else []
        for b, lo, hi, full, start in (spans if left else reversed(spans)):
            if full and not b.count(x):
                continue
            for k in (range(lo, hi + 1) if left else range(hi, lo - 1, -1)):
                if b.get(k) == x:
                    return start + k
        return -1
