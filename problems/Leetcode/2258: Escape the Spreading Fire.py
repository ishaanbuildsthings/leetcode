# https://leetcode.com/problems/escape-the-spreading-fire/description/
# Difficulty: Hard
# tags: matrix bfs, binary search

# Problem
# You are given a 0-indexed 2D integer array grid of size m x n which represents a field. Each cell has one of three values:

# 0 represents grass,
# 1 represents fire,
# 2 represents a wall that you and fire cannot pass through.
# You are situated in the top-left cell, (0, 0), and you want to travel to the safehouse at the bottom-right cell, (m - 1, n - 1). Every minute, you may move to an adjacent grass cell. After your move, every fire cell will spread to all adjacent cells that are not walls.

# Return the maximum number of minutes that you can stay in your initial position before moving while still safely reaching the safehouse. If this is impossible, return -1. If you can always reach the safehouse regardless of the minutes stayed, return 109.

# Note that even if the fire spreads to the safehouse immediately after you have reached it, it will be counted as safely reaching the safehouse.

# A cell is adjacent to another cell if the former is directly north, east, south, or west of the latter (i.e., their sides are touching).

# Solution, O(m*n) * log(m*n) time, O(m*n) space
# If we know to wait a specific time, we can wait, bfs the fire out, then bfs the fire and people at the same time to see if we can escape. Normally we cannot enter a cell the same time dire enters that cell, unless it is the safe house. I just recorded the first time fire hits the safe house and used this to determine if we are safe, though there's better pruning. Each verification takes m*n time (using a real queue) since worst case our bfs takes m*n cells. Maintain visited sets for both people and fire to not overlap cases. If we can escape in that time, try waiting for longer. Our binary search upper boundary is also m*n.

class Solution:
    def maximumMinutes(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        fireCoords = []
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if grid[r][c] == 1:
                    fireCoords.append([r,c])

        # seeing if we can reach the end will at worst case take m*n time as we travel through every cell, which is roughly 10^5
        # we have to binary search check this, fire can worst case reach us in m*n time, so our binary search range is l=0 r=10^5

        def checkCanEscapeAfterWaitingTime(time):
            fireQueue = fireCoords.copy()
            seenFires = set() # visited
            for tup in fireQueue:
                seenFires.add(f'{tup[0]},{tup[1]}')

            diffs = [[1,0], [-1,0], [0,1], [0,-1] ]

            timeUsed = 0
            # spread the fires during waiting time
            while timeUsed < time:
                timeUsed += 1
                fireLength = len(fireQueue)
                # simulate one unit of time for fire
                for i in range(fireLength):
                    firePos = fireQueue.pop(0)
                    # print(f'fire pos {firePos}')
                    r, c = firePos
                    # move the fire adjacent
                    for rowDiff, colDiff in diffs:
                        newRow = r + rowDiff
                        newCol = c + colDiff
                        # skip fires that go out of bounds
                        if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                            continue
                        # skip fires that touch walls
                        if grid[newRow][newCol] == 2:
                            continue
                        # skip fires that touch existing fires
                        if f'{newRow},{newCol}' in seenFires:
                            continue
                        # early prune, if we can burn the safe house or the person (might be needed)
                        if (newRow == HEIGHT - 1 and newCol == WIDTH - 1) or (newRow == 0 and newCol == 0):
                            return False
                        seenFires.add(f'{newRow},{newCol}')
                        fireQueue.append([newRow, newCol])

            # bfs people and fire at the same time
            visited = set() # don't overlap cells for people, if we could arrive to a cell before no reason to try a later path
            # now check if the person can escape
            visited.add(f'{0},{0}')
            personQueue = [[0,0]]
            earliestFireSafeHouse = float('inf')
            while len(personQueue) > 0:
                timeUsed += 1
                # bfs fire
                fireLength = len(fireQueue)
                # simulate one unit of time for fire
                for i in range(fireLength):
                    firePos = fireQueue.pop(0)
                    r, c = firePos
                    # move the fire adjacent
                    for rowDiff, colDiff in diffs:
                        newRow = r + rowDiff
                        newCol = c + colDiff
                        # skip fires that go out of bounds
                        if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                            continue
                        # skip fires that touch walls
                        if grid[newRow][newCol] == 2:
                            continue
                        # skip fires that touch existing fires
                        if f'{newRow},{newCol}' in seenFires:
                            continue
                        # if we can burn the safe house, record the time
                        if newRow == HEIGHT - 1 and newCol == WIDTH - 1:
                            earliestFireSafeHouse = min(earliestFireSafeHouse, timeUsed)
                        seenFires.add(f'{newRow},{newCol}')
                        fireQueue.append([newRow, newCol])


                # simulate one unit of time for people
                length = len(personQueue)
                for i in range(length):
                    tup = personQueue.pop(0)
                    r, c = tup
                    for rowDiff, colDiff in diffs:
                        newRow = r + rowDiff
                        newCol = c + colDiff
                        # skip spots that go out of bounds
                        if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                            continue
                        # skip spots that touch walls
                        if grid[newRow][newCol] == 2:
                            continue
                        # skip spots that are fire unless it's the safe house (we will check time)
                        if f'{newRow},{newCol}' in seenFires and (not (newRow == HEIGHT - 1 and newCol == WIDTH - 1)):
                            continue
                        # skip spots that we already could visit
                        if f'{newRow},{newCol}' in visited:
                            continue
                        # we win if we reach the house in time
                        if newRow == HEIGHT - 1 and newCol == WIDTH - 1 and timeUsed <= earliestFireSafeHouse:
                            return True

                        visited.add(f'{newRow},{newCol}')
                        personQueue.append([newRow,newCol])

            return False

        l = 0
        r = HEIGHT * WIDTH
        while l <= r:
            m = (r + l) // 2 # m is the units of time we test
            # if we can escape in time, try waiting longer
            if checkCanEscapeAfterWaitingTime(m):
                l = m + 1
            else:
                r = m - 1
        # if the amount of time we can wait is the amount of cells in the grid, we can always escape
        if r == HEIGHT * WIDTH:
            return 10**9
        return r






