class Solution:
    def distributeCookies(self, cookies: List[int], k: int) -> int:
        fmask = (1 << len(cookies)) - 1

        maskToSum = [0] * (fmask + 1)
        for mask in range(1, fmask + 1):
            msbIdx = mask.bit_length() - 1
            before = maskToSum[mask ^ (1 << msbIdx)]
            gain = cookies[msbIdx]
            nsum = before + gain
            maskToSum[mask] = nsum

        # mask of people already done and not part of this setup, what is the max unfairness for the remaining people not set in the mask?
        @cache
        def dp(mask, childrenLeft):
            if mask == fmask:
                return 0
            # if we have no children to give to, but still cookies, then we failed
            if childrenLeft == 0:
                return inf
            
            remaining = mask ^ fmask
            submask = remaining
            res = inf
            while submask:
                unfairness = max(maskToSum[submask], dp(mask | submask, childrenLeft - 1))
                res = min(res, unfairness)
                submask = (submask - 1) & remaining
            return res
        
        answer = dp(0, k)
        return answer
                
            