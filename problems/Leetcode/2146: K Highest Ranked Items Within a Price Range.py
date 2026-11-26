# https://leetcode.com/problems/k-highest-ranked-items-within-a-price-range/
# # difficulty: medium
# # tags: matrix bfs, heap, multiconcept, queue

# Problem
# You are given a 0-indexed 2D integer array grid of size m x n that represents a map of the items in a shop. The integers in the grid represent the following:

# 0 represents a wall that you cannot pass through.
# 1 represents an empty cell that you can freely move to and from.
# All other positive integers represent the price of an item in that cell. You may also freely move to and from these item cells.
# It takes 1 step to travel between adjacent grid cells.

# You are also given integer arrays pricing and start where pricing = [low, high] and start = [row, col] indicates that you start at the position (row, col) and are interested only in items with a price in the range of [low, high] (inclusive). You are further given an integer k.

# You are interested in the positions of the k highest-ranked items whose prices are within the given price range. The rank is determined by the first of these criteria that is different:

# Distance, defined as the length of the shortest path from the start (shorter distance has a higher rank).
# Price (lower price has a higher rank, but it must be in the price range).
# The row number (smaller row number has a higher rank).
# The column number (smaller column number has a higher rank).
# Return the k highest-ranked items within the price range sorted by their rank (highest to lowest). If there are fewer than k reachable items within the price range, return all of them.

# Solution
# First do a BFS which at worst case is m*n time. Add each element to a considered pile. Then I sorted and got the k elements, we could use a heap too. Maybe we could greedily expand our BFS (though this may need a heap), or insert considered into a heap directly. A heap does improve complexity. Not sure if we can use median of medians quickselect to get linear time. Also we use BFS not DFS so we know when we get to a cell it is the shortest path.

DIFFS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]
class Solution:
    def highestRankedKItems(self, grid: List[List[int]], pricing: List[int], start: List[int], k: int) -> List[List[int]]:
        height = len(grid)
        width = len(grid[0])
        # 0 = wall
        # 1 = space
        # 2+ = price, can move

        q = collections.deque()
        q.append(start)
        seen = { (start[0], start[1]) }
        steps = 0
        considered = [] # stores (distance, price, row, column)

        while q:
            length = len(q)
            for _ in range(length):
                r, c = q.popleft()
                # if we are at a valid item, add it to our considered
                if pricing[1] >= grid[r][c] >= pricing[0]:
                    tup = (steps, grid[r][c], r, c)
                    considered.append(tup)
                for rowDiff, colDiff in DIFFS:
                    newRow = rowDiff + r
                    newCol = colDiff + c
                    # skip oob
                    if newRow < 0 or newRow == height or newCol < 0 or newCol == width:
                        continue
                    # skip walls
                    if not grid[newRow][newCol]:
                        continue
                    # skip seen
                    if (newRow, newCol) in seen:
                        continue
                    seen.add((newRow, newCol))
                    q.append([newRow, newCol])
            steps += 1
        filtered = sorted(considered)[:k]
        return [[r, c] for _, _, r, c in filtered]




