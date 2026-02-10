class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        dpMin = 1 # "biggest" negative
        dpMax = 1 # identity
        res = -inf
        for v in nums:
            res = max(res, v * dpMin, v * dpMax)
            n1 = dpMin * v
            n2 = dpMax * v
            dpMin = min(1, n1, n2)
            dpMax = max(1, n1, n2)
        return res
