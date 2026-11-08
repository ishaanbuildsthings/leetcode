# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-replace-seq/template.py
# @operations: append appendLeft countOccurrences cut getAll insertAt insertCopiesAt leftmostIndexOf leftmostIndexOfInRange merge paste pointAssign pointGet pop popLeft rangeAssign rangeReplace rangeRotateLeft rangeRotateRight rightmostIndexOf rightmostIndexOfInRange size split trisect
# @data-structure-type: sqrt
# @letters: same
# @complexities:
#   append: sqrt(N) amortized
#   appendLeft: sqrt(N) amortized
#   countOccurrences: sqrt(N) amortized
#   cut: sqrt(N) amortized
#   getAll: N
#   insertAt: sqrt(N) amortized
#   insertCopiesAt: K+sqrt(N) amortized
#   leftmostIndexOf: sqrt(N) amortized
#   leftmostIndexOfInRange: sqrt(N) amortized
#   merge: sqrt(N) amortized
#   paste: sqrt(N) amortized
#   pointAssign: sqrt(N) amortized
#   pointGet: sqrt(N)
#   rangeAssign: sqrt(N) amortized
#   rangeReplace: sqrt(N) amortized
#   rangeRotateLeft: sqrt(N) amortized
#   rangeRotateRight: sqrt(N) amortized
#   rightmostIndexOf: sqrt(N) amortized
#   rightmostIndexOfInRange: sqrt(N) amortized
#   split: sqrt(N) amortized
#   trisect: sqrt(N) amortized
#   size: 1
#   pop: sqrt(N) amortized
#   popLeft: sqrt(N) amortized
#   build: N
# @memory:
#   layout: none
#   node: cls[1*N] par[2*N] val[2*N] cnt[2*N] where[1*N]
#   tags: none
#   other: none
#   note: blocks of about sqrt(N) values; each block's values are classes joined by a union-find (union by size, path halving: O(alpha), counted as O(1)); where maps each value in the block to its class; values are hashed, so any values work

from math import isqrt

# Blocks whose values form a union-find of classes (mass change, CF 911G, in O(sqrt(N)), with sequence edits): the
# array is cut into blocks of about sqrt(N) values. Inside a block equal values form a class, and the classes are
# joined by a union-find: rangeReplace(l, r, x, y) on a whole block renames x's class to y, or joins it into y's, in
# O(1); rangeAssign joins every class. Only the (at most two) partly covered blocks are touched value by value. Any
# values work (each block hashes them). The blocks form a list you can insert into anywhere, rotate, cut pieces out of
# (that is how to erase) and paste back; a[i] then walks the list (O(sqrt(N))). All indices 0-based, ranges inclusive
# [l, r], an index always the position in the CURRENT array; searches return -1 when nothing qualifies.
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
    # pieces (cut / split / trisect) are SqrtReplaces of their own: paste / merge move their blocks over
    __slots__ = ("blocks", "n", "B")

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self._fill(list(arr))

    # O(1) -- the current length of the array
    def size(self):
        return self.n

    # O(N) -- the whole current array
    def getAll(self):
        out = []
        for b in self.blocks:
            out += b.values()
        return out

    # O(sqrt(N)) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        b, k = self._locate(i)
        return b.get(k)

    # O(sqrt(N)) amortized -- a[i] = v; needs 0 <= i < size(), else IndexError
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

    # O(sqrt(N)) amortized -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        res = 0
        for b, lo, hi, full, _ in self._span(l, r):
            res += b.count(x) if full else sum(b.get(k) == x for k in range(lo, hi + 1))
        return res

    # O(sqrt(N)) amortized -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        return self._find(0, self.n - 1, x, True)

    # O(sqrt(N)) amortized -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        return self._find(0, self.n - 1, x, False)

    # O(sqrt(N)) amortized -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._find(l, r, x, True)

    # O(sqrt(N)) amortized -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._find(l, r, x, False)

    # O(sqrt(N)) amortized -- insert v so it becomes a[i]; needs 0 <= i <= size(), else IndexError
    def insertAt(self, i, v):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        j, k = self._at(i)
        if j == len(self.blocks):  # (the end: onto the last block)
            if not j or len(self.blocks[-1]) >= 2 * self.B:
                self.blocks.append(_Block([v]))
                self.n += 1
                return
            j, k = j - 1, len(self.blocks[-1])
        vals = self.blocks[j].values()
        vals.insert(k, v)
        if len(vals) > 2 * self.B:  # (too long: two blocks)
            h = len(vals) // 2
            self.blocks[j:j + 1] = [_Block(vals[:h]), _Block(vals[h:])]
        else:
            self.blocks[j].build(vals)
        self.n += 1
        if self._idealB(self.n) > 2 * self.B:  # (grown a lot: bigger blocks)
            self._fill(self.getAll())

    # O(sqrt(N)) amortized -- append v to the end
    def append(self, v):
        self.insertAt(self.n, v)

    # O(sqrt(N)) amortized -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(k + sqrt(N)) amortized -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    # 0 <= i <= size(), else IndexError
    def insertCopiesAt(self, i, v, k):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertCopiesAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        if k <= 0:
            return
        j = self._splitAt(i)
        self.blocks[j:j] = [_Block([v] * min(self.B, k - s)) for s in range(0, k, self.B)]
        self.n += k
        self._tidy()

    # O(sqrt(N)) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    # taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateLeft(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateLeft: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        k %= r - l + 1
        if k:
            j1 = self._splitAt(l)
            j2 = self._splitAt(l + k)
            j3 = self._splitAt(r + 1)
            self.blocks[j1:j3] = self.blocks[j2:j3] + self.blocks[j1:j2]
            self._tidy()

    # O(sqrt(N)) amortized -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    # (negative shifts left); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateRight(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateRight: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self.rangeRotateLeft(l, r, -k)

    # O(sqrt(N)) amortized -- remove a[l..r] and return it as a SqrtReplace of its own (indices from 0); needs
    # 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"cut: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        j1 = self._splitAt(l)
        j2 = self._splitAt(r + 1)
        piece = SqrtReplace()
        piece.blocks, piece.n, piece.B = self.blocks[j1:j2], r - l + 1, self.B
        del self.blocks[j1:j2]
        self.n -= r - l + 1
        self._tidy()
        piece._tidy()
        return piece

    # O(sqrt(N)) amortized -- insert all of other (any SqrtReplace, e.g. a cut piece) so it starts at a[i]; other is
    # left empty; needs 0 <= i <= size(), else IndexError
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError(f"paste: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        j = self._splitAt(i)
        self.blocks[j:j] = other.blocks
        self.n += other.n
        other.blocks, other.n = [], 0
        self._tidy()

    # O(sqrt(N)) amortized -- append all of other at the end; other is left empty
    def merge(self, other):
        self.paste(self.n, other)

    # O(sqrt(N)) amortized -- (a[0..k-1], a[k..]) as two SqrtReplaces of their own; this one is left empty; needs
    # 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError(f"split: needs 0 <= k <= size(), got k = {k}, n = {self.size()}")
        left = SqrtReplace()
        left.blocks, left.n, left.B = self.blocks, self.n, self.B
        self.blocks, self.n = [], 0
        right = left.cut(k, left.n - 1) if k < left.n else SqrtReplace()
        return left, right

    # O(sqrt(N)) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtReplaces of their own; this one is left
    # empty; needs 0 <= l <= r < size(), else IndexError
    def trisect(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"trisect: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        left, right = self.split(r + 1)
        left, mid = left.split(l)
        return left, mid, right

    # O(sqrt(N) amortized) -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        n = self.size()
        if n < 1:
            raise IndexError("pop: needs size() >= 1")
        v = self.pointGet(n - 1)
        self.cut(n - 1, n - 1)
        return v

    # O(sqrt(N) amortized) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        v = self.pointGet(0)
        self.cut(0, 0)
        return v

    # ---- internals ----

    @staticmethod
    def _idealB(n):
        return max(16, isqrt(n))

    def _fill(self, vals):  # blocks of about _idealB values holding vals
        n = self.n = len(vals)
        B = self.B = self._idealB(n)
        self.blocks = [_Block(vals[s:s + B]) for s in range(0, n, B)]

    # O(N / B + B) amortized -- merge each run of neighbours that fit in one block (each merge is paid for by the
    # split that made it); when the array has grown so much that B is too small, rebuild into even blocks
    def _tidy(self):
        if self._idealB(self.n) > 2 * self.B:
            return self._fill(self.getAll())
        out, B = [], self.B
        for b in self.blocks:
            if not len(b):
                continue
            if out and len(out[-1]) + len(b) <= B:
                b = _Block(out.pop().values() + b.values())
            out.append(b)
        self.blocks = out

    def _at(self, i):  # (block index, position in it) of a[i]; i == size() gives (number of blocks, 0)
        for j, b in enumerate(self.blocks):
            m = len(b)
            if i < m:
                return j, i
            i -= m
        return len(self.blocks), 0

    def _locate(self, i):  # (block, position in it) of a[i]
        j, k = self._at(i)
        return self.blocks[j], k

    def _splitAt(self, i):  # make a block start at a[i] (0 <= i <= size()): that block's index
        j, k = self._at(i)
        if k:
            vals = self.blocks[j].values()
            self.blocks[j:j + 1] = [_Block(vals[:k]), _Block(vals[k:])]
            return j + 1
        return j

    def _span(self, l, r):  # (block, lo, hi, whole, start) for each block meeting a[l..r]: positions lo..hi of it,
        i = 0  # whether that is all of it, and the index of its first value
        for b in self.blocks:
            m = len(b)
            if i + m > l:
                lo, hi = max(l - i, 0), min(r - i, m - 1)
                yield b, lo, hi, lo == 0 and hi == m - 1, i
                if i + m > r:
                    return
            i += m

    def _find(self, l, r, x, left):  # the first (left) / last i in [l, r] with a[i] == x, or -1
        spans = list(self._span(l, r)) if l <= r else []
        for b, lo, hi, full, start in (spans if left else reversed(spans)):
            if full and not b.count(x):
                continue
            for k in (range(lo, hi + 1) if left else range(hi, lo - 1, -1)):
                if b.get(k) == x:
                    return start + k
        return -1
