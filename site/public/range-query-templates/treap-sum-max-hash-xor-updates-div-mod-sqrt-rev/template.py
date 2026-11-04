# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-max-hash-xor-updates-div-mod-sqrt-rev/template.py
# @operations: append appendLeft cut getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv rangeFloorSqrt rangeHash rangeHashReversed rangeMax rangeMod rangeReverse rangeRotateLeft rangeRotateRight rangeSum rangeXorQuery rangesEqual rightmostGtX rightmostGteX size split trisect
# @data-structure-type: treap
# @complexities:
#   append: log(N) expected
#   appendLeft: log(N) expected
#   cut: log(N) expected
#   getAll: N
#   insertAt: log(N) expected
#   insertCopiesAt: log(N) expected
#   isPalindrome: log(N) expected
#   leftmostGtX: log(N) expected
#   leftmostGteX: log(N) expected
#   merge: log(N) expected
#   paste: log(N) expected
#   pointAdd: log(N) expected
#   pointAssign: log(N) expected
#   pointChmax: log(N) expected
#   pointChmin: log(N) expected
#   pointGet: log(N) expected
#   rangeFloorDiv: log(N)*log(U) amortized
#   rangeFloorSqrt: log(N)*log(log(U)) amortized
#   rangeHash: log(N) expected
#   rangeHashReversed: log(N) expected
#   rangeMax: log(N) expected
#   rangeMod: log(N)*log(U) amortized
#   rangeReverse: log(N) expected
#   rangeRotateLeft: log(N) expected
#   rangeRotateRight: log(N) expected
#   rangeSum: log(N) expected
#   rangeXorQuery: log(N) expected
#   rangesEqual: log(N) expected
#   rightmostGtX: log(N) expected
#   rightmostGteX: log(N) expected
#   split: log(N) expected
#   trisect: log(N) expected
#   size: 1
#   build: N
# @memory:
#   layout: none
#   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] xr[1*N]
#   tags: rev[1*N]
#   other: none
#   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

# Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
# out of (that is how to erase) and paste them back in O(logN) expected each, with rangeFloorDiv, rangeMod,
# rangeFloorSqrt; each node keeps its sum, its max, its forward / backward hash (and B^size), its xor over its
# subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches
# return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet to its children".
import random
from math import isqrt


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


class ImplicitTreap:
    # one node pool shared by every ImplicitTreap: cut / paste move nodes between them, so a piece from one can go
    # into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    # whole run), so there is nothing to reset between test cases
    val = [0]
    pri = [0]
    L = [0]
    R = [0]
    sz = [0]
    sm = [0]
    mx = [0]
    fh = [0]
    bh = [0]
    pw = [1]
    xr = [0]
    rev = [0]
    __slots__ = ("root",)

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr))

    def _empty(self):  # a new, empty ImplicitTreap (on the same pool, like every one)
        return ImplicitTreap()

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN) expected -- append v to the end
    def append(self, v):
        self.root = self._merge(self.root, self._newNode(v))

    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0); needs
    # 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"cut: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        self.root = self._merge(a, c)
        piece = self._empty()
        piece.root = b
        return piece

    # O(N) -- the whole current array, every pending tag applied on the way
    def getAll(self):
        L, R, val = self.L, self.R, self.val
        out, stack, t = [], [], self.root
        while stack or t:
            while t:
                self._push(t)
                stack.append(t)
                t = L[t]
            t = stack.pop()
            out.append(val[t])
            t = R[t]
        return out

    # O(logN) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else IndexError (i = size() appends)
    def insertAt(self, i, v):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._newNode(v)), c)

    # O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    # 0 <= i <= size(), else IndexError
    def insertCopiesAt(self, i, v, k):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertCopiesAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        if k > 0:
            a, c = self._split(self.root, i)
            self.root = self._merge(self._merge(a, self._build([v] * k)), c)

    # O(logN) expected -- is a[l..r] a palindrome (its two hashes agree); needs 0 <= l <= r < size(), else IndexError
    def isPalindrome(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"isPalindrome: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.fh[b] == self.bh[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max); needs
    # 0 <= l <= r < size(), else IndexError
    def leftmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        t, i, res = b, 0, -1
        if t and F[t] > x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if L[t] and F[L[t]] > x:
                    t = L[t]
                elif val[t] > x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    i += sz[L[t]] + 1
                    t = R[t]
        self._join(a, b, c)
        return res

    # O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max); needs
    # 0 <= l <= r < size(), else IndexError
    def leftmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        t, i, res = b, 0, -1
        if t and F[t] >= x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if L[t] and F[L[t]] >= x:
                    t = L[t]
                elif val[t] >= x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    i += sz[L[t]] + 1
                    t = R[t]
        self._join(a, b, c)
        return res

    # O(logN) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(logN) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i] (needs
    # 0 <= i <= size(), else IndexError); other is left empty
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError(f"paste: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), c)
        other.root = 0

    # O(logN) expected -- a[i] += v; needs 0 <= i < size(), else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAdd: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = self.val[t] + v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = v; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = v
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmax: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = max(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmin: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        t, path = self._find(i)
        self.val[t] = min(self.val[t], v)
        self._pull(t)
        for x in reversed(path):
            self._pull(x)

    # O(logN) expected -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        return self.val[self._find(i)[0]]

    # amortized O(logN * logU) expected -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing); needs
    # 0 <= l <= r < size(), else IndexError
    def rangeFloorDiv(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeFloorDiv: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        if x >= 2:
            self._shrink(b, 1, lambda v: v // x)
        self._join(a, b, c)

    # amortized O(logN * loglogU) expected -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0); needs
    # 0 <= l <= r < size(), else IndexError
    def rangeFloorSqrt(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeFloorSqrt: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        self._shrink(b, 2, isqrt)
        self._join(a, b, c)

    # O(logN) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    # 0 <= l <= r < size(), else IndexError
    def rangeHash(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeHash: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.fh[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs
    # 0 <= l <= r < size(), else IndexError
    def rangeHashReversed(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeHashReversed: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.bh[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- max of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMax: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.mx[b]
        self._join(a, b, c)
        return res

    # amortized O(logN * logU) expected -- a[i] %= x for i in [l, r] (values >= 0, x >= 1); needs
    # 0 <= l <= r < size(), else IndexError
    def rangeMod(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMod: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        if x >= 1:
            self._shrink(b, x, lambda v: v % x)
        self._join(a, b, c)

    # O(logN) expected -- reverse a[l..r] in place; needs 0 <= l <= r < size(), else IndexError
    def rangeReverse(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeReverse: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        self._applyRev(b)
        self._join(a, b, c)

    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is taken
    # mod the length (negative shifts right); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateLeft(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateLeft: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)

    # O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    # (negative shifts left); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateRight(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateRight: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self.rangeRotateLeft(l, r, -k)

    # O(logN) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeSum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.sm[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeXorQuery(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeXorQuery: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.xr[b]
        self._join(a, b, c)
        return res

    # O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    # 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), else IndexError
    def rangesEqual(self, l1, r1, l2, r2):
        if not (0 <= l1 <= r1 < self.size() and 0 <= l2 <= r2 < self.size()):
            raise IndexError(f"rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), got "
                             f"l1 = {l1}, r1 = {r1}, l2 = {l2}, r2 = {r2}, n = {self.size()}")
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max); needs
    # 0 <= l <= r < size(), else IndexError
    def rightmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        t, i, res = b, 0, -1
        if t and F[t] > x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if R[t] and F[R[t]] > x:
                    i += sz[L[t]] + 1
                    t = R[t]
                elif val[t] > x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    t = L[t]
        self._join(a, b, c)
        return res

    # O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max); needs
    # 0 <= l <= r < size(), else IndexError
    def rightmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.mx
        t, i, res = b, 0, -1
        if t and F[t] >= x:  # some value in a[l..r] passes
            while True:
                self._push(t)
                if R[t] and F[R[t]] >= x:
                    i += sz[L[t]] + 1
                    t = R[t]
                elif val[t] >= x:
                    res = l + i + sz[L[t]]
                    break
                else:
                    t = L[t]
        self._join(a, b, c)
        return res

    # O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty; needs
    # 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError(f"split: needs 0 <= k <= size(), got k = {k}, n = {self.size()}")
        left, right = self._empty(), self._empty()
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty; needs
    # 0 <= l <= r < size(), else IndexError
    def trisect(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"trisect: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.root, mid.root, right.root = self._cut(l, r)
        self.root = 0
        return left, mid, right

    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        self.sm.append(v)
        self.mx.append(v)
        self.fh.append((v + _HO) % _HP)
        self.bh.append((v + _HO) % _HP)
        self.pw.append(_HB)
        self.xr.append(v)
        self.rev.append(0)
        return x

    # a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    def _build(self, vals):
        pri, L, R = self.pri, self.L, self.R
        stack = []
        for v in vals:
            x, last = self._newNode(v), 0
            while stack and pri[stack[-1]] < pri[x]:
                last = stack.pop()
            L[x] = last
            if stack:
                R[stack[-1]] = x
            stack.append(x)
        root = stack[0] if stack else 0
        order, todo = [], ([root] if root else [])
        while todo:
            x = todo.pop()
            order.append(x)
            if L[x]:
                todo.append(L[x])
            if R[x]:
                todo.append(R[x])
        for x in reversed(order):
            self._pull(x)
        return root

    def _pull(self, x):  # recompute x from its children
        l, r = self.L[x], self.R[x]
        self.sz[x] = self.sz[l] + self.sz[r] + 1
        v = self.val[x]
        self.sm[x] = self.sm[l] + v + self.sm[r]
        m = v
        if l and self.mx[l] > m:
            m = self.mx[l]
        if r and self.mx[r] > m:
            m = self.mx[r]
        self.mx[x] = m
        B, P, pw, fh, bh = _HB, _HP, self.pw, self.fh, self.bh
        hv = (v + _HO) % P
        pw[x] = pw[l] * B % P * pw[r] % P
        fh[x] = ((fh[l] * B + hv) * pw[r] + fh[r]) % P
        bh[x] = ((bh[r] * B + hv) * pw[l] + bh[l]) % P
        self.xr[x] = self.xr[l] ^ v ^ self.xr[r]

    def _applyRev(self, x):  # reverse x's subtree
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
            self.fh[x], self.bh[x] = self.bh[x], self.fh[x]

    def _push(self, x):  # hand x's pending tags to its children
        if self.rev[x]:
            self._applyRev(self.L[x])
            self._applyRev(self.R[x])
            self.rev[x] = 0

    def _shrink(self, t, lim, f):  # every value v >= lim under t becomes f(v) (the rest are fixed)
        if not t or self.mx[t] < lim:
            return
        self._push(t)
        v = self.val[t]
        if v >= lim:
            self.val[t] = f(v)
        self._shrink(self.L[t], lim, f)
        self._shrink(self.R[t], lim, f)
        self._pull(t)

    def _split(self, t, k):  # (first k of t, the rest)
        if not t:
            return 0, 0
        self._push(t)
        L, R = self.L, self.R
        if self.sz[L[t]] >= k:
            a, L[t] = self._split(L[t], k)
            self._pull(t)
            return a, t
        R[t], b = self._split(R[t], k - self.sz[L[t]] - 1)
        self._pull(t)
        return t, b

    def _merge(self, a, b):  # a's elements, then b's
        if not a or not b:
            return a or b
        if self.pri[a] > self.pri[b]:
            self._push(a)
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        self._push(b)
        self.L[b] = self._merge(a, self.L[b])
        self._pull(b)
        return b

    def _cut(self, l, r):  # (a[0..l-1], a[l..r], a[r+1..])
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    def _join(self, a, b, c):
        self.root = self._merge(self._merge(a, b), c)

    def _find(self, i):  # (node holding a[i], the nodes above it), every tag on the way pushed
        L, sz, t, path = self.L, self.sz, self.root, []
        while True:
            self._push(t)
            ls = sz[L[t]]
            if i == ls:
                return t, path
            path.append(t)
            if i < ls:
                t = L[t]
            else:
                i -= ls + 1
                t = self.R[t]


# Example (pieces move between treaps; merge appends and leaves its argument empty):
#     t = ImplicitTreap([1, 2, 3, 4, 5])
#     left, mid, right = t.trisect(1, 3)  # left = [1], mid = [2, 3, 4], right = [5]; t is empty now
#     t.merge(right)                      # t = [5]
#     t.merge(mid)                        # t = [5, 2, 3, 4]
#     t.merge(left)                       # t = [5, 2, 3, 4, 1]
