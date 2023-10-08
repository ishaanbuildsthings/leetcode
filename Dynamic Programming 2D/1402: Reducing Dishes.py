# https://leetcode.com/problems/reducing-dishes/description/
# difficulty: hard
# tags: dynamic programming 2d

# problem
# A chef has collected data on the satisfaction level of his n dishes. Chef can cook any dish in 1 unit of time.

# Like-time coefficient of a dish is defined as the time taken to cook that dish including previous dishes multiplied by its satisfaction level i.e. time[i] * satisfaction[i].

# Return the maximum sum of like-time coefficient that the chef can obtain after dishes preparation.

# Dishes can be prepared in any order and the chef can discard some dishes to get this maximum value.

# Solution, sort the best dishes to go last as they get more value. Then dp where we can cook or not cook a dish.

class Solution:
    def maxSatisfaction(self, satisfaction: List[int]) -> int:
        satisfaction.sort()

        @cache
        def dp(prevTime, i):
            # base case
            if i == len(satisfaction):
                return 0

            ifCook = ((prevTime + 1) * satisfaction[i]) + dp(prevTime + 1, i + 1)
            ifSkip = dp(prevTime, i + 1)
            return max(ifCook, ifSkip)

        return dp(0, 0)