class Solution:
    def checkGoodInteger(self, n: int) -> bool:
        dsum = 0
        ssum = 0
        for v in str(n):
            dsum += int(v)
            ssum += int(v)**2
        return ssum-dsum >= 50