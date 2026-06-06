# https://leetcode.com/problems/count-all-possible-routes/description/
# difficulty: hard
# tags: dynamic programming 2d

# problem
# You are given an array of distinct positive integers locations where locations[i] represents the position of city i. You are also given integers start, finish and fuel representing the starting city, ending city, and the initial amount of fuel you have, respectively.

# At each step, if you are at city i, you can pick any city j such that j != i and 0 <= j < locations.length and move to city j. Moving from city i to city j reduces the amount of fuel you have by |locations[i] - locations[j]|. Please notice that |x| denotes the absolute value of x.

# Notice that fuel cannot become negative at any point in time, and that you are allowed to visit any city more than once (including start and finish).

# Return the count of all possible routes from start to finish. Since the answer may be too large, return it modulo 109 + 7.


# Solution, O(fuel * locations * locations) time, O(fuel * locations) space
# Choose somewhere, go there, and now we have a subproblem. Interested problem because the base case was handled by having no adjacent places to go, we just add 1 to the result.

MOD = 10**9 + 7

class Solution:
    def countRoutes(self, locations: List[int], start: int, finish: int, fuel: int) -> int:
        @cache
        def dp(fuelLeft, currentLocation):
            # base case handled by assigning an initial result
            resForThis = 1 if currentLocation == locations[finish] else 0

            for loc in locations:
                if loc == currentLocation:
                    continue
                distance = abs(loc - currentLocation)
                if distance > fuelLeft:
                    continue
                resForThis += dp(fuelLeft - distance, loc)

            return resForThis % MOD

        return dp(fuel, locations[start])



