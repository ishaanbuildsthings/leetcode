# https://leetcode.com/problems/champagne-tower/description/?envType=daily-question&envId=2023-09-24
# difficulty: medium
# tags: dynamic programming 2d

# problem
# We stack glasses in a pyramid, where the first row has 1 glass, the second row has 2 glasses, and so on until the 100th row.  Each glass holds one cup of champagne.

# Then, some champagne is poured into the first glass at the top.  When the topmost glass is full, any excess liquid poured will fall equally to the glass immediately to the left and right of it.  When those glasses become full, any excess champagne will fall equally to the left and right of those glasses, and so on.  (A glass at the bottom row has its excess champagne fall on the floor.)

# For example, after one cup of champagne is poured, the top most glass is full.  After two cups of champagne are poured, the two glasses on the second row are half full.  After three cups of champagne are poured, those two cups become full - there are 3 full glasses total now.  After four cups of champagne are poured, the third row has the middle glass half full, and the two outside glasses are a quarter full, as pictured below.

# Solution, O(n^2) time and space
# We start by pouring a bunch of liquid into the top cup. For each cup, we gain excess from the cups above it. So for the cup we need to query, we look at the 2 cups above it, and sum half of their excesses.

class Solution:
    def champagneTower(self, poured: int, query_row: int, query_glass: int) -> float:
        # # at most we query 100 total tows, which is 101*50 = 5050 total volume to fill all those rows

        # now, our glass may not be full

        # every cup gets half of the excess of each cup above it, we want our recurse to return the total volume it gets
        @cache
        def recurse(row, col):
            # base case
            if row == 0 and col == 0:
                return poured

            # edge case
            if row == -1:
                return 0
            if col == row + 1:
                return 0

            totalFromUpLeft = recurse(row - 1, col - 1)
            excessUpLeft = max((totalFromUpLeft - 1), 0) / 2
            totalFromUpRight = recurse(row - 1, col)
            excessUpRight = max((totalFromUpRight - 1), 0) / 2
            newCupTotal = excessUpLeft + excessUpRight
            return newCupTotal
            volInCup = 0.5 * excessFromUpLeft + 0.5 * excessFromUpRight
            return max(volInCup - 1, 0)

        total = recurse(query_row, query_glass)
        return total if total <= 1 else 1





