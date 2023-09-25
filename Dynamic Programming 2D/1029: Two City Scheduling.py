# https://leetcode.com/problems/two-city-scheduling/
# Difficulty: Medium
# Tags: dynamic programming 2d, greedy

# Problem
# A company is planning to interview 2n people. Given the array costs where costs[i] = [aCosti, bCosti], the cost of flying the ith person to city a is aCosti, and the cost of flying the ith person to city b is bCosti.

# Return the minimum cost to fly every person to a city such that exactly n people arrive in each city.

# Solution, O(n^2) time and space though there is a better greedy solution
# For each person, we either fly them to A or B, and we track a surplus of flying them to A. So our dp state is n*surplus which is n^2 time and space. I also early pruned if the surplus got too big or small.

class Solution:
    def twoCitySchedCost(self, costs: List[List[int]]) -> int:
        @cache
        def dp(i, priorSurplusToA):
            # base case
            if i == len(costs):
                if priorSurplusToA == 0:
                    return 0
                return float('inf')
            # edge case
            remainingPeople = len(costs) - i
            if priorSurplusToA > remainingPeople or priorSurplusToA < -1 * remainingPeople:
                return float('inf')

            ifFlyToA = costs[i][0] + dp(i + 1, priorSurplusToA + 1)
            ifFlyToB = costs[i][1] + dp(i + 1, priorSurplusToA - 1)
            return min(ifFlyToA, ifFlyToB)
        return dp(0, 0)