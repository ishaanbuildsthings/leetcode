# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/combinatorics/ModCalc.py

# calc = ModCalc()                  # mod 10**9 + 7
# calc = ModCalc(mod=998244353)     # your own mod (the ops marked "mod must be prime" need a prime)
# @if nChooseKWithMod
# calc.nChooseKWithMod(5, 2) -> 10
# @endif
# @if waysToPutIdenticalItemsIntoDistinctBucketsWithMod
# calc.waysToPutIdenticalItemsIntoDistinctBucketsWithMod(3, 2, allowEmptyBuckets=True)   -> 4
# calc.waysToPutIdenticalItemsIntoDistinctBucketsWithMod(3, 2, allowEmptyBuckets=False)  -> 2
# @endif
# No size to pick: the factorial tables grow on demand (doubling), so every call just works and later calls, or later
# test cases sharing one instance, reuse what's built. Growing costs O(largest x ever asked for) in total.


class ModCalc:
    # O(1) -- the ops that divide (marked "mod must be prime") get inverses from Fermat's little theorem
    def __init__(self, mod=10**9 + 7):
        self.mod = mod
        # @if getFactorialWithMod getInverseFactorialWithMod nChooseKWithMod nPermuteKWithMod interleaveTwoSequencesWithMod waysToPutIdenticalItemsIntoDistinctBucketsWithMod waysToPutDistinctItemsIntoDistinctBucketsWithMod
        self.fact = [1]  # fact[x] = x! % mod
        self.invFact = [1]  # invFact[x] = 1 / x! % mod (0 from x = mod on: no inverse there)
        # @endif

    # @if getFactorialWithMod getInverseFactorialWithMod nChooseKWithMod nPermuteKWithMod interleaveTwoSequencesWithMod waysToPutIdenticalItemsIntoDistinctBucketsWithMod waysToPutDistinctItemsIntoDistinctBucketsWithMod
    def _grow(self, x):
        # afterwards the tables cover 0..x (at least doubling, so each value is built once over the instance's life)
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

    # @endif
    # @if getFactorialWithMod
    # O(1) amortized -- x! % mod (0 once x >= mod)
    def getFactorialWithMod(self, x):
        if x >= self.mod:
            return 0
        self._grow(x)
        return self.fact[x]

    # @endif
    # @if getInverseFactorialWithMod
    # O(1) amortized -- 1 / x! % mod; needs x < mod (x! has no inverse after that); mod must be prime
    def getInverseFactorialWithMod(self, x):
        if x >= self.mod:
            raise ValueError(f"getInverseFactorialWithMod: {x}! has no inverse mod {self.mod}")
        self._grow(x)
        return self.invFact[x]

    # @endif
    # @if nChooseKWithMod interleaveTwoSequencesWithMod waysToPutIdenticalItemsIntoDistinctBucketsWithMod waysToPutDistinctItemsIntoDistinctBucketsWithMod
    # O(1) amortized (O(log n) once n >= mod: Lucas) -- ways to choose k of n distinct items, order ignored;
    # 0 if k < 0 or k > n; mod must be prime
    def nChooseKWithMod(self, n, k):
        if k < 0 or k > n:
            return 0
        if n >= self.mod:
            return self.nChooseKWithMod(n % self.mod, k % self.mod) * self.nChooseKWithMod(n // self.mod,
                k // self.mod) % self.mod
        self._grow(n)
        return self.fact[n] * self.invFact[k] % self.mod * self.invFact[n - k] % self.mod

    # @endif
    # @if nPermuteKWithMod
    # O(1) amortized -- ways to choose k of n distinct items in order; 0 if k < 0 or k > n; mod must be prime
    def nPermuteKWithMod(self, n, k):
        if k < 0 or k > n:
            return 0
        if n >= self.mod:
            # k consecutive numbers: 0 if one is a multiple of mod, else the same as starting from n % mod
            if k > n % self.mod:
                return 0
            n %= self.mod
        self._grow(n)
        return self.fact[n] * self.invFact[n - k] % self.mod

    # @endif
    # @if interleaveTwoSequencesWithMod
    # O(1) amortized -- ways to interleave a sequence of length1 items with one of length2, keeping each one's order;
    # mod must be prime
    def interleaveTwoSequencesWithMod(self, length1, length2):
        return self.nChooseKWithMod(length1 + length2, length1)

    # @endif
    # @if waysToPutIdenticalItemsIntoDistinctBucketsWithMod
    # O(1) amortized -- identical items into distinct buckets (stars and bars); allowEmptyBuckets (required, no
    # default): may a bucket stay empty; mod must be prime
    def waysToPutIdenticalItemsIntoDistinctBucketsWithMod(self, items, buckets, allowEmptyBuckets: bool):
        if buckets == 0:
            return 1 % self.mod if items == 0 else 0
        if allowEmptyBuckets:
            return self.nChooseKWithMod(items + buckets - 1, buckets - 1)
        return self.nChooseKWithMod(items - 1, buckets - 1)

    # @endif
    # @if waysToPutDistinctItemsIntoDistinctBucketsWithMod
    # O(log items) with allowEmptyBuckets, else O(buckets * log items) -- distinct items into distinct buckets;
    # allowEmptyBuckets (required, no default): may a bucket stay empty (then it's buckets^items and works for any mod;
    # otherwise mod must be prime)
    def waysToPutDistinctItemsIntoDistinctBucketsWithMod(self, items, buckets, allowEmptyBuckets: bool):
        if allowEmptyBuckets:
            return pow(buckets, items, self.mod)
        total = 0  # inclusion-exclusion over the buckets left empty
        for empty in range(buckets + 1):
            term = self.nChooseKWithMod(buckets, empty) * pow(buckets - empty, items, self.mod) % self.mod
            total += -term if empty % 2 else term
        return total % self.mod

    # @endif
    # @if modPow
    # O(log exponent) -- base^exponent % mod; works for any mod
    def modPow(self, base, exponent):
        return pow(base, exponent, self.mod)

    # @endif
    # @if modInv
    # O(log mod) -- 1 / x % mod; x must not be a multiple of mod; mod must be prime
    def modInv(self, x):
        if x % self.mod == 0:
            raise ValueError(f"modInv: {x} has no inverse mod {self.mod}")
        return pow(x, self.mod - 2, self.mod)
    # @endif
