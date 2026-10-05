class Solution:
    def minRotations(self, s: str) -> int:
        curr = 0

        def step(a, b):
            diff1 = abs(a - b)
            diff2 = 10 - diff1
            return min(diff1, diff2)

        res = 0
        for i, v in enumerate(s):
            before = 0 if i == 0 else int(s[i - 1])
            current = int(s[i])
            dist = step(before, current)
            res += dist

        return res
            