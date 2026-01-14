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