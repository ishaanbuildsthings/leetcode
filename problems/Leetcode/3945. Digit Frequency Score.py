class Solution:
    def digitFrequencyScore(self, n: int) -> int:
        c = Counter(str(n))
        res = 0
        for k, v in c.items():
            res += int(k) * v
        return res