# https://leetcode.com/problems/valid-square/description/
# difficulty: medium

# Problem
# Given the coordinates of four points in 2D space p1, p2, p3 and p4, return true if the four points construct a square.

# The coordinate of a point pi is represented as [xi, yi]. The input is not given in any order.

# A valid square has four equal sides with positive length and four equal angles (90-degree angles).

# Solution, O(1) time and space

class Solution:
    def validSquare(self, p1: List[int], p2: List[int], p3: List[int], p4: List[int]) -> bool:
        distances = []
        points = [p1, p2, p3, p4]
        for i in range(len(points) - 1):
            for j in range(i + 1, len(points)):
                y = abs(points[i][1] - points[j][1])
                x = abs(points[i][0] - points[j][0])
                dist = math.sqrt(y**2 + x**2)
                distances.append(dist)
        distances.sort()
        # edge case
        if distances[0] == 0:
            return False

        return (
            all(
                distances[i] == distances[i + 1]
                for i in range(3)
            ) and
            distances[-1] == distances[-2]
        )