# https://leetcode.com/problems/find-all-groups-of-farmland/description/
# difficulty: medium

# Problem
# You are given a 0-indexed m x n binary matrix land where a 0 represents a hectare of forested land and a 1 represents a hectare of farmland.

# To keep the land organized, there are designated rectangular areas of hectares that consist entirely of farmland. These rectangular areas are called groups. No two groups are adjacent, meaning farmland in one group is not four-directionally adjacent to another farmland in a different group.

# land can be represented by a coordinate system where the top left corner of land is (0, 0) and the bottom right corner of land is (m-1, n-1). Find the coordinates of the top left and bottom right corner of each group of farmland. A group of farmland with a top left corner at (r1, c1) and a bottom right corner at (r2, c2) is represented by the 4-length array [r1, c1, r2, c2].

# Return a 2D array containing the 4-length arrays described above for each group of farmland in land. If there are no groups of farmland, return an empty array. You may return the answer in any order.


# Solution, I tracked seen cells and searched the edges. Can maybe be faster with preprocessing but I am writing this solution a while after solving it

class Solution:
    def findFarmland(self, land: List[List[int]]) -> List[List[int]]:
        HEIGHT = len(land)
        WIDTH = len(land[0])

        seen = [ [False for _ in range(WIDTH)] for _ in range(HEIGHT) ]

        DIFFS = [ [-1, 0], [1, 0], [-1, 0], [1, 0] ]

        def search(topR, leftC):
            findBottomR = topR
            while findBottomR < HEIGHT and land[findBottomR][leftC] == 1:
                findBottomR += 1
            findBottomR -= 1
            findRightC = leftC
            while findRightC < WIDTH and land[topR][findRightC] == 1:
                findRightC += 1
            findRightC -= 1
            return [findBottomR, findRightC]

        res = []

        for r in range(HEIGHT):
            for c in range(WIDTH):
                if seen[r][c]:
                    continue
                if land[r][c] == 0:
                    continue
                bottomR, rightC = search(r, c)
                for rowSeen in range(r, bottomR + 1):
                    for colSeen in range(c, rightC + 1):
                        seen[rowSeen][colSeen] = True
                res.append([r, c, bottomR, rightC])
        return res


        # 1 1 0 0 0 1
        # 1 1 0 0 0 0