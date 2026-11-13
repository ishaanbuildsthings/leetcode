# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/RangeXorBasis.py

# RangeXorBasis: XOR basis questions about any subarray arr[l..r] (inclusive), answered online. Values must be >= 0.
# Keeps, for every prefix, a basis that prefers the most recent elements; the basis values whose element is at index
# >= l make exactly the subset XORs of arr[l..r].
# N = len(arr), B = number of bits in max(arr).
#
# rxb = RangeXorBasis([3, 10, 5, 6])
# rxb.maxSubsetXorInRange(1, 3) -> 15   # 10 ^ 5
# rxb.doesSubsetXorEqualToXExistInRange(0, 1, 9) -> True   # 3 ^ 10
class RangeXorBasis:
    # O(N * B) time and space
    def __init__(self, arr):
        for x in arr:
            if x < 0:
                raise ValueError(f"RangeXorBasis: value {x} is negative")
        n = len(arr)
        B = max(arr, default=0).bit_length()
        self.n = n
        self.B = B
        # block i (indexes i*B .. i*B + B - 1) is the basis after arr[0..i]: vals[i*B + b] = the basis value whose
        # highest set bit is b (0 if none), poss[i*B + b] = the index of the newest element it uses (-1 if none)
        self.vals = vals = [0] * (n * B)
        self.poss = poss = [-1] * (n * B)
        curVals = [0] * B
        curPoss = [-1] * B
        for i, x in enumerate(arr):
            pos = i
            for b in range(B - 1, -1, -1):
                if not (x >> b) & 1:
                    continue
                if not curVals[b]:
                    curVals[b] = x
                    curPoss[b] = pos
                    break
                if curPoss[b] < pos:
                    curVals[b], x = x, curVals[b]
                    curPoss[b], pos = pos, curPoss[b]
                x ^= curVals[b]
            vals[i * B:(i + 1) * B] = curVals
            poss[i * B:(i + 1) * B] = curPoss

    def _check(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"RangeXorBasis: range [{l}, {r}] is not inside [0, {self.n - 1}] with l <= r")

    # largest XOR of any subset of arr[l..r] (the empty subset gives 0)
    # O(B)
    def maxSubsetXorInRange(self, l, r):
        return self.maxXorOfXAndSubsetXorInRange(l, r, 0)

    # largest x ^ (XOR of some subset of arr[l..r])
    # O(B)
    def maxXorOfXAndSubsetXorInRange(self, l, r, x):
        self._check(l, r)
        if x < 0:
            raise ValueError(f"RangeXorBasis.maxXorOfXAndSubsetXorInRange: {x} is negative")
        base = r * self.B
        vals, poss = self.vals, self.poss
        for b in range(self.B - 1, -1, -1):
            if poss[base + b] >= l and not (x >> b) & 1:
                x ^= vals[base + b]
        return x

    # True if some subset of arr[l..r] XORs to exactly x (x = 0 is always True: the empty subset)
    # O(B)
    def doesSubsetXorEqualToXExistInRange(self, l, r, x):
        self._check(l, r)
        if x < 0 or x.bit_length() > self.B:
            return False
        base = r * self.B
        vals, poss = self.vals, self.poss
        for b in range(self.B - 1, -1, -1):
            if (x >> b) & 1:
                if poss[base + b] < l:
                    return False
                x ^= vals[base + b]
        return True

    # size of the basis of arr[l..r] (how many of its values are independent)
    # O(B)
    def basisSizeInRange(self, l, r):
        self._check(l, r)
        base = r * self.B
        return sum(1 for b in range(self.B) if self.poss[base + b] >= l)

    # number of distinct values the subsets of arr[l..r] make, counting 0 from the empty subset: 2^basisSize()
    # O(B)
    def countDistinctSubsetXorsInRange(self, l, r):
        return 1 << self.basisSizeInRange(l, r)
