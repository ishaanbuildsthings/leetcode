class Solution:
    def sumOfBlocks(self, n: int) -> int:
        res = 0
        MOD = 10**9 + 7
        idx = 1
        for v in range(1, n + 1):
            curr = 1
            for j in range(idx, idx + v):
                curr *= j
                curr %= MOD
            idx += v
            res += curr
            res %= MOD
        
        return res