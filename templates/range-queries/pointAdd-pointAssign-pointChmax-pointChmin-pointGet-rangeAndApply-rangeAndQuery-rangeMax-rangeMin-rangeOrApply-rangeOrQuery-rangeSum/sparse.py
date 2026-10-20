# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeMax-rangeMin-rangeOrApply-rangeOrQuery-rangeSum/sparse.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeMax rangeMin rangeOrApply rangeOrQuery rangeSum
# @data-structure-type: beats
# @complexities:
#   pointAdd: log(U) amortized
#   pointAssign: log(U) amortized
#   pointChmax: log(U) amortized
#   pointChmin: log(U) amortized
#   pointGet: log(U)
#   rangeAndApply: log(U)*log(U) amortized
#   rangeAndQuery: log(U)
#   rangeMax: log(U)
#   rangeMin: log(U)
#   rangeOrApply: log(U)*log(U) amortized
#   rangeOrQuery: log(U)
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mx[4*log(U)] mn[4*log(U)] tot[4*log(U)] sz[4*log(U)] andAll[4*log(U)] orAll[4*log(U)]
#   tags: tagAnd[4*log(U)] tagXor[4*log(U)]
#   other: none
#   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. Per-node lists that grow

# Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
# is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
# right before anything descends past a node or pushes its tags. Otherwise the beats logic below is the
# dense tree's, with children in L / R instead of at 2i / 2i + 1.

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
  force-0 bits (a=0,x=0) need the bit already 0 for all  -> ~a & ~x & orAll must be 0
  force-1 bits (a=0,x=1) need the bit already 1 for all  -> ~a & x & ~andAll must be 0
Dropping the last two costs real time -- a pure OR would never prune.
"""

# ========================


class SparseBitBeats:
    # O(1) -- all zeros over [lo, hi]; any range of integers works
    def __init__(self, lo, hi, bits=20):
        self.lo, self.hi = lo, hi
        self.FULL = FULL = (1 << bits) - 1
        # node 0 is unused; node 1 is the root, one block of hi - lo + 1 zeros
        self.L, self.R, self.ln = [0, 0], [0, 0], [0, 0]
        self.mx = [0] * 2
        self.mn = [0] * 2
        self.tot = [0] * 2
        self.sz = [0] * 2
        self.andAll = [FULL] * 2
        self.orAll = [0] * 2
        self.tagAnd = [FULL] * 2
        self.tagXor = [0] * 2
        self._zero(1, hi - lo + 1)

    # node i becomes a block of k zeros (its defaults, plus every count = k)
    def _zero(self, i, k):
        self.ln[i] = k
        self.sz[i] = k
        self.andAll[i] = 0

    # a fresh node: a block of k zeros
    def _node(self, k):
        j = len(self.L)
        self.L.append(0)
        self.R.append(0)
        self.ln.append(0)
        self.mx.append(0)
        self.mn.append(0)
        self.tot.append(0)
        self.sz.append(0)
        self.andAll.append(self.FULL)
        self.orAll.append(0)
        self.tagAnd.append(self.FULL)
        self.tagXor.append(0)
        self._zero(j, k)
        return j

    # create node i's children (blocks of zeros: the left one gets the extra slot) if it has none yet
    def _kids(self, i):
        if not self.L[i] and self.ln[i] > 1:
            k = self.ln[i]
            self.L[i] = self._node((k + 1) // 2)
            self.R[i] = self._node(k // 2)

    def _pull(self, i):
        l = self.L[i]; r = self.R[i]
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
        self._kids(i)
        if tl == tr:
            return
        a = self.tagAnd[i]; x = self.tagXor[i]
        if a == self.FULL and x == 0:
            return
        self._apply(self.L[i], a, x)
        self._apply(self.R[i], a, x)
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
        self._kids(i)
        tm = (tl + tr) // 2
        self._upd(self.L[i], tl, tm, ql, qr, a, x)
        self._upd(self.R[i], tm + 1, tr, ql, qr, a, x)
        self._pull(i)

    ################ PUBLIC METHODS START HERE ################

    # O(logN logU) -- a[i] &= X for i in [l, r]
    def rangeAndApply(self, l, r, X):
        if l <= r: self._upd(1, self.lo, self.hi, l, r, X & self.FULL, 0)

    # O(logN logU) -- a[i] |= X for i in [l, r]
    def rangeOrApply(self, l, r, X):
        if l <= r: self._upd(1, self.lo, self.hi, l, r, ~X & self.FULL, X & self.FULL)

    def _set(self, i, tl, tr, p, v):
        if tl == tr:
            self.mx[i] = self.mn[i] = self.tot[i] = v
            self.andAll[i] = self.orAll[i] = v
            self.tagAnd[i] = self.FULL; self.tagXor[i] = 0
            return
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        if p <= tm: self._set(self.L[i], tl, tm, p, v)
        else: self._set(self.R[i], tm + 1, tr, p, v)
        self._pull(i)

    # O(logN) -- a[p] = v
    def pointAssign(self, p, v):
        self._set(1, self.lo, self.hi, p, v & self.FULL)

    def _q(self, i, tl, tr, ql, qr, kind):
        if qr < tl or ql > tr:
            return None
        if ql <= tl and qr >= tr:
            return (self.mx, self.mn, self.tot, self.andAll, self.orAll)[kind][i]
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        a = self._q(self.L[i], tl, tm, ql, qr, kind)
        b = self._q(self.R[i], tm + 1, tr, ql, qr, kind)
        if a is None: return b
        if b is None: return a
        if kind == 0: return a if a > b else b
        if kind == 1: return a if a < b else b
        if kind == 2: return a + b
        if kind == 3: return a & b
        return a | b

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r): return None if (l > r) else self._q(1, self.lo, self.hi, l, r, 0)
    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r): return None if (l > r) else self._q(1, self.lo, self.hi, l, r, 1)
    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r): return 0 if (l > r) else self._q(1, self.lo, self.hi, l, r, 2)
    # O(logN) -- a[l] & ... & a[r]
    def rangeAndQuery(self, l, r): return self.FULL if (l > r) else self._q(1, self.lo, self.hi, l, r, 3)
    # O(logN) -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r): return 0 if (l > r) else self._q(1, self.lo, self.hi, l, r, 4)
    # O(logN) -- a[p]
    def pointGet(self, p): return self.rangeMax(p, p)

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)