# TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant
import math

class SparseTable:
    def __init__(self, nums, combineFn):
        n = len(nums)
        if n == 0:
            self.sparse = []
            self.combineFn = combineFn
            self.log2 = [0]
            return

        BITS = n.bit_length()

        sparse = [[0] * n for _ in range(BITS)]
        sparse[0] = nums[:]

        for log in range(1, BITS):
            half = 1 << (log - 1)
            length = 1 << log
            limit = n - length + 1
            rowPrev = sparse[log - 1]
            row = sparse[log]
            for left in range(limit):
                row[left] = combineFn(rowPrev[left], rowPrev[left + half])

        self.sparse = sparse
        self.combineFn = combineFn

        log2 = [0] * (n + 1)
        for i in range(2, n + 1):
            log2[i] = log2[i >> 1] + 1
        self.log2 = log2

    def query(self, l, r):
        width = r - l + 1
        power = self.log2[width]
        windowWidth = 1 << power
        leftAnswer = self.sparse[power][l]
        rightAnswer = self.sparse[power][r - windowWidth + 1]
        return self.combineFn(leftAnswer, rightAnswer)


class Solution:
    def maxGCDScore(self, nums: List[int], k: int) -> int:
        n = len(nums)

        by2 = []
        for v in nums:
            ops = 0
            while v % 2 == 0:
                v //= 2
                ops += 1
            by2.append(ops)
        
        mn = SparseTable(by2, min) # find min exponent in a range

        mxPow = max(by2)
        pf = [[0] * (mxPow + 1) for _ in range(n)] # pf[i][power] is the number of that exponent in 0...i
        pf[0][by2[0]] += 1
        for i in range(1, n):
            for power in range(mxPow + 1):
                pf[i][power] += pf[i - 1][power]
            pf[i][by2[i]] += 1

        sparse = SparseTable(nums, gcd)
        res = 0
        
        # fix this left edge
        for l in range(n):
            r = l
            while r < n:
                prevGcd = sparse.query(l, r)
                # binary search for the right edge of this boundary
                left = r
                right = n - 1
                resRight = None
                while left <= right:
                    m = (left + right) // 2
                    g = sparse.query(l, m)
                    if g == prevGcd:
                        resRight = m
                        left = m + 1
                    else:
                        right = m - 1
                # we go from l...resRight as a max width option
                width = resRight - l + 1
                score = width * prevGcd
                res = max(res, score)

                # now any subarray from l...r to l...resRight has the exact same subarray gcd, this is the full block range
                # we want the widest one here where we can also double the minimum power of 2
                # remember l...r already contains the minimum exponent of a power of 2 somewhere in there, and it won't go down further as we expand r to resRight, as the gcd is unchanging, so we already contain minimum powers of 2 here, we just want to allow as many as we can up to k

                lowPower = mn.query(l, resRight)
                left = l
                right = resRight
                resDouble = None
                while left <= right:
                    m = (left + right) // 2
                    atMin = pf[m][lowPower] - (pf[l - 1][lowPower] if l else 0)
                    if atMin <= k:
                        resDouble = m
                        left = m + 1
                    else:
                        right = m - 1
                if resDouble is not None:
                    width = resDouble - l + 1
                    score = 2 * width * prevGcd
                    res = max(res, score)

                r = resRight + 1
        
        return res
                        


# O(n^2) naive
# class Solution:
#     def maxGCDScore(self, nums: List[int], k: int) -> int:
#         by2 = []
#         for v in nums:
#             ops = 0
#             while v % 2 == 0:
#                 v //= 2
#                 ops += 1
#             by2.append(ops)

#         res = 0
#         n = len(nums)
#         for l in range(n):
#             currGcd = 0
#             countWithLowPower = 0
#             lowPower = inf
#             for r in range(l, n):
#                 v = nums[r]
#                 power = by2[r]
#                 if power == lowPower:
#                     countWithLowPower += 1
#                 elif power < lowPower:
#                     lowPower = power
#                     countWithLowPower = 1
#                 currGcd = gcd(currGcd, v)
#                 width = r - l + 1
#                 score = width * currGcd
#                 if countWithLowPower <= k:
#                     score *= 2
#                 res = max(res, score)
        
#         return res

