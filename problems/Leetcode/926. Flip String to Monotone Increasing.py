class Solution:
    def minFlipsMonoIncr(self, s: str) -> int:
        pf = [] # stores count of 0s
        curr = 0
        for v in s:
            curr += v == '0'
            pf.append(curr)
        
        def queryZ(l, r):
            if l >= len(s): return 0
            return pf[r] - (pf[l - 1] if l else 0)
        
        def queryO(l, r):
            if l >= len(s): return 0
            return (r - l + 1) - queryZ(l, r)
        
        res = inf

        # 0...i is 0s, i+1...n-1 is 1s
        for i in range(len(s)):
            flipLeft = queryO(0, i)
            flipRight = queryZ(i + 1, len(s) - 1)
            res = min(res, flipLeft + flipRight)
        
        # handle edge case make all into a 1
        res = min(res, s.count('0'))

        return res