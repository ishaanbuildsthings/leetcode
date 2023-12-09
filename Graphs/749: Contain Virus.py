# https://leetcode.com/problems/contain-virus/description/
# difficulty: hard
# tags: graph, simulation

# Problem
# A virus is spreading rapidly, and your task is to quarantine the infected area by installing walls.

# The world is modeled as an m x n binary grid isInfected, where isInfected[i][j] == 0 represents uninfected cells, and isInfected[i][j] == 1 represents cells contaminated with the virus. A wall (and only one wall) can be installed between any two 4-directionally adjacent cells, on the shared boundary.

# Every night, the virus spreads to all neighboring cells in all four directions unless blocked by a wall. Resources are limited. Each day, you can install walls around only one region (i.e., the affected area (continuous block of infected cells) that threatens the most uninfected cells the following night). There will never be a tie.

# Return the number of walls used to quarantine all the infected regions. If the world will become fully infected, return the number of walls used.

# Solution, just a simulation. My code is not the cleanest, had some bugs. I was happy with my idea of how I stored edges though, and the concept of using the hash function for it. I should read people's short code for this. And work on separation of concerns.

DIFFS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]
class Solution:
    def containVirus(self, isInfected: List[List[int]]) -> int:
        height = len(isInfected)
        width = len(isInfected[0])

        seen = set()
        q = collections.deque()
        for r in range(height):
            for c in range(width):
                if not isInfected[r][c]:
                    continue
                seen.add((r, c))
                q.append((r, c))

        # ensures regardless of the direction of the points the same wall hash is produced
        def hash(r1, c1, r2, c2):
            if r1 < r2:
                return (r1, c1, r2, c2)
            elif r1 == r2 and c1 < c2:
                return (r1, c1, r2, c2)
            return (r2, c2, r1, c1)

        walls = set() # stores (r1, c1, r2, c2) for the two cells it is between

        # scans through the board and quarantines the biggest thread
        def quarantine():

            visitedInfected = set() # prevents double counting an island
            finalCells = set() # the infected cells for the island we quarantine
            maxPerim = 0
            wallsUsed = 0

            # returns the threatened perimeter size
            def dfs(r, c, accCells, visitedEmpty):
                visitedInfected.add((r, c))
                accCells.add((r, c)) # acc cells helps us quarantine the area after
                threatenedPerimeter = 0
                for rowDiff, colDiff in DIFFS:
                    newRow, newCol = r + rowDiff, c + colDiff
                    # skip oob
                    if newRow == height or newRow < 0 or newCol == width or newCol < 0:
                        continue
                    # skip visited
                    if (newRow, newCol) in visitedInfected or (newRow, newCol) in visitedEmpty:
                        continue
                    # skip if a wall blocks us, this can happen if two different regions combined
                    if hash(r, c, newRow, newCol) in walls:
                        continue
                    # if it is a safe cell, add it (we know there is no wall)
                    if not isInfected[newRow][newCol]:
                        threatenedPerimeter += hash(r, c, newRow, newCol) not in walls
                        visitedEmpty.add((newRow, newCol))
                        continue
                    threatenedPerimeter += dfs(newRow, newCol, accCells, visitedEmpty)
                return threatenedPerimeter

            for r in range(height):
                for c in range(width):
                    # skip non viruses
                    if not isInfected[r][c]:
                        continue
                    # skip parts of islands we have already visited
                    if (r, c) in visitedInfected:
                        continue
                    accCells = set()
                    visitedEmpty = set()
                    threatenedPerim = dfs(r, c, accCells, visitedEmpty)
                    if threatenedPerim > maxPerim:
                        maxPerim = threatenedPerim
                        finalCells = accCells
            # quarantine the outside
            for r, c in finalCells:
                for rowDiff, colDiff in DIFFS:
                    newRow, newCol = r + rowDiff, c + colDiff
                    # skip oob
                    if newRow == height or newRow < 0 or newCol == width or newCol < 0:
                        continue
                    # skip infected cells
                    if isInfected[newRow][newCol]:
                        continue
                    # place the wall
                    if hash(r, c, newRow, newCol) not in walls:
                        wallsUsed += 1
                        walls.add(hash(r, c, newRow, newCol))
            return wallsUsed

            # only after pasting this in the IDE I realize I don't use this line of code
            visitedEmpty = set() # helps us not double count threatened empty cells

        res = 0

        while q:
            length = len(q)
            res += quarantine()
            for _ in range(length):
                r, c = q.popleft() # get the cell that is up next
                for rowDiff, colDiff in DIFFS:
                    newRow, newCol = rowDiff + r, colDiff + c
                    # skip out of bounds
                    if newRow == height or newRow < 0 or newCol == width or newCol < 0:
                        continue
                    # skip if there is a wall between
                    if hash(r, c, newRow, newCol) in walls:
                        continue
                    # skip seen
                    if (newRow, newCol) in seen:
                        continue
                    seen.add((newRow, newCol))
                    q.append((newRow, newCol))
                    isInfected[newRow][newCol] = 1

        return res
