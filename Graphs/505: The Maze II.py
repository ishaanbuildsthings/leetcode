# https://leetcode.com/problems/the-maze-ii/
# difficulty: medium
# tags: graphs, djikstra

# Problem
# There is a ball in a maze with empty spaces (represented as 0) and walls (represented as 1). The ball can go through the empty spaces by rolling up, down, left or right, but it won't stop rolling until hitting a wall. When the ball stops, it could choose the next direction.

# Given the m x n maze, the ball's start position and the destination, where start = [startrow, startcol] and destination = [destinationrow, destinationcol], return the shortest distance for the ball to stop at the destination. If the ball cannot stop at destination, return -1.

# The distance is the number of empty spaces traveled by the ball from the start position (excluded) to the destination (included).

# You may assume that the borders of the maze are all walls (see examples).


# Solution
# Start at our node, and add adjacent possibilities to a heap. At any time, we pop the smallest total distance from the heap. It's like a BFS but we prioritize smallest weighted travels. I also kept a hash map of the smallest distance it takes to reach a cell, so that we can avoid adding duplicates. For instance if we can reach cell X in 10 moves, but we first pop cell A (5 moves to get to cell A) and then cell A can reach X in 7 extra moves, I don't consider it, but if I can reach it in one extra move, I do. Then we can also skip the 10 moves to get to X when we pop that from the heap.

class Solution:
    def shortestDistance(self, maze: List[List[int]], start: List[int], destination: List[int]) -> int:
        print(f'ROOT CALL')
        HEIGHT = len(maze)
        WIDTH = len(maze[0])

        def getAdjLocations(r, c):
            adjLocations = []
            # go up
            upFound = False
            for newRow in range(r - 1, -1, -1):
                if maze[newRow][c] == 1:
                    if newRow != r - 1:
                        adjLocations.append([newRow + 1, c])
                    upFound = True
                    break
            # add boundary if not hit
            if not upFound:
                adjLocations.append([0, c])

            # go down
            downFound = False
            for newRow in range(r + 1, HEIGHT):
                if maze[newRow][c] == 1:
                    if newRow != r + 1:
                        adjLocations.append([newRow - 1, c])
                    downFound = True
                    break
            # add boundary if not hit
            if not downFound:
                adjLocations.append([HEIGHT - 1, c])

            # go left
            leftFound = False
            for newCol in range(c - 1, -1, -1):
                if maze[r][newCol] == 1:
                    if newCol != c - 1:
                        adjLocations.append([r, newCol + 1])
                    leftFound = True
                    break
            # add boundary if not hit
            if not leftFound:
                adjLocations.append([r, 0])

            # go right
            rightFound = False
            for newCol in range(c + 1, WIDTH):
                if maze[r][newCol] == 1:
                    if newCol != c + 1:
                        adjLocations.append([r, newCol - 1])
                    rightFound = True
                    break
            # add boundary if not hit
            if not rightFound:
                adjLocations.append([r, WIDTH - 1])

            # filter same locations
            finalAdjs = []
            for adjR, adjC in adjLocations:
                if adjR == r and adjC == c:
                    continue
                finalAdjs.append([adjR, adjC])
            return finalAdjs

        # store [distance traveled, r, c]
        heap = []
        heap.append([0, start[0], start[1]])
        seen = defaultdict(lambda: float('inf')) # maps a cell to the lowest distance it has ever had
        key = start[0] * WIDTH + start[1]
        seen[key] = 0

        while True:
            if not heap:
                return -1
            shortestDistance, r, c = heapq.heappop(heap)

            if r == destination[0] and c == destination[1]:
                return shortestDistance

            key = r * WIDTH + c

            # extra pruning in case at one point we found a better state t
            if seen[key] < shortestDistance:
                continue

            adjLocations = getAdjLocations(r, c)
            for adjR, adjC in adjLocations:
                adjKey = adjR * WIDTH + adjC
                adjLowestDistanceToGetThere = seen[adjKey]

                dist = abs(adjR - r) + abs(adjC - c)
                if dist + shortestDistance >= adjLowestDistanceToGetThere:
                    continue
                seen[adjKey] = dist + shortestDistance
                heapq.heappush(heap, [dist + shortestDistance, adjR, adjC])


# D 0 1 0 S
# 0 0 0 0 0
# 0 0 0 1 0
# 1 1 0 1 1
# 0 0 0 0 0
