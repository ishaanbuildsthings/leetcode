# https://leetcode.com/problems/row-with-maximum-ones/
# Difficulty: Easy

# Problem
# Given a m x n binary matrix mat, find the 0-indexed position of the row that contains the maximum count of ones, and the number of ones in that row.

# In case there are multiple rows that have the maximum count of ones, the row with the smallest row number should be selected.

# Return an array containing the index of the row, and the number of ones in it.

# Solution, O(m*n) time, O(1) space
# Just iterate and count each row

class Solution:
    def rowAndMaximumOnes(self, mat: List[List[int]]) -> List[int]:
        result_row = 0
        max_count = 0
        HEIGHT = len(mat)
        WIDTH = len(mat[0])
        for r in range(HEIGHT):
            count = 0
            for c in range(WIDTH):
                if mat[r][c] == 1:
                    count += 1
            if count > max_count:
                max_count = count
                result_row = r
        return [result_row, max_count]

