class Solution:
    def countMonobit(self, n: int) -> int:
        res = 0
        for number in range(0, n + 1):
            vv = bin(number)[2:]
            if all(x == '1' for x in vv):
                res += 1
        return res + 1