class Solution:
    def maxJump(self, stones: List[int]) -> int:
        if len(stones) == 2:
            return stones[-1] - stones[0]
        res = 0
        for i in range(len(stones) - 2):
            res = max(res, stones[i + 2] - stones[i])
        return res