class Solution:
    def maxCaloriesBurnt(self, heights: List[int]) -> int:
        heights.sort()
        res = 0
        n = len(heights)
        prev = 0
        for i in range(n):
            if i % 2 == 0:
                j = n - (i//2) - 1
            else:
                j = (i//2)
            diff = abs(heights[j] - prev)
            res += diff**2
            prev = heights[j]
        
        return res