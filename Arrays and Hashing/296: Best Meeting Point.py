# https://leetcode.com/problems/best-meeting-point/description/
# difficulty: hard
# tags: median

# Given an m x n binary grid grid where each 1 marks the home of one friend, return the minimal total travel distance.

# The total travel distance is the sum of the distances between the houses of the friends and the meeting point.

# The distance is calculated using Manhattan Distance, where distance(p1, p2) = |p2.x - p1.x| + |p2.y - p1.y|.

# Solution
# Solve the medians independently

class Solution:
    def minTotalDistance(self, grid: List[List[int]]) -> int:
        height = len(grid)
        width = len(grid[0])

        xs = []
        ys = []
        for r in range(height):
            for c in range(width):
                if grid[r][c]:
                    xs.append(c)
                    ys.append(r)
        xs.sort() # can skip by enumerating in order

        def getMedian(arr):
            mid = (len(arr) - 1) // 2
            if len(arr) % 2 == 1:
                return arr[mid]
            return int((arr[mid] + arr[mid + 1]) / 2)

        xMed = getMedian(xs)
        yMed = getMedian(ys)

        res = 0
        for r in range(height):
            for c in range(width):
                if grid[r][c]:
                    res += abs(r - yMed) + abs(c - xMed)

        return res