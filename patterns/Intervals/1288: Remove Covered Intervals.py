# https://leetcode.com/problems/remove-covered-intervals/description/
# difficulty: medium
# tags: intervals

# Problem
# Given an array intervals where intervals[i] = [li, ri] represent the interval [li, ri), remove all intervals that are covered by another interval in the list.

# The interval [a, b) is covered by the interval [c, d) if and only if c <= a and b <= d.

# Return the number of remaining intervals.


# Solution 1, O(n log n) time, O(sort) space
# Sort the intervals by smallest start, biggest end. Then iterate and see how many intervals we can consume.
# * Solution 2 (commented), O(n^2) time and O(n) space, just brute force try covering everything, you can make optimizations to skip certain intervals but this solution isn't good anyway

class Solution:
    def removeCoveredIntervals(self, intervals: List[List[int]]) -> int:

        intervals.sort(key=lambda x: (x[0], -x[1]))
        removed = 0
        prevEnd = float('-inf')
        for i in range(len(intervals)):
            start, end = intervals[i]
            if start > prevEnd:
                prevEnd = end
            elif end <= prevEnd:
                removed += 1
            elif end > prevEnd:
                prevEnd = end
        return len(intervals) - removed

      # covered = set()
        # for i in range(len(intervals)):
        #     firstInterval = intervals[i]
        #     for j in range(len(intervals)):
        #         if j == i:
        #             continue
        #         secondInterval = intervals[j]
        #         if firstInterval[0] <= secondInterval[0] and firstInterval[1] >= secondInterval[1]:
        #             covered.add(j)
        #         if secondInterval[0] <= firstInterval[0] and secondInterval[1] >= firstInterval[1]:
        #             covered.add(i)
        # return len(intervals) - len(covered)

