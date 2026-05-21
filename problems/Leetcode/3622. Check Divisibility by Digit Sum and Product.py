class Solution:
    def checkDivisibility(self, n: int) -> bool:
        ds = 0
        dp = 1
        for v in [int(x) for x in str(n)]:
            dp *= v
            ds += v
        return n % (ds+dp) == 0