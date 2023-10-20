# ______________________________________________________________________
# IMMUTABLE RANGE SUM QUERY TEMPLATE
# Variables:
# ITERABLE - replace with the iterable we need to query
# prefix[i] is the sum of [0:i-1], so prior elements. prefix[len(itertable)] is queryable and returns the entire sum.

runningSum = 0
prefixSums = [] # store sums of PRIOR elements
for num in ITERABLE:
    prefixSums.append(runningSum)
    runningSum += num
prefixSums.append(runningSum)

def sumQuery(l, r):
    return prefixSums[r + 1] - prefixSums[l]

# ______________________________________________________________________
# IMMUTABLE RANGE SUM 2D QUERY TEMPLATE
# Gets the sum for a rectange range query in O(1), after O(n*m) preprocessing
# Variables:
# MATRIX - replace with the 2d matrix we need to query

HEIGHT = len(MATRIX)
WIDTH = len(MATRIX[0])
# each cell should store the sum for the square from 0,0 to that cell
prefix_sums = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
for r in range(HEIGHT):
    for c in range(WIDTH):
        # the sum is the left prefix plus the top prefix plus the number, minus the up left prefix
        sum_for_cell = 0
        if r > 0:
            sum_for_cell += prefix_sums[r - 1][c]
        if c > 0:
            sum_for_cell += prefix_sums[r][c - 1]
        sum_for_cell += MATRIX[r][c]
        if r > 0 and c > 0:
            sum_for_cell -= prefix_sums[r-1][c-1]
        prefix_sums[r][c] = sum_for_cell

# (row1, col1) form the top left point of the rectangle, (row2, col2) bottom right
def sumRegion(row1, col1, row2, col2) -> int:
    # the sum for a region is the bottom right prefix, plus a top left corner prefix, minus a left and a top prefix
    sum_for_region = 0
    sum_for_region += prefix_sums[row2][col2]
    if row1 > 0 and col1 > 0:
        sum_for_region += prefix_sums[row1 - 1][col1 - 1]
    if col1 > 0:
        sum_for_region -= prefix_sums[row2][col1 - 1]
    if row1 > 0:
        sum_for_region -= prefix_sums[row1 - 1][col2]
    return sum_for_region