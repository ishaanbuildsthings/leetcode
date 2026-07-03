class Solution:
    def minSubarray(self, nums: List[int], p: int) -> int:
        n = len(nums)
        tot = sum(nums)
        if tot % p == 0:
            return 0
        mp = {0 : -1} # maps sum % p to rightmost
        pf = 0
        res = inf
        for i, v in enumerate(nums):
            pf += v
            # PF - cutOff == tot % p
            # PF - tot = cutOff (with modds)
            reqCut = (pf - tot) % p
            if reqCut in mp:
                width = i - mp[reqCut]
                res = min(res, width)
            mp[pf % p] = i
        return res if res < n else -1
    

