# https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/?currentPage=1&orderBy=newest_to_oldest&query=
# difficulty: medium
# tags: greedy

# Solution
class Solution:
    def findMinArrowShots(self, points: List[List[int]]) -> int:
        points.sort(key = lambda x: x[1])
        res = 0
        currentPos = float('-inf')
        for i in range(len(points)):
            l, r = points[i]
            if not (currentPos >= l and currentPos <= r):
                res += 1
                currentPos = r
        return res

