# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/combinatorics/Stirling.py

# Distinct items into buckets (Stirling numbers of the second kind):
# @if formulaIdentical formulaDistinct
#   StirlingByFormula: every call costs O(buckets * log items). Best for a few calls, or huge item counts. mod must be
#                      prime. Grows lazily, but only a little: a factorial list up to the largest buckets you call
#                      with, already inside each call's cost.
# @endif
# @if tableIdentical tableDistinct
#   StirlingByTable:   GROWS LAZILY. The constructor builds nothing; the table grows inside the calls you make, to
#                      the largest items and buckets you ask for (each side doubles when it grows). Over all calls
#                      that costs O(largest items * largest buckets) in total, and that much memory; a call the table
#                      already covers is O(1). Best for many calls. Works for any mod.
# @endif
# @if formulaIdentical formulaDistinct
# calc = StirlingByFormula()                  # mod 10**9 + 7
# calc = StirlingByFormula(mod=998244353)     # your own mod (must be prime here)
# @endif
# @if tableIdentical tableDistinct
# calc = StirlingByTable()                    # mod 10**9 + 7
# calc = StirlingByTable(mod=1000)            # your own mod (any mod)
# @endif
# @if formulaIdentical tableIdentical
# calc.waysToPutDistinctItemsIntoIdenticalBucketsWithMod(3, 2, allowEmptyBuckets=False) -> 3   {a}{bc}, {b}{ac}, {c}{ab}
# calc.waysToPutDistinctItemsIntoIdenticalBucketsWithMod(3, 2, allowEmptyBuckets=True)  -> 4   those 3, plus {abc}{}
# @endif
# @if formulaDistinct tableDistinct
# calc.waysToPutDistinctItemsIntoDistinctBucketsWithMod(3, 2, allowEmptyBuckets=False)  -> 6   3 times 2 bucket orders
# calc.waysToPutDistinctItemsIntoDistinctBucketsWithMod(3, 2, allowEmptyBuckets=True)   -> 8   2^3
# @endif


# @if formulaIdentical formulaDistinct
class StirlingByFormula:
    # O(1) -- builds nothing yet (the factorial list grows lazily inside the calls); mod must be prime
    def __init__(self, mod=10**9 + 7):
        self.mod = mod
        self.fact = [1]
        self.invFact = [1]

    def _grow(self, x):
        # factorial tables cover 0..x afterwards (doubling)
        old = len(self.fact)
        if x < old:
            return
        size = max(x + 1, 2 * old)
        mod, fact, invFact = self.mod, self.fact, self.invFact
        for i in range(old, size):
            fact.append(fact[-1] * i % mod)
        invFact.extend([0] * (size - old))
        top = min(size - 1, mod - 1)
        if top >= old:
            invFact[top] = pow(fact[top], mod - 2, mod)
            for i in range(top, old, -1):
                invFact[i - 1] = invFact[i] * i % mod

    def _onto(self, items, buckets):
        # distinct items into distinct buckets, none empty: inclusion-exclusion over the buckets left empty
        self._grow(buckets)
        mod, fact, invFact = self.mod, self.fact, self.invFact
        total = 0
        for empty in range(buckets + 1):
            choose = fact[buckets] * invFact[empty] % mod * invFact[buckets - empty] % mod
            term = choose * pow(buckets - empty, items, mod) % mod
            total += -term if empty % 2 else term
        return total % mod

    # @if formulaIdentical
    # O(buckets * log items) per call -- distinct items into identical buckets; allowEmptyBuckets (required, no
    # default): may a bucket stay empty; needs buckets < mod
    def waysToPutDistinctItemsIntoIdenticalBucketsWithMod(self, items, buckets, allowEmptyBuckets: bool):
        if not allowEmptyBuckets:
            return self._onto(items, buckets) * self.invFact[buckets] % self.mod
        # sum over how many buckets get used: sum of i^items / i! * (alternating sum of 1/t! for t <= buckets - i)
        self._grow(buckets)
        mod, invFact = self.mod, self.invFact
        alt = [0] * (buckets + 1)
        running = 0
        for t in range(buckets + 1):
            running = (running + (-invFact[t] if t % 2 else invFact[t])) % mod
            alt[t] = running
        return sum(pow(i, items, mod) * invFact[i] % mod * alt[buckets - i] for i in range(buckets + 1)) % mod

    # @endif
    # @if formulaDistinct
    # O(buckets * log items) per call (O(log items) with allowEmptyBuckets) -- distinct items into distinct buckets;
    # allowEmptyBuckets (required, no default): may a bucket stay empty; needs buckets < mod
    def waysToPutDistinctItemsIntoDistinctBucketsWithMod(self, items, buckets, allowEmptyBuckets: bool):
        if allowEmptyBuckets:
            return pow(buckets, items, self.mod)
        return self._onto(items, buckets)
    # @endif


# @endif
# @if tableIdentical tableDistinct
class StirlingByTable:
    # O(1) -- builds nothing yet: the table grows lazily inside the calls below; any mod
    def __init__(self, mod=10**9 + 7):
        self.mod = mod
        self.table = [[1 % mod]]  # table[i][j] = ways to put i distinct items into j identical non-empty buckets
        self.prefix = [[1 % mod]]  # prefix[i][j] = table[i][0] + ... + table[i][j]: up to j buckets used
        self.fact = [1 % mod]  # fact[j] = j! % mod, the orderings of j distinct buckets

    def _grow(self, items, buckets):
        # afterwards the table covers items x buckets; each side at least doubles when it grows, so it's rebuilt
        # O(log) times and the total cost stays O(final items * final buckets)
        rows, cols = len(self.table), len(self.table[0])
        if items < rows and buckets < cols:
            return
        rows = max(items + 1, 2 * rows) if items >= rows else rows
        cols = max(buckets + 1, 2 * cols) if buckets >= cols else cols
        mod = self.mod
        table = [[0] * cols for _ in range(rows)]
        table[0][0] = 1 % mod
        for i in range(1, rows):
            prev, row = table[i - 1], table[i]
            for j in range(1, cols):
                row[j] = (prev[j - 1] + j * prev[j]) % mod
        self.table = table
        self.prefix = []
        for row in table:
            run, acc = [], 0
            for x in row:
                acc = (acc + x) % mod
                run.append(acc)
            self.prefix.append(run)
        fact = self.fact
        while len(fact) < cols:
            fact.append(fact[-1] * len(fact) % mod)

    # @if tableIdentical
    # O(1) amortized; lazily grows the table when called with bigger items or bigger buckets than before (see the
    # top) -- distinct items into identical buckets; allowEmptyBuckets (required, no default): may a bucket stay empty
    def waysToPutDistinctItemsIntoIdenticalBucketsWithMod(self, items, buckets, allowEmptyBuckets: bool):
        self._grow(items, buckets)
        return self.prefix[items][buckets] if allowEmptyBuckets else self.table[items][buckets]

    # @endif
    # @if tableDistinct
    # O(1) amortized; lazily grows the table when called with bigger items or bigger buckets than before (see the
    # top). O(log items) with allowEmptyBuckets, which never touches the table -- distinct items into distinct buckets;
    # allowEmptyBuckets (required, no default): may a bucket stay empty
    def waysToPutDistinctItemsIntoDistinctBucketsWithMod(self, items, buckets, allowEmptyBuckets: bool):
        if allowEmptyBuckets:
            return pow(buckets, items, self.mod)
        self._grow(items, buckets)
        return self.table[items][buckets] * self.fact[buckets] % self.mod
    # @endif
# @endif
