# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/XorBasis.py

# XorBasis: every value you can make by XORing together some subset of the inserted values (a linear basis over bits).
# The empty subset counts, so 0 can always be made. Inserted values must be >= 0.
# B = number of bits in the largest value inserted, N = number of values inserted.
#
# basis = XorBasis()             # nothing inserted yet
# basis = XorBasis([3, 10, 5])   # inserts 3, 10, 5
#
# Max subset XOR:                 XorBasis(arr).maxSubsetXor()
# Number of distinct subset XORs: XorBasis(arr).countDistinctSubsetXors()
# Subsets whose XOR is exactly k: XorBasis(arr).countSubsetsWithXorEqualToXMod(k, 10**9 + 7)
class XorBasis:
    # O(N * B)
    def __init__(self, arr=()):
        # pivots[b] = the basis value whose highest set bit is b, or 0 if none. Kept fully reduced: bit b is set in no
        # other basis value, which is what makes kthSmallestDistinctSubsetXor work
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
    def doesSubsetXorEqualToXExist(self, x):
        return x >= 0 and self.minXorOfXAndSubsetXor(x) == 0

    # largest XOR of any subset (0 if nothing inserted)
    # XorBasis([3, 10, 5]).maxSubsetXor() -> 15   # 10 ^ 5
    # O(B)
    def maxSubsetXor(self):
        return self.maxXorOfXAndSubsetXor(0)

    # largest x ^ (XOR of some subset)
    # XorBasis([3, 10, 5]).maxXorOfXAndSubsetXor(4) -> 14   # 4 ^ 10
    # O(B)
    def maxXorOfXAndSubsetXor(self, x):
        if x < 0:
            raise ValueError(f"XorBasis.maxXorOfXAndSubsetXor: {x} is negative")
        pivots = self.pivots
        for b in range(len(pivots) - 1, -1, -1):
            if pivots[b] and not (x >> b) & 1:
                x ^= pivots[b]
        return x

    # smallest x ^ (XOR of some subset)
    # XorBasis([3, 10, 5]).minXorOfXAndSubsetXor(15) -> 0   # 15 = 10 ^ 5
    # O(B)
    def minXorOfXAndSubsetXor(self, x):
        if x < 0:
            raise ValueError(f"XorBasis.minXorOfXAndSubsetXor: {x} is negative")
        pivots = self.pivots
        for b in range(len(pivots) - 1, -1, -1):
            if pivots[b] and (x >> b) & 1:
                x ^= pivots[b]
        return x

    # smallest XOR of a non-empty subset: 0 if some non-empty subset XORs to 0, None if nothing inserted
    # XorBasis([3, 10, 5]).minNonEmptySubsetXor() -> 3
    # XorBasis([3, 5, 6]).minNonEmptySubsetXor() -> 0   # 3 ^ 5 ^ 6 = 0
    # O(B)
    def minNonEmptySubsetXor(self):
        if self.numInserted > self.numPivots:
            return 0
        for p in self.pivots:
            if p:
                return p
        return None

    # the kth smallest distinct value some subset makes, k 0-indexed (k = 0 -> 0, the empty subset), or None if
    # k >= countDistinctSubsetXors()
    # XorBasis([1, 2]).kthSmallestDistinctSubsetXor(3) -> 3   # the makeable values are 0, 1, 2, 3
    # O(B)
    def kthSmallestDistinctSubsetXor(self, k):
        if k < 0:
            raise ValueError(f"XorBasis.kthSmallestDistinctSubsetXor: k = {k} is negative")
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

    # the kth smallest XOR over all 2^N subsets by position (the empty one included, repeats kept), k 0-indexed, or
    # None if k >= 2^N. Each distinct value comes from 2^(N - basisSize()) subsets, so it is the distinct one at
    # k >> (N - basisSize())
    # XorBasis([1, 1]).kthSmallestSubsetXor(1) -> 0   # every subset XOR, sorted: 0, 0, 1, 1
    # O(B)
    def kthSmallestSubsetXor(self, k):
        if k < 0:
            raise ValueError(f"XorBasis.kthSmallestSubsetXor: k = {k} is negative")
        n = self.size()
        if k >> n:
            return None
        return self.kthSmallestDistinctSubsetXor(k >> (n - self.basisSize()))

    # number of distinct values the subsets make, counting 0 from the empty subset: 2^basisSize()
    # XorBasis([3, 5, 6]).countDistinctSubsetXors() -> 4   # 0, 3, 5, 6
    # O(1)
    def countDistinctSubsetXors(self):
        return 1 << self.numPivots

    # number of subsets of the inserted values (by position, the empty one included) whose XOR is exactly x, mod mod:
    # 2^(N - basisSize()) if x can be made, else 0
    # XorBasis([3, 5, 6]).countSubsetsWithXorEqualToXMod(0, 10**9 + 7) -> 2   # {} and {3, 5, 6}
    # O(B + log(N))
    def countSubsetsWithXorEqualToXMod(self, x, mod):
        return pow(2, self.numInserted - self.numPivots, mod) if self.doesSubsetXorEqualToXExist(x) else 0

    # size of the basis (how many inserted values were independent)
    # O(1)
    def basisSize(self):
        return self.numPivots

    # how many values were inserted, including ones that didn't grow the basis
    # O(1)
    def size(self):
        return self.numInserted

    # the basis values, largest first (basisSize() of them; their subset XORs make exactly the makeable values)
    # O(B)
    def basis(self):
        return [p for p in reversed(self.pivots) if p]
