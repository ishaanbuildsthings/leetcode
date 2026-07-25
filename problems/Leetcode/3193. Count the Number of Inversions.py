class Solution:
    def numberOfPermutations(self, n: int, requirements: List[List[int]]) -> int:
        MOD = 10**9 + 7
        mxCount = max(t[1] for t in requirements)
        dp = [0] * (mxCount + 1)
        dp[0] = 1

        reqToCnt = {endI : cnt for endI, cnt in requirements}

        # dp[k] is the # of ways to form valid permutations with exactly that many inversions for the previous layer

        for count in range(1, n + 1):
            pf = list(itertools.accumulate(dp))
            ndp = [0] * (mxCount + 1)

            # but if we have a specific requirement here then 
            requiredCount = None
            if count - 1 in reqToCnt:
                requiredCount = reqToCnt[count - 1]

            for ninv in range(mxCount + 1):
                if requiredCount is not None and ninv != requiredCount:
                    continue
                R = ninv
                L = max(0, ninv - count + 1)
                ndp[ninv] = (pf[R] - (pf[L - 1] if L else 0)) % MOD
            
            dp = ndp
        
        return sum(dp)