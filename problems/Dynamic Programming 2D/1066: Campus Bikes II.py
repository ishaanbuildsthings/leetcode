# https://leetcode.com/problems/campus-bikes-ii/
# difficulty: medium
# tags: dynamic programming 2d, dp bitmask

# problem
# On a campus represented as a 2D grid, there are n workers and m bikes, with n <= m. Each worker and bike is a 2D coordinate on this grid.

# We assign one unique bike to each worker so that the sum of the Manhattan distances between each worker and their assigned bike is minimized.

# Return the minimum possible sum of Manhattan distances between each worker and their assigned bike.

# The Manhattan distance between two points p1 and p2 is Manhattan(p1, p2) = |p1.x - p2.x| + |p1.y - p2.y|.

# Solution, O(2^bikes * people * bikes * bikes) time, O(people * bikes) space
# Just try, for each person, using every bike. DP bitmask to indicate which bikes are taken, and iterate over the person we are on.

class Solution:
    def assignBikes(self, workers: List[List[int]], bikes: List[List[int]]) -> int:
        fullMask = 0
        for i in range(len(bikes)):
            fullMask = fullMask | (1 << i)

        # i tells us which person we are solving for, mask tells us which bikes are taken
        @cache
        def dp(i, mask):
            if i == len(workers):
                return 0

            resForThis = float('inf')

            for bikeI in range(len(bikes)):
                bike = bikes[bikeI]
                # skip taken bikes
                if mask & (1 << bikeI):
                    continue
                ifTakeThisBikeNewMask = mask | (1 << bikeI)
                bikeR, bikeC = bike
                r, c = workers[i]
                dist = abs(bikeR - r) + abs(bikeC - c)
                ifTakeThisBike = dist + dp(i + 1, ifTakeThisBikeNewMask)
                resForThis = min(resForThis, ifTakeThisBike)
            return resForThis
        return dp(0, 0)
