class Solution:
    def kInversePairs(self, n: int, k: int) -> int:
        MOD = 10**9 + 7

        # previous layer, the # of ways to produce k inversions with prev # of values
        prev = [0] * (k + 1)
        prev[0] = 1

        for count in range(1, n + 1):

            pf = list(itertools.accumulate(prev))

            ndp = [0] * (k + 1)

            for ninv in range(k + 1):

                R = ninv
                L = max(0, ninv - count + 1)

                gained = pf[R] - (pf[L - 1] if L else 0)
                ndp[ninv] = gained % MOD
            
            prev = ndp
        
        return prev[k]