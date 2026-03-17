# TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant

class SparseTable:
    def __init__(self, nums, combineFn):
        BITS = math.ceil(math.log2(len(nums))) + 1

        # Initialize the sparse table for all windows of length 1
        sparse = [[None] * len(nums) for _ in range(BITS)] # sparse[log][left] is the answer to the fn operator for the subarray [left:left+2**power]
        for left in range(len(nums)):
            sparse[0][left] = nums[left]

        for log in range(1, BITS):
            for left in range(len(nums)):
                right = left + 2**log - 1
                if right >= len(nums):
                    break
                leftHalfAnswer = sparse[log - 1][left]
                rightHalfAnswer = sparse[log - 1][int(left + (2**(log - 1)))]
                combinedAnswer = combineFn(leftHalfAnswer, rightHalfAnswer)
                sparse[log][left] = combinedAnswer

        self.sparse = sparse
        self.combineFn = combineFn

    def query(self, l, r):
        width = r - l + 1
        power = math.floor(math.log2(width))
        windowWidth = 2**power
        leftAnswer = self.sparse[power][l]
        rightSideStart = r - windowWidth + 1
        rightAnswer = self.sparse[power][rightSideStart]
        combinedAnswer = self.combineFn(leftAnswer, rightAnswer)
        return combinedAnswer

class Solution:
    def maxGcdSum(self, nums: List[int], k: int) -> int:
        res = -inf

        def agg(a, b):
            return math.gcd(a, b)

        sparse = SparseTable(nums, agg)

        curr = 0
        pf = []
        for num in nums:
            curr += num
            pf.append(curr)
        
        def query(l, r):
            return pf[r] - pf[l - 1] if l else pf[r]
        
        # for each l, we have up to log(max(nums)) valid right positions, since at most our GCD can drop that many times, so we binary search for the maximum sum for all possible GCDs
        for l in range(len(nums)):
            currentLeftBoundary = l + k - 1
            if currentLeftBoundary >= len(nums):
                break
            desiredGcd = sparse.query(l, currentLeftBoundary)
            while desiredGcd >= 1:

                # binary search for the rightmost index s.t. l...rightmost has a gcd of at least desiredGcd
                left = currentLeftBoundary
                right = len(nums) - 1
                resRightmost = None
                while left <= right:
                    m = (left+right)//2
                    computedGcd = sparse.query(l, m)
                    computedSum = query(l, m)
                    if computedGcd >= desiredGcd:
                        resRightmost = m
                        left = m + 1
                    else:
                        right = m - 1
                if resRightmost is None:
                    break
                width = resRightmost - l + 1
                totSum = query(l, resRightmost)
                score = totSum * desiredGcd
                res = max(res, score)

                if currentLeftBoundary == len(nums) - 1:
                    break
                
                if desiredGcd == 1:
                    break
                
                if resRightmost == len(nums) - 1:
                    break
                nextGcd = sparse.query(l, resRightmost + 1)
                desiredGcd = nextGcd
                currentLeftBoundary = resRightmost + 1

        
        return res
            