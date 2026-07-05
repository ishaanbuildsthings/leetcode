class Solution:
    def maxDigitRange(self, nums: list[int]) -> int:
        currMax = -inf
        res = 0
        for v in nums:
            vs = str(v)
            MIN = inf
            MAX = -inf
            for c in vs:
                MIN = min(MIN, int(c))
                MAX = max(MAX, int(c))
            drange = MAX - MIN
            if drange > currMax:
                res = v
                currMax = drange
            elif drange == currMax:
                res += v
        return res