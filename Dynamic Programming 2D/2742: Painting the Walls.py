# https://leetcode.com/problems/painting-the-walls/?envType=daily-question&envId=2023-10-14
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# You are given two 0-indexed integer arrays, cost and time, of size n representing the costs and the time taken to paint n different walls respectively. There are two painters available:

# A paid painter that paints the ith wall in time[i] units of time and takes cost[i] units of money.
# A free painter that paints any wall in 1 unit of time at a cost of 0. But the free painter can only be used if the paid painter is already occupied.
# Return the minimum amount of money required to paint the n walls.

# Solution
# Each wall can only be painted by one painter. So try each option. At the end, we have a valid state if the total time the paid painter was painting >= the free painter time. We cap the time once it exceeds the max possible free painter time to reduce the DP states. A trick I learned from another hard DP problem recently.

class Solution:
    def paintWalls(self, cost: List[int], time: List[int]) -> int:
        # extra time represents the surplus tht the paid painter has spent painting
        @cache
        def dp(i, extraTime):
            # base case
            if i == len(cost):
                return 0 if extraTime >= 0 else float('inf')

            resForThis = float('inf')

            ifFree = dp(i + 1, extraTime - 1)
            newExtraTime = min(extraTime + time[i], len(cost))
            ifPaid = cost[i] + dp(i + 1, newExtraTime)

            return min(ifFree, ifPaid)

        return dp(0, 0)
