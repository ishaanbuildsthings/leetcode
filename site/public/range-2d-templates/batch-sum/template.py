# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/batch-sum/template.py
# @operations: pointAdd rectSum
# @data-structure-type: offline-sweep
# @input: batch
# @complexities:
#   pointAdd: log^2(N) amortized
#   rectSum: log^2(N) amortized
#   build: 1
# @memory:
#   layout: none
#   node: bit[1*N]
#   tags: none
#   other: events[5*N] ys[1*N] answers[1*N]
#   note: N = how many calls were recorded; a rectSum is stored as its four corners

from bisect import bisect_right
from operator import itemgetter


# Point add and rectangle sum over any coordinates, answered all at once: linear memory, O(N log^2 N) in total. Call
# pointAdd and rectSum in the order they happen (they are only recorded: rectSum returns which query it is, 0, 1, 2,
# ...), then solve() returns every answer, answers[i] for query i. Use it only when no call depends on an earlier
# answer. A rectangle sum is four corner sums (how much was added at x <= X and y <= Y before this moment). The calls
# are split in half by time, again and again: the adds of an earlier half count for the corners of the later half, and
# with both halves sorted by x that is one sweep with a Fenwick tree over y. Rectangles are inclusive, x1..x2 by
# y1..y2; coordinates are any integers.
class OfflineRectSum:
    __slots__ = ("events", "queries")

    # O(1) -- nothing recorded yet
    def __init__(self):
        self.events = []  # in call order: (x, y, v) for an add, (x1, y1, x2, y2, query number) for a sum
        self.queries = 0

    # O(1) now (O(log^2 N) amortized in solve) -- records: add v at (x, y)
    def pointAdd(self, x, y, v):
        self.events.append((x, y, v))

    # O(1) now (O(log^2 N) amortized in solve) -- records: sum of everything added so far at x1 <= x <= x2 and y1 <= y
    # <=
    # y2. Returns this query's number: its answer is solve()[that number]; needs x1 <= x2 and y1 <= y2, else IndexError
    def rectSum(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectSum: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        self.events.append((x1, y1, x2, y2, self.queries))
        self.queries += 1
        return self.queries - 1

    # O(N log^2 N) -- every rectSum's answer, in the order they were asked (can be called again after more calls)
    def solve(self):
        ys = sorted({e[1] for e in self.events if len(e) == 3})
        # one item per add, four per sum (its corners): (x, y as a count of distinct add-y's <= it, amount or sign,
        # query number or -1)
        items = []
        for e in self.events:
            if len(e) == 3:
                items.append((e[0], bisect_right(ys, e[1]), e[2], -1))
            else:
                x1, y1, x2, y2, q = e
                top = bisect_right(ys, y2)
                bot = bisect_right(ys, y1 - 1)
                items += [(x2, top, 1, q), (x1 - 1, top, -1, q), (x2, bot, -1, q), (x1 - 1, bot, 1, q)]
        answers = [0] * self.queries
        m = len(ys)
        bit = [0] * (m + 1)
        byX = itemgetter(0)
        n = len(items)
        width = 1
        # blocks of `width` items, each already sorted by x; neighbors are an earlier and a later stretch of time
        while width < n:
            for l in range(0, n - width, 2 * width):
                mid = l + width
                r = min(mid + width, n)
                i = l
                for j in range(mid, r):
                    x, y, sign, q = items[j]
                    if q < 0:
                        continue
                    while i < mid and items[i][0] <= x:  # the earlier adds at or left of this corner go into the tree
                        if items[i][3] < 0:
                            k = items[i][1]
                            amount = items[i][2]
                            while k <= m:
                                bit[k] += amount
                                k += k & -k
                        i += 1
                    total = 0
                    while y > 0:
                        total += bit[y]
                        y &= y - 1
                    answers[q] += sign * total
                for k2 in range(l, i):  # take them back out
                    if items[k2][3] < 0:
                        k = items[k2][1]
                        amount = items[k2][2]
                        while k <= m:
                            bit[k] -= amount
                            k += k & -k
                items[l:r] = sorted(items[l:r], key=byX)  # (stable, and both halves are sorted: a merge)
            width *= 2
        return answers
