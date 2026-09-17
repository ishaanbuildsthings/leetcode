# TEMPLATE BY https://github.com/agrawalishaan
#
# ========================
# COMPLEXITIES
#
# O(n) build
# seg = BitBeats_PERFORMANT(arr, 20)   # second arg is the bit width
#
# K = bit width (20 for values < 2^20)
# AMORTIZED O(logN * K):  rangeAnd(l, r, x)      -- a[i] &= x
# AMORTIZED O(logN * K):  rangeOr(l, r, x)       -- a[i] |= x
# AMORTIZED O(logN * K):  rangeXor(l, r, x)      -- a[i] ^= x
# AMORTIZED O(logN):      pointSet(pos, newVal)
#
# O(logN):  rangeMax(l, r)
# O(logN):  rangeMin(l, r)
# O(logN):  rangeSum(l, r)
# O(logN):  rangeAndQuery(l, r)    -- AND of the whole range
# O(logN):  rangeOrQuery(l, r)     -- OR of the whole range
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
the AND and the OR of everything under it, the mixed bits are exactly andAll ^ orAll -- one
&-and-^ gives you the whole set in O(1), which is the only reason this is affordable.

Give each node a score equal to how many of its K bits are mixed, and sum that over all nodes.
A node's score is at most K, and there are O(n) nodes over logN levels, so the whole tree starts
at O(n * K * logN).

WHY THIS IS THE RIGHT THING TO COUNT: an AND / OR / XOR is uniform across a node exactly when it
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
  force-0 bits (a=0,x=0) need the bit already 0 for all  -> ~a & ~x & orAll must be 0
  force-1 bits (a=0,x=1) need the bit already 1 for all  -> ~a & x & ~andAll must be 0
Dropping the last two costs real time -- a pure OR would never prune.
"""

# ========================


class BitBeats_PERFORMANT:
    def __init__(self, arr, bits=20):
        self.n = n = len(arr)
        self.FULL = FULL = (1 << bits) - 1
        size = 4 * max(1, n)
        self.mx = [0] * size
        self.mn = [0] * size
        self.tot = [0] * size
        self.sz = [0] * size
        self.andAll = [FULL] * size
        self.orAll = [0] * size
        self.tagAnd = [FULL] * size
        self.tagXor = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        self.tagAnd[i] = self.FULL; self.tagXor[i] = 0
        if tl == tr:
            v = arr[tl]
            self.mx[i] = self.mn[i] = self.tot[i] = v
            self.andAll[i] = self.orAll[i] = v
            self.sz[i] = 1
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        l = 2 * i; r = l + 1
        mx = self.mx; mn = self.mn
        self.mx[i] = mx[l] if mx[l] > mx[r] else mx[r]
        self.mn[i] = mn[l] if mn[l] < mn[r] else mn[r]
        self.tot[i] = self.tot[l] + self.tot[r]
        self.sz[i] = self.sz[l] + self.sz[r]
        self.andAll[i] = self.andAll[l] & self.andAll[r]
        self.orAll[i] = self.orAll[l] | self.orAll[r]
        self.tagAnd[i] = self.FULL; self.tagXor[i] = 0

    # legal only when every bit the node disagrees on is kept: mixed <= a and mixed & x == 0.
    # then every value changes by the SAME delta, so mx / mn / sum all just shift.
    def _apply(self, i, a, x):
        FULL = self.FULL
        keep = (a ^ x) & FULL
        delta = ((~self.orAll[i]) & x & FULL) - (self.andAll[i] & ~keep & FULL)
        self.mx[i] += delta
        self.mn[i] += delta
        self.tot[i] += delta * self.sz[i]
        self.andAll[i] = ((self.andAll[i] & a) ^ x) & FULL
        self.orAll[i] = ((self.orAll[i] & a) ^ x) & FULL
        self.tagAnd[i] = self.tagAnd[i] & a & FULL
        self.tagXor[i] = ((self.tagXor[i] & a) ^ x) & FULL

    def _push(self, i, tl, tr):
        if tl == tr:
            return
        a = self.tagAnd[i]; x = self.tagXor[i]
        if a == self.FULL and x == 0:
            return
        self._apply(2 * i, a, x)
        self._apply(2 * i + 1, a, x)
        self.tagAnd[i] = self.FULL; self.tagXor[i] = 0

    # nothing changes iff for every value v in the node, (v & a) ^ x == v.
    # per bit: keep (a=1,x=0) always fine; flip (a=1,x=1) always changes;
    # force-0 (a=0,x=0) fine only if already 0 everywhere; force-1 fine only if already 1 everywhere.
    def _noEffect(self, i, a, x):
        FULL = self.FULL
        if a & x & FULL: return False
        if ~a & ~x & self.orAll[i] & FULL: return False
        if ~a & x & ~self.andAll[i] & FULL: return False
        return True

    def _upd(self, i, tl, tr, ql, qr, a, x):
        if qr < tl or ql > tr:
            return
        if self._noEffect(i, a, x):
            return
        mixed = (self.andAll[i] ^ self.orAll[i]) & self.FULL
        if ql <= tl and qr >= tr and (mixed & (~a | x) & self.FULL) == 0:
            self._apply(i, a, x)
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._upd(2 * i, tl, tm, ql, qr, a, x)
        self._upd(2 * i + 1, tm + 1, tr, ql, qr, a, x)
        self._pull(i)

    ################ PUBLIC METHODS START HERE ################

    def rangeAnd(self, l, r, X):
        if l <= r and self.n: self._upd(1, 0, self.n - 1, l, r, X & self.FULL, 0)

    def rangeOr(self, l, r, X):
        if l <= r and self.n: self._upd(1, 0, self.n - 1, l, r, ~X & self.FULL, X & self.FULL)

    def rangeXor(self, l, r, X):
        if l <= r and self.n: self._upd(1, 0, self.n - 1, l, r, self.FULL, X & self.FULL)

    def _set(self, i, tl, tr, p, v):
        if tl == tr:
            self.mx[i] = self.mn[i] = self.tot[i] = v
            self.andAll[i] = self.orAll[i] = v
            self.tagAnd[i] = self.FULL; self.tagXor[i] = 0
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        if p <= tm: self._set(2 * i, tl, tm, p, v)
        else: self._set(2 * i + 1, tm + 1, tr, p, v)
        self._pull(i)

    def pointSet(self, p, v):
        if self.n: self._set(1, 0, self.n - 1, p, v & self.FULL)

    def _q(self, i, tl, tr, ql, qr, kind):
        if qr < tl or ql > tr:
            return None
        if ql <= tl and qr >= tr:
            return (self.mx, self.mn, self.tot, self.andAll, self.orAll)[kind][i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._q(2 * i, tl, tm, ql, qr, kind)
        b = self._q(2 * i + 1, tm + 1, tr, ql, qr, kind)
        if a is None: return b
        if b is None: return a
        if kind == 0: return a if a > b else b
        if kind == 1: return a if a < b else b
        if kind == 2: return a + b
        if kind == 3: return a & b
        return a | b

    def rangeMax(self, l, r): return None if (l > r or not self.n) else self._q(1, 0, self.n-1, l, r, 0)
    def rangeMin(self, l, r): return None if (l > r or not self.n) else self._q(1, 0, self.n-1, l, r, 1)
    def rangeSum(self, l, r): return 0 if (l > r or not self.n) else self._q(1, 0, self.n-1, l, r, 2)
    def rangeAndQuery(self, l, r): return self.FULL if (l > r or not self.n) else self._q(1, 0, self.n-1, l, r, 3)
    def rangeOrQuery(self, l, r): return 0 if (l > r or not self.n) else self._q(1, 0, self.n-1, l, r, 4)
    def pointGet(self, p): return self.rangeMax(p, p)