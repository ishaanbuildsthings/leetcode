# https://leetcode.com/problems/minimum-time-to-make-rope-colorful/description/?envType=daily-question&envId=2023-12-27
# difficulty: medium
# tags: greedy, dynamic programming 2d

# Problem
# Alice has n balloons arranged on a rope. You are given a 0-indexed string colors where colors[i] is the color of the ith balloon.

# Alice wants the rope to be colorful. She does not want two consecutive balloons to be of the same color, so she asks Bob for help. Bob can remove some balloons from the rope to make it colorful. You are given a 0-indexed integer array neededTime where neededTime[i] is the time (in seconds) that Bob needs to remove the ith balloon from the rope.

# Return the minimum time Bob needs to make the rope colorful.

# Solution (greedy), for each consecutive group keep only the best one. I was dumb and did a 26n dp instead.

class Solution:
    def minCost(self, colors: str, neededTime: List[int]) -> int:

        memo = [defaultdict(lambda: -1) for _ in range(len(colors))]
        def dp(i, prevColor):
            # base
            if i == len(colors):
                return 0

            if memo[i][prevColor] != -1:
                return memo[i][prevColor]

            resThis = float('inf')

            # we can skip this if we are a different color
            if colors[i] != prevColor:
                resThis = dp(i + 1, colors[i])

            # we can remove this
            ifRemoveThis = neededTime[i] + dp(i + 1, prevColor)

            resThis = min(resThis, ifRemoveThis)
            memo[i][prevColor] = resThis
            return resThis

        return dp(0, None)