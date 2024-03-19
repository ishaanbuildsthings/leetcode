# https://leetcode.com/problems/count-ways-to-group-overlapping-ranges/description/
# difficulty: medium

# Problem
# You are given a 2D integer array ranges where ranges[i] = [starti, endi] denotes that all integers between starti and endi (both inclusive) are contained in the ith range.

# You are to split ranges into two (possibly empty) groups such that:

# Each range belongs to exactly one group.
# Any two overlapping ranges must belong to the same group.
# Two ranges are said to be overlapping if there exists at least one integer that is present in both ranges.

# For example, [1, 3] and [2, 5] are overlapping because 2 and 3 occur in both ranges.
# Return the total number of ways to split ranges into two groups. Since the answer may be very large, return it modulo 109 + 7.

# Solution, O(sort)

class Solution:
    def countWays(self, ranges: List[List[int]]) -> int:
        MOD = 10**9 + 7

        ranges.sort()
        count = 0
        right = float('-inf')
        for i in range(len(ranges)):
            if ranges[i][0] > right:
                count += 1
            right = max(right, ranges[i][1])
        res = 1
        for i in range(count):
            res *= 2
            res %= MOD
        return res