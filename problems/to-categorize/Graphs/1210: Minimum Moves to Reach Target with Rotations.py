# https://leetcode.com/problems/minimum-moves-to-reach-target-with-rotations/
# Difficulty: Hard
# Tags: matrix bfs

# Problem
# In an n*n grid, there is a snake that spans 2 cells and starts moving from the top left corner at (0, 0) and (0, 1). The grid has empty cells represented by zeros and blocked cells represented by ones. The snake wants to reach the lower right corner at (n-1, n-2) and (n-1, n-1).

# In one move the snake can:

# Move one cell to the right if there are no blocked cells there. This move keeps the horizontal/vertical position of the snake as it is.
# Move down one cell if there are no blocked cells there. This move keeps the horizontal/vertical position of the snake as it is.
# Rotate clockwise if it's in a horizontal position and the two cells under it are both empty. In that case the snake moves from (r, c) and (r, c+1) to (r, c) and (r+1, c).

# Rotate counterclockwise if it's in a vertical position and the two cells to its right are both empty. In that case the snake moves from (r, c) and (r+1, c) to (r, c) and (r, c+1).

# Return the minimum number of moves to reach the target.

# If there is no way to reach the target, return -1.

# Solution, O(n*m) time and space (with a real queue)
# BFS all possible moves. Our seen set takes at most n*m values and we spend at most n*m time since we can visit each state once.

class Solution:
    def minimumMoves(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        queue = [ ((0,0),(0,1)) ] # queue holds positions of the snake, tail first then head by coordinates

        seenPositions = set()
        seenPositions.add(((0,0),(0,1)))

        result = 0

        while len(queue) > 0:
            queueLength = len(queue)
            for i in range(queueLength):
                snakePos = queue.pop(0)
                tail, head = snakePos
                tailR, tailC = tail
                headR, headC = head

                if headR == HEIGHT - 1 and headC == WIDTH - 1 and tailR == headR:
                    return result

                # try moving to the right, if we are horizontal
                if headC + 1 < WIDTH and headC == tailC + 1 and grid[headR][headC + 1] < WIDTH and grid[headR][headC + 1] != 1:
                    newHeadPos = (headR, headC + 1)
                    newTailPos = (tailR, tailC + 1)
                    newTup = (newTailPos, newHeadPos)
                    if not newTup in seenPositions:
                        seenPositions.add(newTup)
                        queue.append(newTup)
                # try moving to the right, if we are vertical
                if headC + 1 < WIDTH and headR == tailR + 1 and grid[headR][headC + 1] == 0 and grid[tailR][tailC + 1] == 0:
                    newHeadPos = (headR, headC + 1)
                    newTailPos = (tailR, tailC + 1)
                    newTup = (newTailPos, newHeadPos)
                    if not newTup in seenPositions:
                        seenPositions.add(newTup)
                        queue.append(newTup)
                # try moving down, if we are vertical
                if headR + 1 < HEIGHT and headR == tailR + 1 and grid[headR + 1][headC] < HEIGHT and grid[headR + 1][headC] != 1:
                    newHeadPos = (headR + 1, headC)
                    newTailPos = (tailR + 1, tailC)
                    newTup = (newTailPos, newHeadPos)
                    if not newTup in seenPositions:
                        seenPositions.add(newTup)
                        queue.append(newTup)
                # try moving down, if we are horizontal
                if headR + 1 < HEIGHT and headC == tailC + 1 and grid[headR + 1][headC] == 0 and grid[tailR + 1][tailC] == 0:
                    newHeadPos = (headR + 1, headC)
                    newTailPos = (tailR + 1, tailC)
                    newTup = (newTailPos, newHeadPos)
                    if not newTup in seenPositions:
                        seenPositions.add(newTup)
                        queue.append(newTup)
                # try rotating down if we are horizontal
                if headR + 1 < HEIGHT and headC == tailC + 1 and grid[headR + 1][headC] == 0 and grid[tailR + 1][tailC] == 0:
                    newHeadPos = (tailR + 1, tailC)
                    newTailPos = (tailR, tailC)
                    newTup = (newTailPos, newHeadPos)
                    if not newTup in seenPositions:
                        seenPositions.add(newTup)
                        queue.append(newTup)
                # try rotating up if we are down
                if headC + 1 < WIDTH and headR == tailR + 1 and grid[headR][headC + 1] == 0 and grid[tailR][tailC + 1] == 0:
                    newHeadPos = (tailR, tailC + 1)
                    newTailPos = (tailR, tailC)
                    newTup = (newTailPos, newHeadPos)
                    if not newTup in seenPositions:
                        seenPositions.add(newTup)
                        queue.append(newTup)

            result += 1
        return -1


