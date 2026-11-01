# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/isRBS-pointGet/template.py
# @operations: isRBS pointGet
# @data-structure-type: sparse-table
# @letters: same
# @complexities:
#   isRBS: 1
#   pointGet: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: table[1*N*log(N)]
#   tags: none
#   other: P[1*N] s[1*N]
#   note: P: prefix sums; the table holds P's minimums over every power-of-two window

# Static bracket sequence: isRBS(l, r) asks whether s[l..r] is a regular (balanced) bracket sequence, in O(1).
# With open = +1 and anything else = -1, s[l..r] is regular iff its total is 0 and no prefix of it dips below 0. With
# prefix sums P (P[0] = 0, P[i + 1] = P[i] + s[i]) that is P[r + 1] == P[l] and min(P[l + 1..r + 1]) >= P[l]: a sparse
# table answers the min in O(1). All indices 0-based, ranges inclusive. The values are the characters themselves.


class StaticBrackets:
    # O(N log N) -- brackets: the sequence, a list of characters like ["(", ")", "("] (a str like "()(" works too);
    # openChar: the character that opens ("(" unless you pass e.g. "["); every other character closes
    def __init__(self, brackets, openChar="("):
        self.s = s = list(brackets)
        n = len(s)
        P = [0] * (n + 1)
        for i, ch in enumerate(s):
            P[i + 1] = P[i] + (1 if ch == openChar else -1)
        self.P = P
        self.table = [P]  # table[k][i] = min(P[i .. i + 2^k - 1])
        k = 1
        while 2 * k <= n + 1:
            prev = self.table[-1]
            self.table.append([a if a < b else b for a, b in zip(prev, prev[k:])])
            k *= 2

    # O(1) -- brackets[i]
    def pointGet(self, i):
        return self.s[i]

    # O(1) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    def isRBS(self, l, r):
        P = self.P
        if P[r + 1] != P[l]:
            return False
        lo, hi = l + 1, r + 1
        k = (hi - lo + 1).bit_length() - 1
        row = self.table[k]
        a, b = row[lo], row[hi - (1 << k) + 1]
        return (a if a < b else b) >= P[l]
