# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/next-free/template.py
# @operations: isFree nextFree prevFree take takeRange
# @data-structure-type: next-free
# @complexities:
#   isFree: α(N) amortized
#   nextFree: α(N) amortized
#   prevFree: α(N) amortized
#   take: α(N) amortized
#   takeRange: α(N) amortized
#   build: N
# @memory:
#   layout: none
#   node: nxt[1*N] prv[1*N]
#   tags: none
#   other: none
#   note: takeRange costs α(N) amortized per index it takes, so O(N α(N)) over every call together

# nf = NextFree(n)
# Indices 0..n-1 start free; take(i) / takeRange(l, r) use them up, and nextFree / prevFree jump straight to the
# nearest index still free (painting intervals, "assign each query to the first unused slot", ...)


class NextFree:
    # O(n), every index 0..n-1 starts free
    def __init__(self, n):
        self.n = n
        self.nxt = list(range(n + 1))  # follow nxt to the first free index >= i (n: none)
        self.prv = list(range(n + 1))  # follow prv to (the last free index <= i - 1) + 1, shifted so 0 means none

    def _up(self, i):
        nxt = self.nxt
        while nxt[i] != i:
            nxt[i] = nxt[nxt[i]]
            i = nxt[i]
        return i

    def _down(self, i):
        prv = self.prv
        while prv[i] != i:
            prv[i] = prv[prv[i]]
            i = prv[i]
        return i

    # O(α(n)) amortized, the smallest free index >= i, n if there's none; needs 0 <= i <= n, else IndexError
    def nextFree(self, i):
        if not 0 <= i <= self.n:
            raise IndexError(f"nextFree: needs 0 <= i <= n, got i = {i}, n = {self.n}")
        return self._up(i)

    # O(α(n)) amortized, the largest free index <= i, -1 if there's none; needs -1 <= i < n, else IndexError
    def prevFree(self, i):
        if not -1 <= i < self.n:
            raise IndexError(f"prevFree: needs -1 <= i < n, got i = {i}, n = {self.n}")
        return self._down(i + 1) - 1

    # O(α(n)) amortized, True if i hasn't been taken; needs 0 <= i < n, else IndexError
    def isFree(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"isFree: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self._up(i) == i

    # O(α(n)) amortized, uses up index i (nothing if it was already taken); needs 0 <= i < n, else IndexError
    def take(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"take: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if self._up(i) == i:
            self.nxt[i] = i + 1
            self.prv[i + 1] = i

    # O((how many were free) * α(n)) amortized, so O(n α(n)) over every call: uses up every free index in l..r and
    # returns them in order; needs 0 <= l <= r < n, else IndexError
    def takeRange(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"takeRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        res = []
        i = self._up(l)
        while i <= r:
            res.append(i)
            self.nxt[i] = i + 1
            self.prv[i + 1] = i
            i = self._up(i + 1)
        return res
