# https://leetcode.com/problems/minimum-operations-to-make-a-uni-value-grid/description/
# difficulty: medium

# Problem
# You are given a 2D integer grid of size m x n and an integer x. In one operation, you can add x to or subtract x from any element in the grid.

# A uni-value grid is a grid where all the elements of it are equal.

# Return the minimum number of operations to make the grid uni-value. If it is not possible, return -1.

# Solution, it's the median if they all have the same parity
class Solution:
    def minOperations(self, grid: List[List[int]], x: int) -> int:
        vals = [val for row in grid for val in row]
        for i in range(1, len(vals)):
            if (vals[i] - vals[i - 1]) % x != 0:
                return -1
        vals.sort()
        median = vals[len(vals) // 2]
        return sum(abs(median - val) // x for val in vals)