# https://leetcode.com/problems/shortest-distance-to-target-color/
# difficulty: medium
# tags: dynamic programming 2d

# Solution, O(n) time O(1) space, could use just one hashmap as well, or binary search for the worse solution

class Solution:
    def shortestDistanceColor(self, colors: List[int], queries: List[List[int]]) -> List[int]:
        dpLeft = {
            (-1, i) : float('inf') for i in range(1, 4)
        } # maps (i, color) to the distance of the closest color

        for i in range(len(colors)):
            currColor = colors[i]
            for color in range(1, 4):
                distFromColor = 1 + dpLeft[(i - 1, color)] if color != currColor else 0
                dpLeft[(i, color)] = distFromColor

        dpRight = {
            (len(colors), i) : float('inf') for i in range(1, 4)
        }

        for i in range(len(colors) - 1, -1, -1):
            currColor = colors[i]
            for color in range(1, 4):
                distFromColor = 1 + dpRight[(i + 1, color)] if color != currColor else 0
                dpRight[(i, color)] = distFromColor

        return [
            min(dpLeft[(i, color)], dpRight[(i, color)]) if min(dpLeft[(i, color)], dpRight[(i, color)]) != float('inf') else -1 for i, color in queries
        ]