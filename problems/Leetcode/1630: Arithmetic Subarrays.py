# MIN sparse table
# O(n log n) build
# O(1) range MIN

class SparseMin:
    def __init__(self, arr):
        self.n = len(arr)
        self.LOG = self.n.bit_length()
        self.sparse = [[0] * self.n for _ in range(self.LOG)]
        for i in range(self.n):
            self.sparse[0][i] = arr[i]
        for power in range(1, self.LOG):
            halfWidth = 1 << (power - 1)
            for left in range(self.n):
                val = self.sparse[power - 1][left]
                rightEdge = left + halfWidth
                if rightEdge < self.n:
                    val = min(val, self.sparse[power - 1][rightEdge])
                self.sparse[power][left] = val

    def query(self, l, r):
        width = r - l + 1
        maxPow = width.bit_length() - 1
        powWidth = 1 << maxPow
        return min(
            self.sparse[maxPow][l],
            self.sparse[maxPow][l + width - powWidth]
        )

# MAX sparse table
# O(n log n) build
# O(1) range MAX

class SparseMax:
    def __init__(self, arr):
        self.n = len(arr)
        self.LOG = self.n.bit_length()
        self.sparse = [[0] * self.n for _ in range(self.LOG)]
        for i in range(self.n):
            self.sparse[0][i] = arr[i]
        for power in range(1, self.LOG):
            halfWidth = 1 << (power - 1)
            for left in range(self.n):
                val = self.sparse[power - 1][left]
                rightEdge = left + halfWidth
                if rightEdge < self.n:
                    val = max(val, self.sparse[power - 1][rightEdge])
                self.sparse[power][left] = val

    def query(self, l, r):
        width = r - l + 1
        maxPow = width.bit_length() - 1
        powWidth = 1 << maxPow
        return max(
            self.sparse[maxPow][l],
            self.sparse[maxPow][l + width - powWidth]
        )


class Solution:
    def checkArithmeticSubarrays(self, nums: List[int], l: List[int], r: List[int]) -> List[bool]:
        MOD = (2**61) - 1
        B = random.randrange(2, MOD - 2)
        SHIFT = 100000 # make everything positive
        n = len(nums)

        # pf hashes
        pf = [0] * n
        for i, v in enumerate(nums):
            prev = pf[i - 1] if i else 0
            npf = (prev + pow(B, v + SHIFT, MOD)) % MOD
            pf[i] = npf

        def queryHash(l, r):
            return (pf[r] - (pf[l - 1] if l else 0)) % MOD

        mn = SparseMin(nums)
        mx = SparseMax(nums)

        res = []
        for ql, qr in zip(l, r):
            pfHash = queryHash(ql, qr)
            low = mn.query(ql, qr)
            high = mx.query(ql, qr)
            if low == high:
                res.append(True)
                continue
            jumps = qr - ql
            diff = high - low
            if diff % jumps:
                res.append(False)
                continue
            stepSize = diff // jumps
            ratio = pow(B, stepSize, MOD)
            terms = qr - ql + 1
            want = (pow(B, low + SHIFT, MOD)
                    * (pow(ratio, terms, MOD) - 1)
                    * pow(ratio - 1, MOD - 2, MOD)) % MOD
            res.append(queryHash(ql, qr) == want)
        
        return res

