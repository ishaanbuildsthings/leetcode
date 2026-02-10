class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        fmax = lambda x, y: x if x > y else y

        res = -inf
        currMax = -inf
        for v in nums:
            currMax = fmax(currMax + v, v)
            res = fmax(res, currMax)
        return res