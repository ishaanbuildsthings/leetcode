# https://leetcode.com/problems/minimum-time-visiting-all-points/
# difficulty: easy
# tags: math

# Problem
# On a 2D plane, there are n points with integer coordinates points[i] = [xi, yi]. Return the minimum time in seconds to visit all the points in the order given by points.

# You can move according to these rules:

# In 1 second, you can either:
# move vertically by one unit,
# move horizontally by one unit, or
# move diagonally sqrt(2) units (in other words, move one unit vertically then one unit horizontally in 1 second).
# You have to visit the points in the same order as they appear in the array.
# You are allowed to pass through points that appear later in the order, but these do not count as visits.

# Solution, O(points) time, O(1) space, we can easily deduce the time for any two points, I solved this on my phone lol

class Solution:
    def minTimeToVisitAllPoints(self, points: List[List[int]]) -> int:
        def getDist(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            diag = min(abs(x1-x2), abs(y1-y2))
            straight = max(abs(x1-x2), abs(y1-y2)) - diag
            return diag + straight

        res = 0
        for i in range(len(points) - 1):
          res += getDist(points[i], points[i + 1])
        return res
