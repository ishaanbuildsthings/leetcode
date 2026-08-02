class Solution:
    def countTriples(self, n: int) -> int:
        res = 0
        for one in range(1, n + 1):
            for two in range(one, n + 1):
                big = one**2 + two**2
                reduction = math.sqrt(big)
                if reduction > n:
                    continue
                res += math.floor(reduction) == reduction
        return res * 2