# https://leetcode.com/problems/number-of-laser-beams-in-a-bank/description/?envType=daily-question&envId=2024-01-03
# difficulty: medium

# Problem
# Anti-theft security devices are activated inside a bank. You are given a 0-indexed binary string array bank representing the floor plan of the bank, which is an m x n 2D matrix. bank[i] represents the ith row, consisting of '0's and '1's. '0' means the cell is empty, while'1' means the cell has a security device.

# There is one laser beam between any two security devices if both conditions are met:

# The two devices are located on two different rows: r1 and r2, where r1 < r2.
# For each row i where r1 < i < r2, there are no security devices in the ith row.
# Laser beams are independent, i.e., one beam does not interfere nor join with another.

# Return the total number of laser beams in the bank.

# Solution
# Just a basic logic puzzle, can do with O(1) space too

class Solution:
    def numberOfBeams(self, bank: List[str]) -> int:
        height = len(bank)
        width = len(bank[0])

        # can do it with O(1) space
        rowTotals = []
        for r, row in enumerate(bank):
            total = sum(int(cell) for cell in row)
            if total != 0:
                rowTotals.append(total)
        res = 0
        for i, total in enumerate(rowTotals):
            if i != 0:
                res += total * rowTotals[i - 1]
        return res