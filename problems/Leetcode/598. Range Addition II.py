class Solution:
    def maxCount(self, m: int, n: int, ops: List[List[int]]) -> int:
        minX = m
        minY = n
        for x, y in ops:
            minX = min(minX, x)
            minY = min(minY, y)
        return minX * minY