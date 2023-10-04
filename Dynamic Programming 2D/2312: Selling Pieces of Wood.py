# https://leetcode.com/problems/selling-pieces-of-wood/
# difficulty: hard
# tags: dynamic programming 2d

# problem
# You are given two integers m and n that represent the height and width of a rectangular piece of wood. You are also given a 2D integer array prices, where prices[i] = [hi, wi, pricei] indicates you can sell a rectangular piece of wood of height hi and width wi for pricei dollars.

# To cut a piece of wood, you must make a vertical or horizontal cut across the entire height or width of the piece to split it into two smaller pieces. After cutting a piece of wood into some number of smaller pieces, you can sell pieces according to prices. You may sell multiple pieces of the same shape, and you do not have to sell all the shapes. The grain of the wood makes a difference, so you cannot rotate a piece to swap its height and width.

# Return the maximum money you can earn after cutting an m x n piece of wood.

# Note that you can cut the piece of wood as many times as you want.

# Solution, O(m*n*(m+n)) time, O(m*n) space
# To solve an m*n state, we can try up to m+n cuts. So try each one. My fastest solve on a "very hard" problem (2300+ elo), almost got it first try too.

class Solution:
    def sellingWood(self, m: int, n: int, prices: List[List[int]]) -> int:
        HEIGHT = m
        WIDTH = n

        priceMap = [[-1 for _ in range(HEIGHT + 1)] for _ in range(WIDTH + 1)]
        for h, w, price in prices:
            priceMap[w][h] = price

        @cache
        def dp(width, height):
            # base case, no cuts can be made
            if width == 1 and height == 1:
                return max(0, priceMap[1][1])

            resForThis = max(0, priceMap[width][height])
            for verticalCut in range(width - 1):
                leftRegionWidth = verticalCut + 1
                rightRegionWidth = width - leftRegionWidth
                ifCutHere = dp(leftRegionWidth, height) + dp(rightRegionWidth, height)
                resForThis = max(resForThis, ifCutHere)
            for horizontalCut in range(height - 1):
                topRegionHeight = horizontalCut + 1
                bottomRegionHeight = height - topRegionHeight
                ifCutHere = dp(width, topRegionHeight) + dp(width, bottomRegionHeight)
                resForThis = max(resForThis, ifCutHere)

            return resForThis

        return dp(WIDTH, HEIGHT)
