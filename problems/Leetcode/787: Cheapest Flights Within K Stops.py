# https://leetcode.com/problems/cheapest-flights-within-k-stops/description/
# difficulty: medium
# tags: dynamic programming 2d

# Problem
# There are n cities connected by some number of flights. You are given an array flights where flights[i] = [fromi, toi, pricei] indicates that there is a flight from city fromi to city toi with cost pricei.

# You are also given three integers src, dst, and k, return the cheapest price from src to dst with at most k stops. If there is no such route, return -1.

# Solution, O(edges * nodes * flights left) time, O(nodes * flights left) space
# Just dp each node with amount left

class Solution:
    def findCheapestPrice(self, n: int, flights: List[List[int]], src: int, dst: int, k: int) -> int:
        flightMap = defaultdict(list) # maps a flight to a list of [destination, price]
        for a, b, price in flights:
            flightMap[a].append([b, price])

        @cache
        def dp(currentNode, allowedFlightsLeft):
            # base case
            if currentNode == dst:
                return 0
            if allowedFlightsLeft == 0:
                return float('inf')

            cheapestPriceForThis = float('inf')
            for neighbor, price in flightMap[currentNode]:
                ifFlyHere = price + dp(neighbor, allowedFlightsLeft - 1)
                cheapestPriceForThis = min(cheapestPriceForThis, ifFlyHere)
            return cheapestPriceForThis

        res = dp(src, k + 1)
        if res == float('inf'):
            return -1
        return res

