# https://leetcode.com/problems/closest-dessert-cost/description/
# difficulty: medium
# tags: backtracking

# Problem
# You would like to make dessert and are preparing to buy the ingredients. You have n ice cream base flavors and m types of toppings to choose from. You must follow these rules when making your dessert:

# There must be exactly one ice cream base.
# You can add one or more types of topping or have no toppings at all.
# There are at most two of each type of topping.
# You are given three inputs:

# baseCosts, an integer array of length n, where each baseCosts[i] represents the price of the ith ice cream base flavor.
# toppingCosts, an integer array of length m, where each toppingCosts[i] is the price of one of the ith topping.
# target, an integer representing your target price for dessert.
# You want to make a dessert with a total cost as close to target as possible.

# Return the closest possible cost of the dessert to target. If there are multiple, return the lower one.

# Solution
# For each base, try all topping configurations, the depth is O(toppings) and branching factor is O(target), but really it gets amortized since once we branch future branching factors go down

class Solution:
    def closestCost(self, baseCosts: List[int], toppingCosts: List[int], target: int) -> int:
        best = float('inf')

        def backtrack(i, totalCost):
            nonlocal best
            # base case
            if i == len(toppingCosts):
                bestDistance = abs(target - best)
                currDistance = abs(target - totalCost)
                if currDistance < bestDistance:
                    best = totalCost
                elif currDistance == bestDistance:
                    best = min(best, totalCost)
                return

            # if take 0
            backtrack(i + 1, totalCost)
            # if take 1
            backtrack(i + 1, totalCost + toppingCosts[i])
            # if take 2
            backtrack(i + 1, totalCost + (2 * toppingCosts[i]))

        for base in baseCosts:
            backtrack(0, base)

        return best

