# https://leetcode.com/problems/grid-illumination/description/
# difficulty: hard

# Problem
# There is a 2D grid of size n x n where each cell of this grid has a lamp that is initially turned off.

# You are given a 2D array of lamp positions lamps, where lamps[i] = [rowi, coli] indicates that the lamp at grid[rowi][coli] is turned on. Even if the same lamp is listed more than once, it is turned on.

# When a lamp is turned on, it illuminates its cell and all other cells in the same row, column, or diagonal.

# You are also given another 2D array queries, where queries[j] = [rowj, colj]. For the jth query, determine whether grid[rowj][colj] is illuminated or not. After answering the jth query, turn off the lamp at grid[rowj][colj] and its 8 adjacent lamps if they exist. A lamp is adjacent if its cell shares either a side or corner with grid[rowj][colj].

# Return an array of integers ans, where ans[j] should be 1 if the cell in the jth query was illuminated, or 0 if the lamp was not.


# Solution
# Just get the rows, columns, and diagonals for counts of illumination, turn off as needed and update.

DIFFS = [ [1, 1], [1, 0], [1, -1], [0, 1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 0] ]

class Solution:
    def gridIllumination(self, n: int, lamps: List[List[int]], queries: List[List[int]]) -> List[int]:
        rows = defaultdict(int)
        cols = defaultdict(int)
        majors = defaultdict(int) # the row-col surplus
        minors = defaultdict(int) # the sum of r and c

        lamps = list(set((r, c) for r, c in lamps)) # fast remove duplicates, can be done within the on set

        on = set((r, c) for r, c in lamps)

        for r, c in lamps:
            rows[r] += 1
            cols[c] += 1
            majors[r - c] += 1
            minors[r + c] += 1

        res = []
        for r, c in queries:
            # if nothing can illuminate this, we are illuminated
            if not rows[r] and not cols[c] and not majors[r - c] and not minors[r + c]:
                res.append(0)
                continue

            # if we had a chance to be on, check the adjacents
            for rowDiff, colDiff in DIFFS:
                newRow = r + rowDiff
                newCol = c + colDiff
                # skip out of bounds
                if newRow < 0 or newRow == n or newCol < 0 or newCol == n:
                    continue
                # skip off lamps
                if not (newRow, newCol) in on:
                    continue

                # turn off
                on.remove((newRow, newCol))
                rows[newRow] -= 1
                cols[newCol] -= 1
                majors[newRow - newCol] -= 1
                minors[newRow + newCol] -= 1
            res.append(1)

        return res


        # 0 0 0 X 0 X
        # X 0 0 0 X 0
        # 0 0 0 0 0 X
        # 0 0 0 0 0 0
        # 0 0 X 0 0 0
        # 0 0 0 0 0 0