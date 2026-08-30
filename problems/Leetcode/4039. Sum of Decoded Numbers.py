class Solution:
    def sumDecoded(self, nums: list[int]) -> int:
        MOD = 10**9 + 7
        res = 0

        for v in nums:
            width = v % 10
            d = v // 10

            s = str(d)

            x = int(s[:width])
            y = int(s[width:])


            gain = pow(x, y, MOD)
            res += gain

        return res % MOD
            
            