class Solution:
    def maxActiveSectionsAfterTrade(self, s: str) -> int:
        zeroBlocks = []

        streak = 0
        for i, v in enumerate(s):
            if v == '1':
                if streak:
                    zeroBlocks.append(streak)
                streak = 0
                continue
            if streak == 0:
                currL = i
            streak += 1
        if streak:
            zeroBlocks.append(streak)
        res = 0
        for i in range(len(zeroBlocks) - 1):
            res = max(res, zeroBlocks[i] + zeroBlocks[i + 1])
        return res + s.count('1')
        