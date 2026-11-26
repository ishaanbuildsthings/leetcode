# https://leetcode.com/problems/minimum-time-takes-to-reach-destination-without-drowning/description/
# Difficulty: Hard
# Tags: matrix bfs

# Problem
# You are given an n * m 0-indexed grid of string land. Right now, you are standing at the cell that contains "S", and you want to get to the cell containing "D". There are three other types of cells in this land:

# ".": These cells are empty.
# "X": These cells are stone.
# "*": These cells are flooded.
# At each second, you can move to a cell that shares a side with your current cell (if it exists). Also, at each second, every empty cell that shares a side with a flooded cell becomes flooded as well.
# There are two problems ahead of your journey:

# You can't step on stone cells.
# You can't step on flooded cells since you will drown (also, you can't step on a cell that will be flooded at the same time as you step on it).
# Return the minimum time it takes you to reach the destination in seconds, or -1 if it is impossible.

# Note that the destination will never be flooded.

# Solution, O(m*n) time and space if using a real queue.
# Just bfs the people and water at the same time. Record seen people and water to not overlap. We check n*m cells and at most 4 directions.

class Solution:
    def minimumSeconds(self, land: List[List[str]]) -> int:
        HEIGHT = len(land)
        WIDTH = len(land[0])

        seenWater = set()
        seenPeople = set()

        waterQueue = []

        for r in range(HEIGHT):
            for c in range(WIDTH):
                if land[r][c] == 'S':
                    personQueue = [[r, c]]
                    seenPeople.add(r * WIDTH + c)
                elif land[r][c] == '*':
                    waterQueue.append([r, c])
                    seenWater.add(r * WIDTH + c)
                elif land[r][c] == 'D':
                    goal = [r, c]

        # edge case, we start there
        if personQueue[0][0] == goal[0] and personQueue[0][1] == goal[1]:
            return 0

        result = 0

        diffs = [[1,0], [-1,0], [0,1], [0,-1] ]

        while len(personQueue) > 0:
            result += 1
            # bfs the water first
            waterLength = len(waterQueue)
            for i in range(waterLength):
                r, c = waterQueue.pop(0)
                for rowDiff, colDiff in diffs:
                    newRow = rowDiff + r
                    newCol = colDiff + c
                    key = WIDTH * newRow + newCol
                    # skip out of bounds
                    if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                        continue
                    # skip seen water
                    if key in seenWater:
                        continue
                    # skip cells that are stones, no need to skip water because that's handled in seenWater
                    if land[newRow][newCol] == 'X':
                        continue
                    # cannot flood the destination
                    if land[newRow][newCol] == 'D':
                        continue
                    seenWater.add(key)
                    waterQueue.append([newRow, newCol])

            # bfs the people
            personLength = len(personQueue)
            for i in range(personLength):
                r, c = personQueue.pop(0)
                for rowDiff, colDiff in diffs:
                    newRow = rowDiff + r
                    newCol = colDiff + c
                    key = WIDTH * newRow + newCol
                    # skip out of bounds
                    if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                        continue
                    # skip seen water
                    if key in seenWater:
                        continue
                    # skip seen people
                    if key in seenPeople:
                        continue
                    # skip cells that are stones, no need to skip water because that's handled in seenWater
                    if land[newRow][newCol] == 'X':
                        continue
                    # reach the destiation
                    if land[newRow][newCol] == 'D':
                        return result
                    seenPeople.add(key)
                    personQueue.append([newRow, newCol])

        return -1


            # X X _
            # D X S
            # _ _ X


