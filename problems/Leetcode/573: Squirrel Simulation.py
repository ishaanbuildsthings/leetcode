# https://leetcode.com/problems/squirrel-simulation/description/
# difficulty: medium

# Problem
# You are given two integers height and width representing a garden of size height x width. You are also given:

# an array tree where tree = [treer, treec] is the position of the tree in the garden,
# an array squirrel where squirrel = [squirrelr, squirrelc] is the position of the squirrel in the garden,
# and an array nuts where nuts[i] = [nutir, nutic] is the position of the ith nut in the garden.
# The squirrel can only take at most one nut at one time and can move in four directions: up, down, left, and right, to the adjacent cell.

# Return the minimal distance for the squirrel to collect all the nuts and put them under the tree one by one.

# The distance is the number of moves.

# Solution, O(nuts) time, O(1) space. Just test each nut if we grabbed it first then went to the tree. I was trying a one pass solution at first but it was convoluted, one may exist.

class Solution:
    def minDistance(self, height: int, width: int, tree: List[int], squirrel: List[int], nuts: List[List[int]]) -> int:
        totalRoundTripDistanceFromTree = 0 # distances for all nut round trips tree<->nut
        treeR, treeC = tree
        squirrelR, squirrelC = squirrel
        for nut in nuts:
            nutR, nutC = nut
            nutTreeDist = abs(nutR - treeR) + abs(nutC - treeC)
            nutTreeRoundtrip = nutTreeDist * 2
            totalRoundTripDistanceFromTree += nutTreeRoundtrip

        # boundary case, we go the three first then pick up all nuts
        squirrelTreeDist = abs(squirrelR - tree[0]) + abs(squirrelC - tree[1])
        res = squirrelTreeDist + totalRoundTripDistanceFromTree

        for nutR, nutC in nuts:
            # compute if we pick up that nut first
            distToFirstNut = abs(nutR - squirrelR) + abs(nutC - squirrelC)
            nutTreeDist = abs(nutR - treeR) + abs(nutC - treeC)
            distToReachTreeWithFirstNut = distToFirstNut + nutTreeDist
            roundTripNutTreeDist = 2 * nutTreeDist
            remainingRoundTripDistance = totalRoundTripDistanceFromTree - roundTripNutTreeDist
            totalDistance = remainingRoundTripDistance + distToReachTreeWithFirstNut
            res = min(res, totalDistance)

        return res

