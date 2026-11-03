# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/isRBS-pointAssign-pointGet-rangeFlip/template.py
# @operations: getAll isRBS pointAssign pointGet rangeFlip
# @data-structure-type: lazy-seg-tree
# @letters: same
# @complexities:
#   getAll: N
#   isRBS: log(N)
#   pointAssign: log(N)
#   pointGet: log(N)
#   rangeFlip: log(N)
#   build: N
# @memory:
#   layout: 4n-recursive
#   node: sm[4*N] mn[4*N] mx[4*N]
#   tags: flp[4*N]
#   other: none
#   note: the characters aren't stored: a node's +-1s say them

# Bracket sequence with RANGE FLIP (every open becomes a close and vice versa): isRBS(l, r) asks whether s[l..r] is a
# regular (balanced) bracket sequence. With open = +1 and close = -1, s[l..r] is regular iff its total is 0 and no
# prefix of it dips below 0. Each node keeps (sum, min prefix sum, max prefix sum) of its range, prefixes including
# the empty one; two halves combine as sum = L.sum + R.sum, minPre = min(L.minPre, L.sum + R.minPre), maxPre likewise.
# A flip negates every value: sum -> -sum, and min / max prefix swap and change sign. Recursive lazy tree over 4N
# slots; the characters themselves are not stored (a +1 reads back as openChar, a -1 as closeChar). All indices
# 0-based, ranges inclusive.


class LazyBracketTree:
    __slots__ = ('n', 'oc', 'cc', 'sm', 'mn', 'mx', 'flp')

    # O(N) -- brackets: the sequence, a list of characters like ["(", ")", "("] (a str like "()(" works too);
    # openChar / closeChar: the characters that open / close ("(" / ")" unless you pass e.g. "[" / "]"); a character
    # that isn't openChar counts as (and reads back as) closeChar
    def __init__(self, brackets, openChar="(", closeChar=")"):
        s = list(brackets)
        n = self.n = len(s)
        self.oc, self.cc = openChar, closeChar
        size = 4 * max(1, n)
        self.sm = [0] * size  # sum of the node's +-1s
        self.mn = [0] * size  # its min prefix sum (the empty prefix counts: <= 0)
        self.mx = [0] * size  # its max prefix sum (>= 0)
        self.flp = [0] * size  # pending flip
        if n:
            self._build(1, 0, n - 1, s)

    # O(N) -- the whole sequence, as characters
    def getAll(self):
        out = []
        if self.n:
            self._collect(1, 0, self.n - 1, out)
        return out

    # O(logN) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?; needs
    # 0 <= l <= r < n, else IndexError
    def isRBS(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"isRBS: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        s, m = self._fold(1, 0, self.n - 1, l, r, 0, 0)
        return s == 0 and m >= 0

    # O(logN) -- brackets[i] = ch; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, ch):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self._set(1, 0, self.n - 1, i, 1 if ch == self.oc else -1)

    # O(logN) -- brackets[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        x, lo, hi = 1, 0, self.n - 1
        while lo < hi:
            mid = (lo + hi) // 2
            self._push(x, lo, mid, hi)
            if i <= mid:
                x, hi = 2 * x, mid
            else:
                x, lo = 2 * x + 1, mid + 1
        return self.oc if self.sm[x] > 0 else self.cc

    # O(logN) -- every open in brackets[l..r] becomes a close and vice versa; needs 0 <= l <= r < n, else IndexError
    def rangeFlip(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeFlip: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(1, 0, self.n - 1, l, r, 0)

    # ---- internals ----

    def _build(self, x, lo, hi, s):
        if lo == hi:
            v = 1 if s[lo] == self.oc else -1
            self.sm[x] = v
            self.mn[x] = v if v < 0 else 0
            self.mx[x] = v if v > 0 else 0
            return
        mid = (lo + hi) // 2
        self._build(2 * x, lo, mid, s)
        self._build(2 * x + 1, mid + 1, hi, s)
        self._pull(x)

    def _pull(self, x):
        sm, mn = self.sm, self.mn
        l, r = 2 * x, 2 * x + 1
        sm[x] = sm[l] + sm[r]
        m = sm[l] + mn[r]
        mn[x] = mn[l] if mn[l] < m else m
        mx = self.mx
        m = sm[l] + mx[r]
        mx[x] = mx[l] if mx[l] > m else m

    def _flip(self, x):  # every value of node x negated
        self.sm[x] = -self.sm[x]
        self.mn[x], self.mx[x] = -self.mx[x], -self.mn[x]
        self.flp[x] ^= 1

    def _push(self, x, lo, mid, hi):  # hand x's pending tags to its children
        if self.flp[x]:  # (after the assign: assign, then flip)
            self._flip(2 * x)
            self._flip(2 * x + 1)
            self.flp[x] = 0

    def _update(self, x, lo, hi, l, r, v):  # v: assign +-1, or 0 for a flip
        if l <= lo and hi <= r:
            self._flip(x)
            return
        mid = (lo + hi) // 2
        self._push(x, lo, mid, hi)
        if l <= mid:
            self._update(2 * x, lo, mid, l, r, v)
        if r > mid:
            self._update(2 * x + 1, mid + 1, hi, l, r, v)
        self._pull(x)

    def _set(self, x, lo, hi, i, v):
        if lo == hi:
            self.sm[x] = v
            self.mn[x] = v if v < 0 else 0
            self.mx[x] = v if v > 0 else 0
            return
        mid = (lo + hi) // 2
        self._push(x, lo, mid, hi)
        if i <= mid:
            self._set(2 * x, lo, mid, i, v)
        else:
            self._set(2 * x + 1, mid + 1, hi, i, v)
        self._pull(x)

    # (s, m): sum and min prefix of everything left of this part; returns them with this part folded in
    def _fold(self, x, lo, hi, l, r, s, m):
        if l <= lo and hi <= r:
            t = s + self.mn[x]
            return s + self.sm[x], (t if t < m else m)
        mid = (lo + hi) // 2
        self._push(x, lo, mid, hi)
        if l <= mid:
            s, m = self._fold(2 * x, lo, mid, l, r, s, m)
        if r > mid:
            s, m = self._fold(2 * x + 1, mid + 1, hi, l, r, s, m)
        return s, m

    def _collect(self, x, lo, hi, out):
        if lo == hi:
            out.append(self.oc if self.sm[x] > 0 else self.cc)
            return
        mid = (lo + hi) // 2
        self._push(x, lo, mid, hi)
        self._collect(2 * x, lo, mid, out)
        self._collect(2 * x + 1, mid + 1, hi, out)
