# https://leetcode.com/problems/furthest-building-you-can-reach/description/?envType=daily-question&envId=2024-02-17
# difficulty: medium
# tags: heap

# Problem
# You are given an integer array heights representing the heights of buildings, some bricks, and some ladders.

# You start your journey from building 0 and move to the next building by possibly using bricks or ladders.

# While moving from building i to building i+1 (0-indexed),

# If the current building's height is greater than or equal to the next building's height, you do not need a ladder or bricks.
# If the current building's height is less than the next building's height, you can either use one ladder or (h[i+1] - h[i]) bricks.
# Return the furthest building index (0-indexed) you can reach if you use the given ladders and bricks optimally.

# Solution, standard heap stuff. A bit tricky. I think you can do it both by bricks used or by ladders used.

class Solution:
    def furthestBuilding(self, heights: List[int], bricks: int, ladders: int) -> int:
        minHeap = []
        bricksUsed = 0
        for i in range(1, len(heights)):
            if heights[i] <= heights[i - 1]:
                continue
            requiredBricks = heights[i] - heights[i - 1]
            heapq.heappush(minHeap, requiredBricks)
            if len(minHeap) > ladders:
                smallestBricks = heapq.heappop(minHeap)
                bricksUsed += smallestBricks
                if bricksUsed > bricks:
                    return i - 1
        return len(heights) - 1