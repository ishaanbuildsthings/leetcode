# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/XorBasis.py

# XorBasis: every value you can make by XORing together some subset of the inserted values (a linear basis over bits).
# The empty subset counts, so 0 can always be made. Inserted values must be >= 0.
# B = number of bits in the largest value inserted, N = number of values inserted.
#
# basis = XorBasis()             # nothing inserted yet
# basis = XorBasis([3, 10, 5])   # inserts 3, 10, 5
#
# Max subset XOR:                 XorBasis(arr).maxXor()
# Number of distinct subset XORs: XorBasis(arr).countDistinctXors()
# Subsets whose XOR is exactly k: XorBasis(arr).countSubsetsMakingMod(k, 10**9 + 7)
class XorBasis:
    # O(N * B)
    def __init__(self, arr=()):
        # pivots[b] = the basis value whose highest set bit is b, or 0 if none. Kept fully reduced: bit b is set in no
        # other basis value, which is what makes kthSmallestXor work
        self.pivots = []
        self.numInserted = 0
        self.numPivots = 0
        for x in arr:
            self.insert(x)

    # inserts x; returns True if x couldn't be made before (the basis grew), else False
    # O(B)
    def insert(self, x):
        if x < 0:
            raise ValueError(f"XorBasis.insert: {x} is negative")
        self.numInserted += 1
        pivots = self.pivots
        for b in range(min(x.bit_length(), len(pivots)) - 1, -1, -1):
            if (x >> b) & 1 and pivots[b]:
                x ^= pivots[b]
        if x == 0:
            return False
        top = x.bit_length() - 1
        if top >= len(pivots):
            pivots.extend([0] * (top + 1 - len(pivots)))
        for b in range(top + 1, len(pivots)):
            if (pivots[b] >> top) & 1:
                pivots[b] ^= x
        pivots[top] = x
        self.numPivots += 1
        return True

    # True if some subset XORs to exactly x (x = 0 is always True: the empty subset)
    # O(B)
    def canMake(self, x):
        return x >= 0 and self.minXorWith(x) == 0

    # largest XOR of any subset (0 if nothing inserted)
    # XorBasis([3, 10, 5]).maxXor() -> 15   # 10 ^ 5
    # O(B)
    def maxXor(self):
        return self.maxXorWith(0)

    # largest x ^ (XOR of some subset)
    # XorBasis([3, 10, 5]).maxXorWith(4) -> 14   # 4 ^ 10
    # O(B)
    def maxXorWith(self, x):
        if x < 0:
            raise ValueError(f"XorBasis.maxXorWith: {x} is negative")
        pivots = self.pivots
        for b in range(len(pivots) - 1, -1, -1):
            if pivots[b] and not (x >> b) & 1:
                x ^= pivots[b]
        return x

    # smallest x ^ (XOR of some subset)
    # XorBasis([3, 10, 5]).minXorWith(15) -> 0   # 15 = 10 ^ 5
    # O(B)
    def minXorWith(self, x):
        if x < 0:
            raise ValueError(f"XorBasis.minXorWith: {x} is negative")
        pivots = self.pivots
        for b in range(len(pivots) - 1, -1, -1):
            if pivots[b] and (x >> b) & 1:
                x ^= pivots[b]
        return x

    # smallest XOR of a non-empty subset: 0 if some non-empty subset XORs to 0, None if nothing inserted
    # XorBasis([3, 10, 5]).minNonzeroXor() -> 3
    # XorBasis([3, 5, 6]).minNonzeroXor() -> 0   # 3 ^ 5 ^ 6 = 0
    # O(B)
    def minNonzeroXor(self):
        if self.numInserted > self.numPivots:
            return 0
        for p in self.pivots:
            if p:
                return p
        return None

    # the kth smallest distinct value some subset makes, k 0-indexed (k = 0 -> 0, the empty subset), or None if
    # k >= countDistinctXors()
    # XorBasis([1, 2]).kthSmallestXor(3) -> 3   # the makeable values are 0, 1, 2, 3
    # O(B)
    def kthSmallestXor(self, k):
        if k < 0:
            raise ValueError(f"XorBasis.kthSmallestXor: k = {k} is negative")
        if k >> self.numPivots:
            return None
        res = 0
        i = 0
        for p in self.pivots:
            if p:
                if (k >> i) & 1:
                    res ^= p
                i += 1
        return res

    # number of distinct values the subsets make, counting 0 from the empty subset: 2^rank
    # XorBasis([3, 5, 6]).countDistinctXors() -> 4   # 0, 3, 5, 6
    # O(1)
    def countDistinctXors(self):
        return 1 << self.numPivots

    # number of subsets of the inserted values (by position, the empty one included) whose XOR is exactly x, mod mod:
    # 2^(N - rank) if x can be made, else 0
    # XorBasis([3, 5, 6]).countSubsetsMakingMod(0, 10**9 + 7) -> 2   # {} and {3, 5, 6}
    # O(B + log(N))
    def countSubsetsMakingMod(self, x, mod):
        return pow(2, self.numInserted - self.numPivots, mod) if self.canMake(x) else 0

    # size of the basis (how many inserted values were independent)
    # O(1)
    def rank(self):
        return self.numPivots

    # how many values were inserted, including ones that didn't grow the basis
    # O(1)
    def size(self):
        return self.numInserted

    # the basis values, largest first (rank of them; their subset XORs make exactly the makeable values)
    # O(B)
    def basis(self):
        return [p for p in reversed(self.pivots) if p]

    # inserts everything other holds, as if other's values had been inserted here (size grows by other.size())
    # O(B^2)
    def merge(self, other):
        for p in other.basis():
            self.insert(p)
        self.numInserted += other.numInserted - other.numPivots
