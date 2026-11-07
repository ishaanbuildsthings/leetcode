# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeMax-rangeMin-rangeOrApply-rangeOrQuery-rangeSum-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/sparse.py
# @operations: leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeMax rangeMin rangeOrApply rangeOrQuery rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
# @data-structure-type: beats
# @complexities:
#   leftmostGtX: log(U)
#   leftmostGteX: log(U)
#   leftmostLtX: log(U)
#   leftmostLteX: log(U)
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
#   rightmostGtX: log(U)
#   rightmostGteX: log(U)
#   rightmostLtX: log(U)
#   rightmostLteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: mx[4*log(U)] mn[4*log(U)] tot[4*log(U)] andAll[4*log(U)] orAll[4*log(U)]
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
# AMORTIZED O(logU * K):  rangeAndApply(l, r, x)      -- a[i] &= x
# AMORTIZED O(logU * K):  rangeOrApply(l, r, x)       -- a[i] |= x
# AMORTIZED O(logU):      pointAssign(pos, newVal)
#
# O(logU):  rangeMax(l, r)      -- max of a[l..r]
# O(logU):  rangeMin(l, r)      -- min of a[l..r]
# O(logU):  rangeSum(l, r)      -- a[l] + ... + a[r]
# O(logU):  rangeAndQuery(l, r) -- a[l] & ... & a[r]
# O(logU):  rangeOrQuery(l, r)  -- a[l] | ... | a[r]
# O(logU):  pointGet(pos)
# O(n) space
#
# Whole thing is O((n + q) * K * logU). Values must be NON-NEGATIVE and below 2^K. Python ints cannot overflow.
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
        self.andAll = [FULL] * 2
        self.orAll = [0] * 2
        self.tagAnd = [FULL] * 2
        self.tagXor = [0] * 2
        self._zero(1, hi - lo + 1)

    # node i becomes a block of k zeros (its defaults, plus every count = k)
    def _zero(self, i, k):
        self.ln[i] = k
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
        mx = self.mx
        self.mx[i] = mx[l] if mx[l] > mx[r] else mx[r]
        mn = self.mn
        self.mn[i] = mn[l] if mn[l] < mn[r] else mn[r]
        self.tot[i] = self.tot[l] + self.tot[r]
        self.andAll[i] = self.andAll[l] & self.andAll[r]
        self.orAll[i] = self.orAll[l] | self.orAll[r]
        self.tagAnd[i] = self.FULL; self.tagXor[i] = 0

    # legal only when every bit the node disagrees on is kept: mixed <= a and mixed & x == 0.
    # then every value changes by the SAME delta, so mx / mn / tot just shift (k = the node's length).
    def _apply(self, i, a, x, k):
        FULL = self.FULL
        keep = (a ^ x) & FULL
        delta = ((~self.orAll[i]) & x & FULL) - (self.andAll[i] & ~keep & FULL)
        self.mx[i] += delta
        self.mn[i] += delta
        self.tot[i] += delta * k
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
        self._kids(i)
        tm = (tl + tr) // 2
        self._apply(self.L[i], a, x, tm - tl + 1)
        self._apply(self.R[i], a, x, tr - tm)
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
            self._apply(i, a, x, tr - tl + 1)
            return
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        self._upd(self.L[i], tl, tm, ql, qr, a, x)
        self._upd(self.R[i], tm + 1, tr, ql, qr, a, x)
        self._pull(i)

    ################ PUBLIC METHODS START HERE ################

    # O(logU logU) -- a[i] &= X for i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def rangeAndApply(self, l, r, X):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeAndApply: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if l <= r: self._upd(1, self.lo, self.hi, l, r, X & self.FULL, 0)

    # O(logU logU) -- a[i] |= X for i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def rangeOrApply(self, l, r, X):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeOrApply: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if l <= r: self._upd(1, self.lo, self.hi, l, r, ~X & self.FULL, X & self.FULL)

    def _set(self, i, tl, tr, p, v):
        if tl == tr:
            self.mx[i] = self.mn[i] = self.tot[i] = self.andAll[i] = self.orAll[i] = v
            self.tagAnd[i] = self.FULL; self.tagXor[i] = 0
            return
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        if p <= tm: self._set(self.L[i], tl, tm, p, v)
        else: self._set(self.R[i], tm + 1, tr, p, v)
        self._pull(i)

    # O(logU) -- a[p] = v; needs lo <= p <= hi, else IndexError
    def pointAssign(self, p, v):
        if not self.lo <= p <= self.hi:
            raise IndexError(f"pointAssign: needs lo <= p <= hi, got p = {p}")
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

    # O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMax(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeMax: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return None if (l > r) else self._q(1, self.lo, self.hi, l, r, 0)
    # O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMin(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeMin: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return None if (l > r) else self._q(1, self.lo, self.hi, l, r, 1)
    # O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeSum(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return 0 if (l > r) else self._q(1, self.lo, self.hi, l, r, 2)
    # O(logU) -- a[l] & ... & a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeAndQuery(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeAndQuery: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self.FULL if (l > r) else self._q(1, self.lo, self.hi, l, r, 3)
    # O(logU) -- a[l] | ... | a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeOrQuery(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeOrQuery: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return 0 if (l > r) else self._q(1, self.lo, self.hi, l, r, 4)
    # O(logU) -- a[p]; needs lo <= p <= hi, else IndexError
    def pointGet(self, p):
        if not self.lo <= p <= self.hi:
            raise IndexError(f"pointGet: needs lo <= p <= hi, got p = {p}")
        return self.rangeAndQuery(p, p)

    # a[i] = max(a[i], val); needs lo <= i <= hi, else IndexError
    def pointChmax(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmax: needs lo <= i <= hi, got i = {i}")
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] = min(a[i], val); needs lo <= i <= hi, else IndexError
    def pointChmin(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmin: needs lo <= i <= hi, got i = {i}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] += delta; needs lo <= i <= hi, else IndexError
    def pointAdd(self, i, delta):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAdd: needs lo <= i <= hi, got i = {i}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"leftmostGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mx
        res = self._firstPass(1, self.lo, self.hi, l, r, lambda i: F[i] > x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"leftmostGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mx
        res = self._firstPass(1, self.lo, self.hi, l, r, lambda i: F[i] >= x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostLtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"leftmostLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mn
        res = self._firstPass(1, self.lo, self.hi, l, r, lambda i: F[i] < x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostLteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"leftmostLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mn
        res = self._firstPass(1, self.lo, self.hi, l, r, lambda i: F[i] <= x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rightmostGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mx
        res = self._lastPass(1, self.lo, self.hi, l, r, lambda i: F[i] > x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rightmostGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mx
        res = self._lastPass(1, self.lo, self.hi, l, r, lambda i: F[i] >= x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostLtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rightmostLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mn
        res = self._lastPass(1, self.lo, self.hi, l, r, lambda i: F[i] < x) if l <= r else None
        return self.lo - 1 if res is None else res

    # O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostLteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rightmostLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        F = self.mn
        res = self._lastPass(1, self.lo, self.hi, l, r, lambda i: F[i] <= x) if l <= r else None
        return self.lo - 1 if res is None else res

    # the first index in [l, r] under node i whose value passes ok(node), or None: O(logU), since only one
    # node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    def _firstPass(self, i, tl, tr, l, r, ok):
        if r < tl or tr < l or not ok(i):
            return None
        if tl == tr:
            return tl
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        res = self._firstPass(self.L[i], tl, tm, l, r, ok)
        return res if res is not None else self._firstPass(self.R[i], tm + 1, tr, l, r, ok)

    # the last index in [l, r] under node i whose value passes ok(node), or None: O(logU), since only one
    # node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    def _lastPass(self, i, tl, tr, l, r, ok):
        if r < tl or tr < l or not ok(i):
            return None
        if tl == tr:
            return tl
        self._push(i, tl, tr)
        self._kids(i)
        tm = (tl + tr) // 2
        res = self._lastPass(self.R[i], tm + 1, tr, l, r, ok)
        return res if res is not None else self._lastPass(self.L[i], tl, tm, l, r, ok)
