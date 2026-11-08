# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostGtX-leftmostGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeMax-rangeOrApply-rangeOrQuery-rangeSum-rightmostGtX-rightmostGteX/template.py
# @operations: andAll getAll leftmostGtX leftmostGteX maxAll orAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeMax rangeOrApply rangeOrQuery rangeSum rightmostGtX rightmostGteX sumAll
# @data-structure-type: beats
# @complexities:
#   andAll: log(N)
#   getAll: N
#   leftmostGtX: log(N)
#   leftmostGteX: log(N)
#   maxAll: log(N)
#   orAll: log(N)
#   pointAdd: log(N) amortized
#   pointAssign: log(N) amortized
#   pointChmax: log(N) amortized
#   pointChmin: log(N) amortized
#   pointGet: log(N)
#   rangeAndApply: log(N)*log(U) amortized
#   rangeAndQuery: log(N)
#   rangeMax: log(N)
#   rangeOrApply: log(N)*log(U) amortized
#   rangeOrQuery: log(N)
#   rangeSum: log(N)
#   rightmostGtX: log(N)
#   rightmostGteX: log(N)
#   sumAll: log(N)
#   build: N
# @memory:
#   layout: 4n-recursive
#   node: mx[4*N] tot[4*N] andAgg[4*N] orAgg[4*N]
#   tags: tagAnd[4*N] tagXor[4*N]
#   other: none
#   note: the and/or tags compose into one (and, xor) pair per node (or X is the pair (~X, X)); no range xor, see BitCountTree
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/range-AndApply-OrApply-Min-Max-Sum-AndQuery-OrQuery-pointSet.py

# ========================
# COMPLEXITIES
#
# O(n) build
# seg = BitBeats_PERFORMANT(arr, 20)   # second arg is the bit width
#
# K = bit width (20 for values < 2^20)
# AMORTIZED O(logN * K):  rangeAndApply(l, r, x)      -- a[i] &= x
# AMORTIZED O(logN * K):  rangeOrApply(l, r, x)       -- a[i] |= x
# AMORTIZED O(logN):      pointAssign(pos, newVal)
#
# O(logN):  rangeMax(l, r)      -- max of a[l..r]
# O(logN):  rangeSum(l, r)      -- a[l] + ... + a[r]
# O(logN):  rangeAndQuery(l, r) -- a[l] & ... & a[r]
# O(logN):  rangeOrQuery(l, r)  -- a[l] | ... | a[r]
# O(logN):  pointGet(pos)
# O(n) space
#
# Whole thing is O((n + q) * K * logN). Values must be NON-NEGATIVE and below 2^K. Python ints cannot overflow.
#
# ========================
#
"""
HOW DO POTENTIALS WORK? (bitwise beats)

THE POTENTIAL IS PER BIT, NOT PER VALUE. This is what makes this template different from the
chmin/chmax beats ones, where the potential counts distinct values.

Call a bit MIXED in a node when the node's values do not all agree on it. Since the node stores
the AND and the OR of everything under it, the mixed bits are exactly andAgg ^ orAgg -- one
&-and-^ gives you the whole set in O(1), which is the only reason this is affordable.

Give each node a score equal to how many of its K bits are mixed, and sum that over all nodes.
A node's score is at most K, and there are O(n) nodes over logN levels, so the whole tree starts
at O(n * K * logN).

WHY THIS IS THE RIGHT THING TO COUNT: an AND / OR is uniform across a node exactly when it
leaves every mixed bit alone. If it touches only bits the node already agrees on, then every value
changes by the SAME delta -- which is why max, min AND sum all survive the O(1) apply here, not
just max. And if it does touch a mixed bit, then after the operation that bit is no longer mixed
(an AND forces it to 0 everywhere, an OR forces it to 1 everywhere), so the score drops.

So the three cases are:
  1) the op cannot change anything here                  -> return, free
  2) fully covered and no mixed bit is touched           -> O(1) apply, no potential spent, which
                                                            is exactly why we must NOT descend
  3) a mixed bit is touched                              -> descend, and that bit becomes uniform
                                                            in the nodes below, paying for the visit
Same shape as chmin beats: we can only descend when potential actually drops.

WHY THERE IS NO RANGE XOR: xor flips a bit everywhere, so a mixed bit stays mixed. A fully covered
node whose mixed bits xor touches can't take the O(1) apply (its values would move by different
amounts), and descending spends no potential, so one xor over a range of distinct values walks the
whole tree: O(N) per op, every time. For xor with sums use BitCountTree, which counts set bits per
node instead and handles xor in O(logN * K) without beats.

Pushing a tag to the children costs O(K) of potential and there are logN of them per op, so q ops
add O(q * K * logN). Total O((n + q) * K * logN).

THE TAG IS TWO MASKS, (tagAnd, tagXor), meaning  v -> (v & tagAnd) ^ tagXor.
Every per-bit function you can build out of AND / OR / XOR is one of four things -- keep, force 0,
force 1, flip -- and all four fit:
    keep     a=1 x=0        force 0  a=0 x=0
    force 1  a=0 x=1        flip     a=1 x=1
so the three operations are just
    AND x  ->  (a, x) = (x,  0)
    OR  x  ->  (a, x) = (~x, x)
    XOR x  ->  (a, x) = (~0, x)
and two tags compose into one:
    a = a1 & a2,   x = (x1 & a2) ^ x2

WHY A PUSHED TAG IS ALWAYS LEGAL:
_apply has a precondition -- mixed <= a and mixed & x == 0 -- that nothing in the code checks.
It holds because a tag is only ever created at a node that satisfied it, the operation does not
change that node's mixed set (it only touches uniform bits), and composing two tags that both
respect a mixed set gives a tag that still respects it. A child's mixed bits are a subset of its
parent's, so a tag legal for the parent is legal for the child.

WHY THE PRUNE NEEDS ALL THREE CHECKS (_noEffect):
nothing changes iff for every value v in the node, (v & a) ^ x == v. Per bit:
  flip bits    (a=1,x=1) always change something         -> a & x must be 0
  force-0 bits (a=0,x=0) need the bit already 0 for all  -> ~a & ~x & orAgg must be 0
  force-1 bits (a=0,x=1) need the bit already 1 for all  -> ~a & x & ~andAgg must be 0
Dropping the last two costs real time -- a pure OR would never prune.
"""

# ========================


class BitBeats_PERFORMANT:
    def __init__(self, arr, bits=20):
        self.n = n = len(arr)
        self.FULL = FULL = (1 << bits) - 1
        size = 4 * max(1, n)
        self.mx = [0] * size
        self.tot = [0] * size
        self.andAgg = [FULL] * size
        self.orAgg = [0] * size
        self.tagAnd = [FULL] * size
        self.tagXor = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        self.tagAnd[i] = self.FULL; self.tagXor[i] = 0
        if tl == tr:
            v = arr[tl]
            self.mx[i] = self.tot[i] = self.andAgg[i] = self.orAgg[i] = v
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        l = 2 * i; r = l + 1
        mx = self.mx
        self.mx[i] = mx[l] if mx[l] > mx[r] else mx[r]
        self.tot[i] = self.tot[l] + self.tot[r]
        self.andAgg[i] = self.andAgg[l] & self.andAgg[r]
        self.orAgg[i] = self.orAgg[l] | self.orAgg[r]
        self.tagAnd[i] = self.FULL; self.tagXor[i] = 0

    # legal only when every bit the node disagrees on is kept: mixed <= a and mixed & x == 0.
    # then every value changes by the SAME delta, so mx / tot just shift (k = the node's length).
    def _apply(self, i, a, x, k):
        FULL = self.FULL
        keep = (a ^ x) & FULL
        delta = ((~self.orAgg[i]) & x & FULL) - (self.andAgg[i] & ~keep & FULL)
        self.mx[i] += delta
        self.tot[i] += delta * k
        self.andAgg[i] = ((self.andAgg[i] & a) ^ x) & FULL
        self.orAgg[i] = ((self.orAgg[i] & a) ^ x) & FULL
        self.tagAnd[i] = self.tagAnd[i] & a & FULL
        self.tagXor[i] = ((self.tagXor[i] & a) ^ x) & FULL

    def _push(self, i, tl, tr):
        if tl == tr:
            return
        a = self.tagAnd[i]; x = self.tagXor[i]
        if a == self.FULL and x == 0:
            return
        tm = (tl + tr) // 2
        self._apply(2 * i, a, x, tm - tl + 1)
        self._apply(2 * i + 1, a, x, tr - tm)
        self.tagAnd[i] = self.FULL; self.tagXor[i] = 0

    # nothing changes iff for every value v in the node, (v & a) ^ x == v.
    # per bit: keep (a=1,x=0) always fine; flip (a=1,x=1) always changes;
    # force-0 (a=0,x=0) fine only if already 0 everywhere; force-1 fine only if already 1 everywhere.
    def _noEffect(self, i, a, x):
        FULL = self.FULL
        if a & x & FULL: return False
        if ~a & ~x & self.orAgg[i] & FULL: return False
        if ~a & x & ~self.andAgg[i] & FULL: return False
        return True

    def _upd(self, i, tl, tr, ql, qr, a, x):
        if qr < tl or ql > tr:
            return
        if self._noEffect(i, a, x):
            return
        mixed = (self.andAgg[i] ^ self.orAgg[i]) & self.FULL
        if ql <= tl and qr >= tr and (mixed & (~a | x) & self.FULL) == 0:
            self._apply(i, a, x, tr - tl + 1)
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._upd(2 * i, tl, tm, ql, qr, a, x)
        self._upd(2 * i + 1, tm + 1, tr, ql, qr, a, x)
        self._pull(i)

    ################ PUBLIC METHODS START HERE ################

    # O(logN * logU) amortized -- a[i] &= X for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAndApply(self, l, r, X):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAndApply: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l <= r and self.n: self._upd(1, 0, self.n - 1, l, r, X & self.FULL, 0)

    # O(logN * logU) amortized -- a[i] |= X for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeOrApply(self, l, r, X):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeOrApply: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l <= r and self.n: self._upd(1, 0, self.n - 1, l, r, ~X & self.FULL, X & self.FULL)

    def _set(self, i, tl, tr, p, v):
        if tl == tr:
            self.mx[i] = self.tot[i] = self.andAgg[i] = self.orAgg[i] = v
            self.tagAnd[i] = self.FULL; self.tagXor[i] = 0
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        if p <= tm: self._set(2 * i, tl, tm, p, v)
        else: self._set(2 * i + 1, tm + 1, tr, p, v)
        self._pull(i)

    # O(logN) amortized -- a[p] = v; needs 0 <= p < n, else IndexError
    def pointAssign(self, p, v):
        if not 0 <= p < self.n:
            raise IndexError(f"pointAssign: needs 0 <= p < n, got p = {p}, n = {self.n}")
        if self.n: self._set(1, 0, self.n - 1, p, v & self.FULL)

    def _q(self, i, tl, tr, ql, qr, kind):
        if qr < tl or ql > tr:
            return None
        if ql <= tl and qr >= tr:
            return (self.mx, self.tot, self.andAgg, self.orAgg)[kind][i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._q(2 * i, tl, tm, ql, qr, kind)
        b = self._q(2 * i + 1, tm + 1, tr, ql, qr, kind)
        if a is None: return b
        if b is None: return a
        if kind == 0: return a if a > b else b
        if kind == 1: return a + b
        if kind == 2: return a & b
        return a | b

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return None if (l > r or not self.n) else self._q(1, 0, self.n-1, l, r, 0)
    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return 0 if (l > r or not self.n) else self._q(1, 0, self.n-1, l, r, 1)
    # O(logN) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeAndQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAndQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self.FULL if (l > r or not self.n) else self._q(1, 0, self.n-1, l, r, 2)
    # O(logN) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeOrQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeOrQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return 0 if (l > r or not self.n) else self._q(1, 0, self.n-1, l, r, 3)
    # O(logN) -- a[p]; needs 0 <= p < n, else IndexError
    def pointGet(self, p):
        if not 0 <= p < self.n:
            raise IndexError(f"pointGet: needs 0 <= p < n, got p = {p}, n = {self.n}")
        return self.rangeAndQuery(p, p)

    def _getAllRec(self, i, tl, tr, out):
        if tl == tr:
            out.append(self.andAgg[i])
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._getAllRec(2 * i, tl, tm, out)
        self._getAllRec(2 * i + 1, tm + 1, tr, out)

    # O(N) -- the whole array: one DFS that pushes every tag down and reads the leaves left to right
    def getAll(self):
        out = []
        if self.n: self._getAllRec(1, 0, self.n - 1, out)
        return out

    # O(logN) amortized -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logN) amortized -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)

    # O(logN) amortized -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)

    # O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.n < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.n - 1)

    # O(log(N)) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def andAll(self):
        if self.n < 1:
            raise IndexError("andAll: needs n >= 1")
        return self.rangeAndQuery(0, self.n - 1)

    # O(log(N)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def orAll(self):
        if self.n < 1:
            raise IndexError("orAll: needs n >= 1")
        return self.rangeOrQuery(0, self.n - 1)

    # O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mx
        return self._firstPass(1, 0, self.n - 1, l, r, lambda i: F[i] > x) if l <= r and self.n else -1

    # O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mx
        return self._firstPass(1, 0, self.n - 1, l, r, lambda i: F[i] >= x) if l <= r and self.n else -1

    # O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mx
        return self._lastPass(1, 0, self.n - 1, l, r, lambda i: F[i] > x) if l <= r and self.n else -1

    # O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        F = self.mx
        return self._lastPass(1, 0, self.n - 1, l, r, lambda i: F[i] >= x) if l <= r and self.n else -1

    # the first index in [l, r] under node i whose value passes ok(node), or -1: O(logN), since only one
    # node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    def _firstPass(self, i, tl, tr, l, r, ok):
        if r < tl or tr < l or not ok(i):
            return -1
        if tl == tr:
            return tl
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        res = self._firstPass(2 * i, tl, tm, l, r, ok)
        return res if res != -1 else self._firstPass(2 * i + 1, tm + 1, tr, l, r, ok)

    # the last index in [l, r] under node i whose value passes ok(node), or -1: O(logN), since only one
    # node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    def _lastPass(self, i, tl, tr, l, r, ok):
        if r < tl or tr < l or not ok(i):
            return -1
        if tl == tr:
            return tl
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        res = self._lastPass(2 * i + 1, tm + 1, tr, l, r, ok)
        return res if res != -1 else self._lastPass(2 * i, tl, tm, l, r, ok)
