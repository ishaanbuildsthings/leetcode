# https://leetcode.com/problems/uncrossed-lines/description/
# difficulty: medium
# tags: dynamic programming 2d, lcs

# Problem
# You are given two integer arrays nums1 and nums2. We write the integers of nums1 and nums2 (in the order they are given) on two separate horizontal lines.

# We may draw connecting lines: a straight line connecting two numbers nums1[i] and nums2[j] such that:

# nums1[i] == nums2[j], and
# the line we draw does not intersect any other connecting (non-horizontal) line.
# Note that a connecting line cannot intersect even at the endpoints (i.e., each number can only belong to one connecting line).

# Return the maximum number of connecting lines we can draw in this way.

# Solution, O(n^2) time and space
# Standard LCS, pair elements or move on

class Solution:
    def maxUncrossedLines(self, nums1: List[int], nums2: List[int]) -> int:
        @cache
        def dp(i, j):
            # base case
            if i == len(nums1) or j == len(nums2):
                return 0

            if nums1[i] == nums2[j]:
                return 1 + dp(i + 1, j + 1)

            return max(dp(i + 1, j), dp(i, j + 1))
        return dp(0, 0)