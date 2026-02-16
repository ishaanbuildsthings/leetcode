class Solution:
    def toggleLightBulbs(self, bulbs: list[int]) -> list[int]:
        on = [0] * (101)
        for v in bulbs:
            on[v]^=1
        res = []
        for i in range(1, 101):
            if on[i]:
                res.append(i)
        return res