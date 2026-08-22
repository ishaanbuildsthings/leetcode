class NumMatrix:

    def __init__(self, matrix: List[List[int]]):
        HEIGHT = len(matrix)
        WIDTH = len(matrix[0])
        # each cell should store the sum for the square from 0,0 to that cell
        self.prefix_sums = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        print(self.prefix_sums)
        for r in range(HEIGHT):
            for c in range(WIDTH):
                # the sum is the left prefix plus the top prefix plus the number, minus the up left prefix
                sum_for_cell = 0
                if r > 0:
                    sum_for_cell += self.prefix_sums[r - 1][c]
                if c > 0:
                    sum_for_cell += self.prefix_sums[r][c - 1]
                sum_for_cell += matrix[r][c]
                if r > 0 and c > 0:
                    sum_for_cell -= self.prefix_sums[r-1][c-1]
                self.prefix_sums[r][c] = sum_for_cell

    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
        # the sum for a region is the bottom right prefix, plus a top left corner prefix, minus a left and a top prefix
        sum_for_region = 0
        sum_for_region += self.prefix_sums[row2][col2]
        if row1 > 0 and col1 > 0:
            sum_for_region += self.prefix_sums[row1 - 1][col1 - 1]
        if col1 > 0:
            sum_for_region -= self.prefix_sums[row2][col1 - 1]
        if row1 > 0:
            sum_for_region -= self.prefix_sums[row1 - 1][col2]
        return sum_for_region

# Your NumMatrix object will be instantiated and called as such:
# obj = NumMatrix(matrix)
# param_1 = obj.sumRegion(row1,col1,row2,col2)