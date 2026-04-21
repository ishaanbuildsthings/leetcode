class Solution:
    def consecutiveNumbersSum(self, n: int) -> int:
        tot = 0
        res = 0
        for cnt in range(1, n + 1):
            tot += cnt
            if tot > n:
                break
            remain = n - tot
            if remain % cnt == 0:
                res += 1
        return res
        