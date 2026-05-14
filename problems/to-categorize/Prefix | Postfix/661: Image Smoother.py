# https://leetcode.com/problems/image-smoother/description/?envType=daily-question&envId=2023-12-19
# difficulty: easy
# tags: range query, prefix

# Problem
# An image smoother is a filter of the size 3 x 3 that can be applied to each cell of an image by rounding down the average of the cell and the eight surrounding cells (i.e., the average of the nine cells in the blue smoother). If one or more of the surrounding cells of a cell is not present, we do not consider it in the average (i.e., the average of the four cells in the red smoother).


# Given an m x n integer matrix img representing the grayscale of an image, return the image after applying the smoother on each cell of it.

# Solution
# O(n*m) time and space, generalized for any size smoothing

FILTER_SIDE_LENGTH = 3
class Solution:
    def imageSmoother(self, img: List[List[int]]) -> List[List[int]]:
        matHeight = len(img)
        matWidth = len(img[0])
        # each cell should store the sum for the square from 0,0 to that cell
        prefixSums = [[0 for _ in range(matWidth)] for _ in range(matHeight)]
        for r in range(matHeight):
            for c in range(matWidth):
                # the sum is the left prefix plus the top prefix plus the number, minus the up left prefix
                sumForCell = 0
                if r > 0:
                    sumForCell += prefixSums[r - 1][c]
                if c > 0:
                    sumForCell += prefixSums[r][c - 1]
                sumForCell += img[r][c]
                if r > 0 and c > 0:
                    sumForCell -= prefixSums[r-1][c-1]
                prefixSums[r][c] = sumForCell

        # (row1, col1) form the top left point of the rectangle, (row2, col2) bottom right
        def sumRegion(row1, col1, row2, col2) -> int:
            # the sum for a region is the bottom right prefix, plus a top left corner prefix, minus a left and a top prefix
            sumForRegion = 0
            sumForRegion += prefixSums[row2][col2]
            if row1 > 0 and col1 > 0:
                sumForRegion += prefixSums[row1 - 1][col1 - 1]
            if col1 > 0:
                sumForRegion -= prefixSums[row2][col1 - 1]
            if row1 > 0:
                sumForRegion -= prefixSums[row1 - 1][col2]
            return sumForRegion

        res = [[0] * matWidth for _ in range(matHeight)]
        for r in range (matHeight):
            for c in range (matWidth):
                filterOffset = int((FILTER_SIDE_LENGTH - 1) / 2)
                left = max(0, c - filterOffset)
                top = max(0, r - filterOffset)
                bottom = min(matHeight - 1, r + filterOffset)
                right = min(matWidth - 1, c + filterOffset)
                height = bottom - top + 1
                width = right - left + 1
                res[r][c] = int(sumRegion(top, left, bottom, right) / (height * width))
        return res