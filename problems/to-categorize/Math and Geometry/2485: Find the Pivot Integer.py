# https://leetcode.com/problems/find-the-pivot-integer/
# difficulty: easy
# tags: binary search, math

# Problem
# Given a positive integer n, find the pivot integer x such that:

# The sum of all elements between 1 and x inclusively equals the sum of all elements between x and n inclusively.
# Return the pivot integer x. If no such integer exists, return -1. It is guaranteed that there will be at most one pivot index for the given input.

# Solution, O(log n) time, O(1) space
# We can calculate the prefix sum of a given n (and therefore a range query) in O(1) since it's just calculating a triangle number. Binary search and test.

# @cache
def calcTriangleNum(n):
    return (n * (n + 1)) / 2

class Solution:
    def pivotInteger(self, n: int) -> int:
        l = 1
        r = n

        while l <= r:
            m = (r + l) // 2 # r is the pivot we try
            leftPortion = calcTriangleNum(m)
            rightPortion = calcTriangleNum(n) - calcTriangleNum(m - 1)
            difference = rightPortion - leftPortion
            if rightPortion == leftPortion:
                return m
            if rightPortion > leftPortion:
                l = m + 1
            if leftPortion > rightPortion:
                r = m - 1
        leftPortion = calcTriangleNum(r + 1)
        rightPortion = calcTriangleNum(n) - calcTriangleNum(r + 1)
        return -1