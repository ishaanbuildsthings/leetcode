# https://leetcode.com/problems/count-number-of-rectangles-containing-each-point/
# Difficulty: Medium
# Tags: Binary search

# Problem
# You are given a 2D integer array rectangles where rectangles[i] = [li, hi] indicates that ith rectangle has a length of li and a height of hi. You are also given a 2D integer array points where points[j] = [xj, yj] is a point with coordinates (xj, yj).

# The ith rectangle has its bottom-left corner point at the coordinates (0, 0) and its top-right corner point at (li, hi).

# Return an integer array count of length points.length where count[j] is the number of rectangles that contain the jth point.

# The ith rectangle contains the jth point if 0 <= xj <= li and 0 <= yj <= hi. Note that points that lie on the edges of a rectangle are also considered to be contained by that rectangle.

# Solution O(rectangles) space, O(rectangles log rectangles + points * rect height * log rect width) time
# Due to the odd constraints, we just hold a bucket for each height consisting of a list of rectangle widths. This takes max(100, rectangles) space and rectangles time. Can be optimized to reduce 100 to be the highest y coordinate for a rectangle. Then, sort each container, worst case rectangles log rectangles time and sort(rectangles) space. Now, for each point, iterate from y to max rect height, binary search on each bucket to find the amount of points, and add to result. In each bucket, I found the index of the first number >= x, and I validate that. To use l<=r, we can just push l out to the right, l will point to the first index big enough, or len(bucket) if there are none.

class Solution:
    def countRectangles(self, rectangles: List[List[int]], points: List[List[int]]) -> List[int]:
        byHeight = defaultdict(list) # byHeight[height] gives us a sorted list of rectnagles that have width, height
        for width, height in rectangles:
            byHeight[height].append(width)
        for height in byHeight:
            byHeight[height].sort()
        res = []
        for x, y in points:
            countForThis = 0
            for height in range(y, 101):
                l = 0
                r = len(byHeight[height]) - 1
                if r < 0:
                    continue
                # find the first number that is >= x
                while l < r:
                    m = (r+l) // 2 # m is the index for the width for a specific height
                    if byHeight[height][m] >= x:
                        r = m
                    else:
                        l = m + 1
                    # r is the index of the first number big enough
                if byHeight[height][r] < x:
                    continue
                newAdded = len(byHeight[height]) - r
                countForThis += newAdded
            res.append(countForThis)
        return res

