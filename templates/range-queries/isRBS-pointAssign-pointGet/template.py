# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/isRBS-pointAssign-pointGet/template.py
# @operations: getAll isRBS pointAssign pointGet
# @data-structure-type: seg-tree
# @letters: same
# @complexities:
#   getAll: N
#   isRBS: log(N)
#   pointAssign: log(N)
#   pointGet: 1
#   build: N
# @memory:
#   layout: pow2-iterative
#   node: sm[4*N] mp[4*N]
#   tags: none
#   other: s[1*N]
#   note: one (sum, min prefix sum) pair per node over 2 * size slots (size = next power of two >= n); s: the characters

# Bracket sequence with point writes: isRBS(l, r) asks whether s[l..r] is a regular (balanced) bracket sequence.
# With open = +1 and anything else = -1, s[l..r] is regular iff its total is 0 and no prefix of it dips below 0. Each
# seg tree node keeps (sum, min prefix sum) of its range; two halves combine as
#   sum = L.sum + R.sum,   minPre = min(L.minPre, L.sum + R.minPre)
# and a query folds the covering nodes left to right. Iterative over 2 * size slots (size = next power of two >= n).
# All indices 0-based, ranges inclusive. The values are the characters themselves.


class BracketTree:
    __slots__ = ("n", "size", "openChar", "s", "sm", "mp")

    # O(N) -- brackets: the sequence, a list of characters like ["(", ")", "("] (a str like "()(" works too);
    # openChar: the character that opens ("(" unless you pass e.g. "["); every other character closes
    def __init__(self, brackets, openChar="("):
        self.s = s = list(brackets)
        self.openChar = openChar
        n = self.n = len(s)
        size = self.size = 1 << max(0, (n - 1).bit_length())
        sm = self.sm = [0] * (2 * size)  # sum of the node's +-1s
        mp = self.mp = [0] * (2 * size)  # its min prefix sum (0 for the empty prefix of padding)
        for i, ch in enumerate(s):
            v = 1 if ch == openChar else -1
            sm[size + i] = v
            mp[size + i] = v if v < 0 else 0
        for x in range(size - 1, 0, -1):
            l, r = 2 * x, 2 * x + 1
            sm[x] = sm[l] + sm[r]
            m = sm[l] + mp[r]
            mp[x] = mp[l] if mp[l] < m else m

    # O(N) -- the whole sequence
    def getAll(self):
        return self.s[:]

    # O(1) -- brackets[i]
    def pointGet(self, i):
        return self.s[i]

    # O(logN) -- brackets[i] = ch
    def pointAssign(self, i, ch):
        self.s[i] = ch
        sm, mp = self.sm, self.mp
        x = i + self.size
        v = 1 if ch == self.openChar else -1
        sm[x] = v
        mp[x] = v if v < 0 else 0
        x >>= 1
        while x:
            l, r = 2 * x, 2 * x + 1
            sm[x] = sm[l] + sm[r]
            m = sm[l] + mp[r]
            mp[x] = mp[l] if mp[l] < m else m
            x >>= 1

    # O(logN) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    def isRBS(self, l, r):
        sm, mp = self.sm, self.mp
        ls = lm = 0  # (sum, min prefix) of the left part folded so far
        rights = []  # the right side's nodes, folded in afterwards right to left
        l += self.size
        r += self.size + 1
        while l < r:
            if l & 1:
                m = ls + mp[l]
                if m < lm:
                    lm = m
                ls += sm[l]
                l += 1
            if r & 1:
                r -= 1
                rights.append(r)
            l >>= 1
            r >>= 1
        for x in reversed(rights):
            m = ls + mp[x]
            if m < lm:
                lm = m
            ls += sm[x]
        return ls == 0 and lm >= 0
