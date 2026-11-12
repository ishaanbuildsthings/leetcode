# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/agg-deque-gcd-lcm-product-mod/template.py
# @operations: append appendLeft gcdAll getAll lcmAll pointGet pop popLeft productAllMod size sumAll xorAll
# @data-structure-type: agg-deque
# @complexities:
#   append: log(U)
#   appendLeft: log(U)
#   gcdAll: log(U)
#   getAll: N
#   lcmAll: log(U)
#   pointGet: 1
#   pop: log(U) amortized
#   popLeft: log(U) amortized
#   productAllMod: 1
#   size: 1
#   sumAll: 1
#   xorAll: 1
#   build: N
# @memory:
#   layout: none
#   node: front[1*N] back[1*N] Fg[1*N] Bg[1*N] Flc[1*N] Blc[1*N] Fpr[1*N] Bpr[1*N]
#   tags: none
#   other: none
#   note: the front half (stored last to first) and the back half hold the window; each half also keeps the gcd, LCM, product % MOD of its bottom..top, so the whole window's is one combine of the two tops; a pop that empties a half moves half of the other over and rebuilds both (amortized O(1)); the sum and xor are running totals
# Aggregate deque (two stacks): a window that grows and shrinks at both ends (sliding windows, deques) with the gcd,
# LCM, product % MOD, sum and xor of the whole window in O(1). Each half is a stack that keeps the aggregates of its
# bottom..top, so a push or pop is O(1) and the whole window is one combine of the two tops; a pop that empties its
# half moves half of the other over and rebuilds both, amortized O(1). The sum and xor are running totals. No point
# assign or range query: for those, use a seg tree or treap. All indices 0-based. A gcd or LCM is a Euclid run, O(log
# U), so a push and gcdAll / lcmAll cost that. lcmAll answers -1 once the LCM passes cap, so it can't overflow. cap
# defaults to 2**63 - 1; pass your own after arr and mod, e.g. AggDequeGcdLcmProductMod(arr, 1000000007, cap=10**9).
# Removing values is safe: each half keeps the LCM (or -1) of every prefix of its stack, so once the values that
# pushed it past cap are popped, lcmAll is exact again. The product is kept % MOD (pass mod to the constructor).
from math import gcd


class AggDequeGcdLcmProductMod:
    __slots__ = ("front", "back", "sm", "xr", "mod", "cap", "Fg", "Bg", "Flc", "Blc", "Fpr", "Bpr")

    # O(N) -- arr: the initial array (a list), or left out to start empty; mod: for the product; cap: lcmAll is -1 past
    # it
    def __init__(self, arr=(), mod=10**9 + 7, cap=2**63 - 1):
        self.front, self.back = [], []  # front: the first values, stored last to first
        self.sm = self.xr = 0
        self.mod = mod
        self.cap = cap
        self.Fg, self.Bg = [], []  # Fg[j]: over front[0..j]; Bg[k]: over back[0..k]
        self.Flc, self.Blc = [], []  # Flc[j]: over front[0..j]; Blc[k]: over back[0..k]
        self.Fpr, self.Bpr = [], []  # Fpr[j]: over front[0..j]; Bpr[k]: over back[0..k]
        for v in arr:
            self.append(v)

    # O(1) -- the current length of the window
    def size(self):
        return len(self.front) + len(self.back)

    # O(N) -- the whole window as a list
    def getAll(self):
        return self.front[::-1] + self.back

    # O(1) -- a[i]; needs 0 <= i < size(), else raises IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        f = len(self.front)
        return self.front[f - 1 - i] if i < f else self.back[i - f]

    # O(log U) -- append v at the right end
    def append(self, v):
        self.sm += v
        self.xr ^= v
        S = self.Bg
        if S:
            a, b = S[-1], abs(v)
            S.append(gcd(a, b))
        else:
            S.append(abs(v))
        S = self.Blc
        if S:
            a, b = S[-1], self._lcmOne(v)
            S.append(self._lcm(a, b))
        else:
            S.append(self._lcmOne(v))
        S = self.Bpr
        if S:
            a, b = S[-1], v % self.mod
            S.append(a * b % self.mod)
        else:
            S.append(v % self.mod)
        self.back.append(v)

    # O(log U) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    def appendLeft(self, v):
        self.sm += v
        self.xr ^= v
        S = self.Fg
        if S:
            a, b = S[-1], abs(v)
            S.append(gcd(a, b))
        else:
            S.append(abs(v))
        S = self.Flc
        if S:
            a, b = S[-1], self._lcmOne(v)
            S.append(self._lcm(a, b))
        else:
            S.append(self._lcmOne(v))
        S = self.Fpr
        if S:
            a, b = S[-1], v % self.mod
            S.append(a * b % self.mod)
        else:
            S.append(v % self.mod)
        self.front.append(v)

    # O(log U) amortized -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        if self.size() < 1:
            raise IndexError("pop: needs size() >= 1")
        if not self.back:
            self._moveToBack()
        self.Bg.pop()
        self.Blc.pop()
        self.Bpr.pop()
        v = self.back.pop()
        self.sm -= v
        self.xr ^= v
        return v

    # O(log U) amortized -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises
    # IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        if not self.front:
            self._moveToFront()
        self.Fg.pop()
        self.Flc.pop()
        self.Fpr.pop()
        v = self.front.pop()
        self.sm -= v
        self.xr ^= v
        return v

    # O(1) -- a[0] + ... + a[n-1]; needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.size() < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.sm

    # O(1) -- xor of the whole window; needs n >= 1, else raises IndexError
    def xorAll(self):
        if self.size() < 1:
            raise IndexError("xorAll: needs n >= 1")
        return self.xr

    # O(log U) -- gcd of the whole window (one combine of the two halves' tops); needs n >= 1, else raises IndexError
    def gcdAll(self):
        if self.size() < 1:
            raise IndexError("gcdAll: needs n >= 1")
        F, B = self.Fg, self.Bg
        if not F:
            return B[-1]
        if not B:
            return F[-1]
        a, b = F[-1], B[-1]
        return gcd(a, b)

    # O(log U) -- LCM of the whole window (one combine of the two halves' tops) or -1 once it passes cap; needs n >= 1,
    # else raises IndexError
    def lcmAll(self):
        if self.size() < 1:
            raise IndexError("lcmAll: needs n >= 1")
        F, B = self.Flc, self.Blc
        if not F:
            return B[-1]
        if not B:
            return F[-1]
        a, b = F[-1], B[-1]
        return self._lcm(a, b)

    # O(1) -- product % MOD of the whole window (one combine of the two halves' tops); needs n >= 1, else raises
    # IndexError
    def productAllMod(self):
        if self.size() < 1:
            raise IndexError("productAllMod: needs n >= 1")
        F, B = self.Fpr, self.Bpr
        if not F:
            return B[-1]
        if not B:
            return F[-1]
        a, b = F[-1], B[-1]
        return a * b % self.mod

    # ---- internals ----

    def _moveToFront(self):  # the back half's first half becomes the front (the front is empty)
        k = (len(self.back) + 1) // 2
        self.front = self.back[:k][::-1]
        self.back = self.back[k:]
        self._rebuild()

    def _moveToBack(self):  # the front half's values nearest the middle (stored first) become the back
        k = (len(self.front) + 1) // 2
        self.back = self.front[:k][::-1]
        self.front = self.front[k:]
        self._rebuild()

    def _rebuild(self):  # every half's aggregates, O(size())
        S = []
        for v in self.front:
            if S:
                a, b = S[-1], abs(v)
                S.append(gcd(a, b))
            else:
                S.append(abs(v))
        self.Fg = S
        S = []
        for v in self.back:
            if S:
                a, b = S[-1], abs(v)
                S.append(gcd(a, b))
            else:
                S.append(abs(v))
        self.Bg = S
        S = []
        for v in self.front:
            if S:
                a, b = S[-1], self._lcmOne(v)
                S.append(self._lcm(a, b))
            else:
                S.append(self._lcmOne(v))
        self.Flc = S
        S = []
        for v in self.back:
            if S:
                a, b = S[-1], self._lcmOne(v)
                S.append(self._lcm(a, b))
            else:
                S.append(self._lcmOne(v))
        self.Blc = S
        S = []
        for v in self.front:
            if S:
                a, b = S[-1], v % self.mod
                S.append(a * b % self.mod)
            else:
                S.append(v % self.mod)
        self.Fpr = S
        S = []
        for v in self.back:
            if S:
                a, b = S[-1], v % self.mod
                S.append(a * b % self.mod)
            else:
                S.append(v % self.mod)
        self.Bpr = S

    def _lcmOne(self, v):  # |v|, or -1 past cap
        v = abs(v)
        return v if v <= self.cap else -1

    def _lcm(self, a, b):  # 0 if either is 0 (an LCM with a 0 is 0); else -1 if either is past cap or the LCM is
        if a == 0 or b == 0:
            return 0
        if a < 0 or b < 0:
            return -1
        r = a // gcd(a, b) * b
        return r if r <= self.cap else -1
