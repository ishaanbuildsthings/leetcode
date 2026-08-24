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
    def findUnsortedSubarray(self, nums: List[int]) -> int:
        if nums == sorted(nums):
            return 0
        maxS = SparseTable(nums, lambda a, b: max(a, b))
        minS = SparseTable(nums, lambda a, b: min(a, b))
        res = inf

        # find the farthest left edge where the prefix is sorted
        farthestLeft = 0
        for i in range(1, len(nums)):
            if nums[i] >= nums[i - 1]:
                farthestLeft = i
            else:
                break
        
        # find the furthest left edge where the suffix is sorted
        farthestRight = len(nums) - 1
        for i in range(len(nums) - 2, -1, -1):
            if nums[i] <= nums[i + 1]:
                farthestRight = i
            else:
                break

        def isValid(l, r):
            # prefix isnt sorted
            if l - 1 > farthestLeft:
                return False
            # suffix isnt sorted
            if r + 1 < farthestRight:
                return False
            beforeTerm = nums[l - 1] if l else -inf
            afterTerm = nums[r + 1] if r < len(nums) - 1 else inf
            minInRange = minS.query(l, r)
            maxInRange = maxS.query(l, r)
            if minInRange < beforeTerm:
                return False
            if maxInRange > afterTerm:
                return False
            return True

        # for each left index, binary search for the shortest length that is valid
        for l in range(len(nums)):
            left = l
            right = len(nums) - 1
            resI = None
            while left <= right:
                m = (left+right)//2
                if isValid(l, m):
                    resI = m
                    right = m - 1
                else:
                    left = m + 1
            if resI is not None:
                width = resI - l + 1
                res = min(res, width)
        
        return res
