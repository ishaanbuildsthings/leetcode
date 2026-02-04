class Solution:
    def waysToSplit(self, nums: List[int]) -> int:
        curr = 0
        pf = []
        for v in nums:
            curr += v
            pf.append(curr)
        
        def query(l, r):
            if not l:
                return pf[r]
            return pf[r] - pf[l - 1]
        
        MOD = 10**9 + 7
        res = 0

        for r in range(len(nums) - 2):
            pfSum = query(0, r)
            # find the furthest left start where the middle is big enough
            left = r+1
            right = len(nums) - 2
            resI = None
            while left <= right:
                m = (right+left)//2
                sLeft = query(r+1, m)
                if sLeft >= pfSum:
                    resI = m
                    right = m - 1
                else:
                    left = m + 1
            if resI is None:
                continue
            
            # find the furthest right the middle portion can go and still be <= right portion
            left = resI
            right = len(nums) - 2
            resI2 = None
            while left <= right:
                m = (right+left)//2
                sLeft = query(r+1, m)
                sRight = query(m + 1, len(nums) - 1)
                if sLeft <= sRight:
                    resI2 = m
                    left = m + 1
                else:
                    right = m - 1
            if resI2 is None:
                continue
            width = resI2 - resI + 1
            res += width
        
        return res % MOD