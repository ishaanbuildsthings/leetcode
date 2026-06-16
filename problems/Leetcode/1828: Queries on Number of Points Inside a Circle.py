# https://leetcode.com/problems/queries-on-number-of-points-inside-a-circle/description/
# difficulty: medium

# problem
# You are given an array points where points[i] = [xi, yi] is the coordinates of the ith point on a 2D plane. Multiple points can have the same coordinates.

# You are also given an array queries where queries[j] = [xj, yj, rj] describes a circle centered at (xj, yj) with a radius of rj.

# For each query queries[j], compute the number of points inside the jth circle. Points on the border of the circle are considered inside.

# Return an array answer, where answer[j] is the answer to the jth query.

# Solution, brute force, surprisingly there is no algorithm with faster worst case (but there are faster average case algorithms). For each query, check all points. O(n * k) time, O(1) space

class Solution:
    def countPoints(self, points: List[List[int]], queries: List[List[int]]) -> List[int]:
        res = []
        for x, y, r in queries:
            amount = 0
            for x2, y2 in points:
                dist = math.sqrt(abs(x - x2)**2 + abs(y - y2)**2)
                if dist <= r:
                    amount += 1
            res.append(amount)
        return res