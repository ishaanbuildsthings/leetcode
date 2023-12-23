# https://leetcode.com/problems/minimum-cuts-to-divide-a-circle/description/
# difficulty: easy
# tags: math, functional

# Problem
# A valid cut in a circle can be:

# A cut that is represented by a straight line that touches two points on the edge of the circle and passes through its center, or
# A cut that is represented by a straight line that touches one point on the edge of the circle and its center.
# Some valid and invalid cuts are shown in the figures below.


# Given the integer n, return the minimum number of cuts needed to divide a circle into n equal slices.

# Solution, O(1) time and space

class Solution:
    def numberOfCuts(self, n: int) -> int:
        return (
            n // 2 if n % 2 == 0 else
            n if n != 1 else
            0
        )

