# https://leetcode.com/problems/maximum-ice-cream-bars/
# difficulty: medium
# tags: bucket sort (kind of)


# Problem
# It is a sweltering summer day, and a boy wants to buy some ice cream bars.

# At the store, there are n ice cream bars. You are given an array costs of length n, where costs[i] is the price of the ith ice cream bar in coins. The boy initially has coins coins to spend, and he wants to buy as many ice cream bars as possible.

# Note: The boy can buy the ice cream bars in any order.

# Return the maximum number of ice cream bars the boy can buy with coins coins.

# You must solve the problem by counting sort.

# Solution, O(costs + max cost) time, O(costs) space
# Get the # of occurences of each cost, try bigger costs until we run out of money. This works because costs[i] is capped.

class Solution:
    def maxIceCream(self, costs: List[int], coins: int) -> int:
        counts = collections.Counter(costs)
        res = 0
        totalSpent = 0
        nextCost = 1
        biggestCost = max(costs)
        while True:
            coinsLeft = coins - totalSpent
            if nextCost > coinsLeft:
                return res
            if nextCost > biggestCost:
                return res
            amountAtThatCost = counts[nextCost]
            maxWeCanBuy = min(amountAtThatCost, coinsLeft // nextCost)
            res += maxWeCanBuy
            totalSpent += maxWeCanBuy * nextCost
            nextCost += 1
        return res
