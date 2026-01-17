class Solution:
    def preimageSizeFZF(self, k: int) -> int:

        def getFives(nFactorial):
            ans = 0
            for power in range(1, 100):
                factor = 5**power
                if factor > nFactorial:
                    break
                divisible = nFactorial // factor
                ans += divisible
            return ans
        
        # binary search for the smallest x! that has at at least k factors of 5

        l = 0
        r = 10**18
        resSmall = None
        while l <= r:
            m = (r+l)//2
            amountFive = getFives(m)
            if amountFive >= k:
                resSmall = m
                r = m - 1
            else:
                l = m + 1

        if resSmall is None:
            return 0
        
        # binary search for the largest <= k
        l = 0
        r = 10**18
        resLarge = None
        while l <= r:
            m = (r+l)//2
            amountFive = getFives(m)
            if amountFive <= k:
                resLarge = m
                l = m + 1
            else:
                r = m - 1
        
        return resLarge - resSmall + 1


