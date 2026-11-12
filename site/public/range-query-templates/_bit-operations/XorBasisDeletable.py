# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/XorBasisDeletable.py

# XorBasisDeletable: an XOR basis you can insert values into and delete values from, online (a multiset: copies count).
# Every query is about the values held right now: what XORs of their subsets can make (the empty subset makes 0).
# Values must be >= 0. B = number of bits in the largest value, N = number of values held.
# Use XorBasis instead when nothing is ever deleted: the same queries, with O(B) inserts.
#
# basis = XorBasisDeletable([3, 10, 5])
# basis.remove(10)    # True: one copy of 10 was held
# basis.maxXor()      # 6, from 3 ^ 5
#
# How deletes work (https://eolymp.com/posts/7u074ngkv127l3fl0m33bf5gck): the values are split into several bases, each
# spanning a subspace of the one before, grouped by dimension; the biggest spans everything, so queries read it. A value
# goes into the first basis that can't already make it. To delete v from basis X: if X without v still spans the next
# smaller basis Y, v is just dropped (X loses a dimension); else some value y of Y restores X's span, so y takes v's
# place in X and y is deleted from Y instead. That walks down at most B dimensions. Each basis keeps fully reduced rows
# that remember which of its values they combine, so every step is O(B).
class XorBasisDeletable:
    # O(N * B^2)
    def __init__(self, arr=()):
        self.levels = []  # levels[d]: the bases of dimension d, which all span the same values
        self.byVal = {}  # value -> ids of its copies held in a basis
        self.val = {}  # id -> value
        self.loc = {}  # id -> its basis
        self.pos = {}  # id -> its position in that basis (bit pos of the row masks)
        self.nextId = 0
        self.zeros = 0  # copies of 0 (held, but in no basis)
        self.count = 0
        for x in arr:
            self.insert(x)

    # inserts x; returns True if x couldn't be made before (the rank grew), else False
    # O(B^2)
    def insert(self, x):
        if x < 0:
            raise ValueError(f"XorBasisDeletable.insert: {x} is negative")
        self.count += 1
        if x == 0:
            self.zeros += 1
            return False
        e = self.nextId
        self.nextId += 1
        self.val[e] = x
        self.byVal.setdefault(x, []).append(e)
        top = self._topLevel()
        for d in range(top, 0, -1):  # the first basis (biggest first) that can't make x
            if self.levels[d] and self._reduce(self.levels[d][-1], x):
                b = self.levels[d][-1]
                self._detach(b)
                self._addRow(b, e, x)
                self._attach(b)
                return d == top
        b = _Basis()  # every basis can make x: a new one of dimension 1 (it spans the same as any other of dimension 1)
        self._addRow(b, e, x)
        self._attach(b)
        return top == 0

    # removes one copy of x; returns True if one was held, else False (nothing changes)
    # O(B^2)
    def remove(self, x):
        if x == 0:
            if not self.zeros:
                return False
            self.zeros -= 1
            self.count -= 1
            return True
        ids = self.byVal.get(x)
        if not ids:
            return False
        e = ids.pop()
        if not ids:
            del self.byVal[x]
        self.count -= 1
        del self.val[e]
        b, p = self.loc.pop(e), self.pos.pop(e)
        while True:
            d = len(b.vec)
            rows = [i for i in range(d) if b.msk[i] >> p & 1]  # the rows that use the deleted value
            r0 = min(rows, key=lambda i: b.piv[i])
            pivotsUsed = 0
            for i in rows:
                pivotsUsed |= 1 << b.piv[i]
            # y (any value b can make) needs the deleted one iff its reduced form uses an odd number of those rows
            smaller = next((self.levels[k][-1] for k in range(d - 1, 0, -1) if self.levels[k]), None)
            yAt = -1
            if smaller is not None:
                for j, yid in enumerate(smaller.elem):
                    if bin(self.val[yid] & pivotsUsed).count("1") & 1:
                        yAt = j
                        break
            self._detach(b)
            self._removeAt(b, p, rows, r0)
            if yAt < 0:  # b without the value still spans the smaller basis: done, b drops a dimension
                if b.vec:
                    self._attach(b)
                return True
            yid = smaller.elem[yAt]  # y takes the deleted value's place (b keeps its span) and leaves the smaller basis
            self._addRow(b, yid, self.val[yid])
            self._attach(b)
            b, p = smaller, yAt

    # True if some subset XORs to exactly x (x = 0 is always True: the empty subset)
    # O(B)
    def canMake(self, x):
        if x < 0:
            return False
        top = self._top()
        return x == 0 if top is None else self._reduce(top, x) == 0

    # largest XOR of any subset (0 if nothing is held)
    # O(B)
    def maxXor(self):
        return self.maxXorWith(0)

    # largest x ^ (XOR of some subset)
    # O(B)
    def maxXorWith(self, x):
        if x < 0:
            raise ValueError(f"XorBasisDeletable.maxXorWith: {x} is negative")
        top = self._top()
        if top is not None:
            for v, p in zip(top.vec, top.piv):
                if not x >> p & 1:
                    x ^= v
        return x

    # smallest x ^ (XOR of some subset)
    # O(B)
    def minXorWith(self, x):
        if x < 0:
            raise ValueError(f"XorBasisDeletable.minXorWith: {x} is negative")
        top = self._top()
        return x if top is None else self._reduce(top, x)

    # smallest XOR of a non-empty subset: 0 if some non-empty subset XORs to 0, None if nothing is held
    # O(B)
    def minNonzeroXor(self):
        if self.count == 0:
            return None
        top = self._top()
        if top is None or self.count > len(top.vec):
            return 0
        return min(top.vec)

    # the kth smallest distinct value some subset makes, k 0-indexed (k = 0 -> 0), or None if k >= countDistinctXors()
    # O(B log B)
    def kthSmallestXor(self, k):
        if k < 0:
            raise ValueError(f"XorBasisDeletable.kthSmallestXor: k = {k} is negative")
        top = self._top()
        rows = sorted(top.vec) if top is not None else []
        if k >> len(rows):
            return None
        res = 0
        for i, v in enumerate(rows):
            if k >> i & 1:
                res ^= v
        return res

    # number of distinct values the subsets make, counting 0 from the empty subset: 2^rank
    # O(B)
    def countDistinctXors(self):
        return 1 << self.rank()

    # number of subsets of the held values (by position, the empty one included) whose XOR is exactly x, mod mod:
    # 2^(N - rank) if x can be made, else 0
    # O(B + log(N))
    def countSubsetsMakingMod(self, x, mod):
        return pow(2, self.count - self.rank(), mod) if self.canMake(x) else 0

    # size of the basis of the held values
    # O(B)
    def rank(self):
        return self._topLevel()

    # how many values are held, copies and zeros included
    # O(1)
    def size(self):
        return self.count

    # a basis of the held values, largest first (rank of them, fully reduced)
    # O(B log B)
    def basis(self):
        top = self._top()
        return sorted(top.vec, reverse=True) if top is not None else []

    # ---- internals ----

    def _topLevel(self):
        for d in range(len(self.levels) - 1, 0, -1):
            if self.levels[d]:
                return d
        return 0

    def _top(self):
        d = self._topLevel()
        return self.levels[d][-1] if d else None

    @staticmethod
    def _reduce(b, x):  # x with b's pivot bits cleared: 0 iff b can make x
        for v, p in zip(b.vec, b.piv):
            if x >> p & 1:
                x ^= v
        return x

    def _attach(self, b):  # into the list of its dimension
        d = len(b.vec)
        while len(self.levels) <= d:
            self.levels.append([])
        b.idx = len(self.levels[d])
        self.levels[d].append(b)

    def _detach(self, b):
        lst = self.levels[len(b.vec)]
        last = lst.pop()
        if last is not b:
            lst[b.idx] = last
            last.idx = b.idx

    def _addRow(self, b, e, x):  # value x (id e) into b, which can't make it yet; keeps the rows fully reduced
        p = len(b.elem)
        m = 1 << p
        for i in range(len(b.vec)):
            if x >> b.piv[i] & 1:
                x ^= b.vec[i]
                m ^= b.msk[i]
        q = x.bit_length() - 1
        for i in range(len(b.vec)):
            if b.vec[i] >> q & 1:
                b.vec[i] ^= x
                b.msk[i] ^= m
        b.vec.append(x)
        b.msk.append(m)
        b.piv.append(q)
        b.elem.append(e)
        self.loc[e] = b
        self.pos[e] = p

    def _removeAt(self, b, p, rows, r0):  # drops the value at position p (its rows: rows; r0 has the lowest pivot)
        for i in rows:
            if i != r0:  # (r0's pivot is below theirs, so their pivots stay put)
                b.vec[i] ^= b.vec[r0]
                b.msk[i] ^= b.msk[r0]
        for arr in (b.vec, b.msk, b.piv):
            arr[r0] = arr[-1]
            arr.pop()
        last = len(b.elem) - 1  # the last position moves into p, so positions stay 0..dim-1
        if p != last:
            moved = b.elem[last]
            b.elem[p] = moved
            self.pos[moved] = p
            for i in range(len(b.msk)):
                if b.msk[i] >> last & 1:
                    b.msk[i] ^= (1 << last) | (1 << p)
        b.elem.pop()


class _Basis:  # one basis: fully reduced rows (vec, the values of elem they XOR together as msk, highest bit piv)
    __slots__ = ("vec", "msk", "piv", "elem", "idx")

    def __init__(self):
        self.vec, self.msk, self.piv, self.elem = [], [], [], []
        self.idx = -1
