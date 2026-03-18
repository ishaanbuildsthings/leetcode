class Solution:
    def findBestValue(self, arr: List[int], target: int) -> int:
        if sum(arr) < target:
            return max(arr)
        l = 0
        r = 10**18

        # binary search, smallest value we can change everything to, where sum still >= target?

        def tot(x):
            return sum(min(v, x) for v in arr)
        
        resV = None
        while l<=r:
            m = (l+r)//2
            total = tot(m)
            if total >= target:
                resV = m
                r = m - 1
            else:
                l = m + 1
        
        diff1 = abs(tot(resV) - target)
        diff2 = abs(tot(resV-1) - target)
        if diff2 <= diff1:
            return resV-1
        return resV

            