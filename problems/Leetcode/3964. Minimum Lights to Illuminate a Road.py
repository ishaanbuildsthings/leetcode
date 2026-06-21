class Solution:
    def minLights(self, lights: list[int]) -> int:
        n = len(lights)
        sweep = [0] * (n + 1)
        for i, v in enumerate(lights):
            if not v:
                continue
            L = max(0, i - v)
            R = min(n - 1, i + v)
            sweep[L] += 1
            sweep[R + 1] -= 1

        lit = [False] * n
        curr = 0
        for i in range(n):
            curr += sweep[i]
            if curr:
                lit[i] = True

        blocks = []
        streak = 0
        for i, v in enumerate(lit):
            if not v:
                streak += 1
            else:
                blocks.append(streak); streak = 0
        blocks.append(streak)

        res = 0
        for b in blocks:
            res += ceil(b / 3)
        return res
            
