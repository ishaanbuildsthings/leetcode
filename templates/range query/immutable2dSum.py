
# ______________________________________________________________________
# IMMUTABLE RANGE SUM 2D QUERY TEMPLATE
# Gets the sum for a rectange range query in O(1), after O(n*m) preprocessing
# Variables:
# MATRIX - replace with the 2d matrix we need to query

HEIGHT = len(MATRIX)
WIDTH = len(MATRIX[0])
# each cell should store the sum for the square from 0,0 to that cell
prefixSums = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
for r in range(HEIGHT):
    for c in range(WIDTH):
        # the sum is the left prefix plus the top prefix plus the number, minus the up left prefix
        sumForCell = 0
        if r > 0:
            sumForCell += prefixSums[r - 1][c]
        if c > 0:
            sumForCell += prefixSums[r][c - 1]
        sumForCell += MATRIX[r][c]
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