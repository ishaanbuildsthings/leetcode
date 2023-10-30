# https://leetcode.com/problems/bomb-enemy/description/
# difficulty: medium
# tags: binary search, square root decomp

# Problem
# Given an m x n matrix grid where each cell is either a wall 'W', an enemy 'E' or empty '0', return the maximum enemies you can kill using one bomb. You can only place the bomb in an empty cell.

# The bomb kills all the enemies in the same row and column from the planted point until it hits the wall since it is too strong to be destroyed.

# Solution
# 4 solutions! m*n(m+n) brute force. m*n(root m + root n) sqrt decomp. m*n(log n + log m) binary search. m*n "DP" where we just iterate then track the nuber of enemies in that region and store it in a hashtable. When I wrote code I did the binary search one.

class Solution:
    def maxKilledEnemies(self, grid: List[List[str]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        rows = defaultdict(list) # rows[row] = [left free spot, right free spot, # of people in that range]

        for r in range(HEIGHT):
            rowData = []
            currentLeftFree = None
            c = 0
            enemies = 0
            while c < WIDTH:
                if grid[r][c] == 'E':
                    if currentLeftFree == None:
                        currentLeftFree = c
                    enemies += 1
                elif grid[r][c] == 'W':
                    if currentLeftFree != None:
                        rowData.append([currentLeftFree, c - 1, enemies])
                        currentLeftFree = None
                        enemies = 0
                elif grid[r][c] == '0':
                    if currentLeftFree == None:
                        currentLeftFree = c
                c += 1
            if currentLeftFree != None:
                rowData.append([currentLeftFree, WIDTH - 1, enemies])
            rows[r] = rowData

        cols = defaultdict(list)
        for c in range(WIDTH):
            colData = []
            currentTopFree = None
            r = 0
            enemies = 0
            while r < HEIGHT:
                if grid[r][c] == 'E':
                    if currentTopFree == None:
                        currentTopFree = r
                    enemies += 1
                elif grid[r][c] == 'W':
                    if currentTopFree != None:
                        colData.append([currentTopFree, r - 1, enemies])
                        currentTopFree = None
                        enemies = 0
                elif grid[r][c] == '0':
                    if currentTopFree == None:
                        currentTopFree = r
                r += 1
            if currentTopFree != None:
                colData.append([currentTopFree, HEIGHT - 1, enemies])
            cols[c] = colData

        res = 0
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if grid[r][c] == 'W' or grid[r][c] == 'E':
                    continue
                totalEnemiesInThisCross = 0

                # find the col section we exist in for our given row
                rowBuckets = rows[r]
                left = 0
                right = len(rowBuckets) - 1
                while left <= right:
                    m = (right + left) // 2
                    bucket = rowBuckets[m]
                    start, end, enemies = bucket
                    if c >= start and c <= end:
                        totalEnemiesInThisCross += enemies
                        break
                    elif c > end:
                        left = m + 1
                    elif c < start:
                        right = m - 1

                # find the row section we exist in for our given row
                colBuckets = cols[c]
                left = 0
                right = len(colBuckets) - 1
                while left <= right:
                    m = (right + left) // 2
                    bucket = colBuckets[m]
                    start, end, enemies = bucket
                    if r >= start and r <= end:
                        totalEnemiesInThisCross += enemies
                        break
                    elif r > end:
                        left = m + 1
                    elif r < start:
                        right = m - 1


                res = max(res, totalEnemiesInThisCross)

        return res


