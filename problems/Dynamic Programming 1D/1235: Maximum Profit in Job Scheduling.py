# https://leetcode.com/problems/maximum-profit-in-job-scheduling/
# Difficulty: Hard
# tags: Dynamic Programming 1d, Binary Search

# Problem
# We have n jobs, where every job is scheduled to be done from startTime[i] to endTime[i], obtaining a profit of profit[i].

# You're given the startTime, endTime and profit arrays, return the maximum profit you can take such that there are no two jobs in the subset with overlapping time range.

# If you choose a job that ends at time X you will be able to start another job that starts at time X.

# Solution, O(n log n) time, O(n) space
# First, sort intervals by start time. Then, dp(i) tells us the answer starting at the ith interval. If we take it, proceed to the next interval that doesn't overlap (found with binary search), otherwise proceed to the next interval. We didn't need the starts array, it just made it easier to code.

class Solution:
    def jobScheduling(self, startTime: List[int], endTime: List[int], profit: List[int]) -> int:
        zipped = [[startTime[i], endTime[i], profit[i]] for i in range(len(startTime))]
        zipped.sort()
        starts = [zipped[i][0] for i in range(len(zipped))]

        # i is the index of zipped we are working with
        @cache
        def dp(i):
            # base case
            if i == len(zipped):
                return 0

            # if we take this job, we have to find the first job in the next region with a start time >= end
            end = zipped[i][1]
            firstIdxBiggerStart = bisect.bisect_left(starts, x=end, lo=i+1)
            ifTake = zipped[i][2] + dp(firstIdxBiggerStart)

            ifSkip = dp(i + 1)

            return max(ifTake, ifSkip)

        return dp(0)