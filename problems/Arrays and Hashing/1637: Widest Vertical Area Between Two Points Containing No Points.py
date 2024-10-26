# https://leetcode.com/problems/widest-vertical-area-between-two-points-containing-no-points/description/
# difficulty: medium

# problem
# Given n points on a 2D plane where points[i] = [xi, yi], Return the widest vertical area between two points such that no points are inside the area.

# A vertical area is an area of fixed-width extending infinitely along the y-axis (i.e., infinite height). The widest vertical area is the one with the maximum width.

# Note that points on the edge of a vertical area are not considered included in the area.

# Solution, O(n log n) time and O(sort) space, just sort by x-coordinate, then find the largest gap

class Solution:
    def maxWidthOfVerticalArea(self, points: List[List[int]]) -> int:
        points.sort()
        widest = 0
        for i in range(len(points) - 1):
            widest = max(widest, points[i + 1][0] - points[i][0])
        return widest