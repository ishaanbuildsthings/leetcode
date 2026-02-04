class Solution:
    def minimumK(self, nums: List[int]) -> int:

        def do(x):
            ops = 0
            for v in nums:
                ops += math.ceil(v / x)
            return ops <= x**2
        l = 1
        r = 10**18
        res = None
        while l<=r:
            m = (r+l)//2
            if do(m):
                res = m
                r = m - 1
            else:
                l = m + 1
        return res
