# https://leetcode.com/problems/range-sum-query-2d-mutable/description/
# difficulty: hard
# tags: range query, square root decomposition, binary indexed tree, segment tree

# Problem
# Given a 2D matrix matrix, handle multiple queries of the following types:

# Update the value of a cell in matrix.
# Calculate the sum of the elements of matrix inside the rectangle defined by its upper left corner (row1, col1) and lower right corner (row2, col2).
# Implement the NumMatrix class:

# NumMatrix(int[][] matrix) Initializes the object with the integer matrix matrix.
# void update(int row, int col, int val) Updates the value of matrix[row][col] to be val.
# int sumRegion(int row1, int col1, int row2, int col2) Returns the sum of the elements of matrix inside the rectangle defined by its upper left corner (row1, col1) and lower right corner (row2, col2).

# Solution
# O(m*n) init, O(1) update, O(root m * root n) range sum time. O(root m * root n) space, or O(m*n) space if we reallocate the matrix. O(1) space for update and range sum.

# We simply divide the grid into boxes of width sqrt(grid width) and height sqrt(grid height). We map each box to its sum. When we update, we update the sum of that box. I also update the original grid cell and use the prior value to know how much to increase or decrease the box sum by.
# When we do a query, we sum up the boxes, as well as extra cells on the top, right, bottom, and left.

class NumMatrix:

    def __init__(self, matrix: List[List[int]]):
        self.matrix = matrix
        HEIGHT = len(matrix)
        WIDTH = len(matrix[0])
        self.heightBucketSize = math.floor(math.sqrt(HEIGHT))
        self.widthBucketSize = math.floor(math.sqrt(WIDTH))
        numberOfHeightBuckets = math.ceil(HEIGHT / self.heightBucketSize)
        numberOfWidthBuckets = math.ceil(WIDTH / self.widthBucketSize)
        self.buckets = defaultdict(int) # maps a key 'bucketRow,bucketCol' to its sum
        for r in range(HEIGHT):
            bucketRow = math.ceil((r + 1) / self.heightBucketSize)
            for c in range(WIDTH):
                bucketCol = math.ceil((c + 1) / self.widthBucketSize)
                key = f'{bucketRow},{bucketCol}'
                self.buckets[key] += matrix[r][c]



    def update(self, row: int, col: int, val: int) -> None:
        bucketRow = math.ceil((row + 1) / self.heightBucketSize)
        bucketCol = math.ceil((col + 1) / self.widthBucketSize)
        key = f'{bucketRow},{bucketCol}'
        prev = self.matrix[row][col]
        diff = val - prev
        self.buckets[key] += diff
        self.matrix[row][col] = val

    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
        width = col2 - col1 + 1
        height = row2 - row1 + 1
        regionSum = 0
        if width <= self.widthBucketSize or height <= self.heightBucketSize:
            for r in range(row1, row2 + 1):
                for c in range(col1, col2 + 1):
                    regionSum += self.matrix[r][c]
            return regionSum

        firstSafeRowIndex = None # helps with edge cases due to partial buckets I believe
        firstSafeColIndex = None
        lastSafeRowIndex = None
        lastSafeColIndex = None

        for i in range(col1, col1 + self.widthBucketSize + 1):
            if i % self.widthBucketSize == 0:
                firstSafeColIndex = i
                break

        for i in range(row1, row1 + self.heightBucketSize + 1):
            if i % self.heightBucketSize == 0:
                firstSafeRowIndex = i
                break

        for i in range(col1, col1 + self.widthBucketSize + 1):
            if i % self.widthBucketSize == 0 and i + self.widthBucketSize - 1 <= col2:
                lastSafeColIndex = i

        for i in range(row1, row1 + self.heightBucketSize + 1):
            if i % self.heightBucketSize == 0 and i + self.heightBucketSize - 1 <= row2:
                lastSafeRowIndex = i

        if firstSafeRowIndex == None or firstSafeColIndex == None or lastSafeColIndex == None or lastSafeRowIndex == None:
            for r in range(row1, row2 + 1):
                for c in range(col1, col2 + 1):
                    regionSum += self.matrix[r][c]
            return regionSum

        # add all the buckets we can
        for r in range(firstSafeRowIndex, lastSafeRowIndex + 1, self.heightBucketSize):
            bucketRow = math.ceil((r + 1) / self.heightBucketSize)
            for c in range(firstSafeColIndex, lastSafeColIndex + 1, self.widthBucketSize):
                bucketCol = math.ceil((c + 1) / self.widthBucketSize)
                key = f'{bucketRow},{bucketCol}'
                regionSum += self.buckets[key]

        # add all rows above the first safe
        for r in range(row1, firstSafeRowIndex):
            for c in range(col1, col2 + 1):
                regionSum += self.matrix[r][c]

        # add all rows below first safe row
        for r in range(lastSafeRowIndex + self.heightBucketSize, row2 + 1):
            for c in range(col1, col2 + 1):
                regionSum += self.matrix[r][c]

        # add all to the left of the first column, within the boundary rows
        for r in range(firstSafeRowIndex, lastSafeRowIndex + self.heightBucketSize):
            for c in range(col1, firstSafeColIndex):
                regionSum += self.matrix[r][c]

        # add to the right of the last column, within the boundary rows
        for r in range(firstSafeRowIndex, lastSafeRowIndex + self.heightBucketSize):
            for c in range(lastSafeColIndex + self.widthBucketSize, col2 + 1):
                regionSum += self.matrix[r][c]

        return regionSum


# Your NumMatrix object will be instantiated and called as such:
# obj = NumMatrix(matrix)
# obj.update(row,col,val)
# param_2 = obj.sumRegion(row1,col1,row2,col2)