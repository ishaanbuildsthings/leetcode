# https://leetcode.com/problems/max-sum-of-rectangle-no-larger-than-k/
# Difficulty: hard
# Tags: binary search, avl, prefix, range query

# Problem
# Given an m x n matrix matrix and an integer k, return the max sum of a rectangle in the matrix such that its sum is no larger than k.

# It is guaranteed that there will be a rectangle with a sum no larger than k.

# Solution
# Think of the 1d variant, we can keep a sorted list and query the max prefix to cut off. To that, but in 2d, meaning we also need variable widths, and variable starting locations. It is of the order n^3 * log n, though optimizations can be made based on if n or m is smaller. The storage is n*m for the prefixes.

import sortedcontainers

class Solution:
    def maxSumSubmatrix(self, matrix: List[List[int]], k: int) -> int:
        HEIGHT = len(matrix)
        WIDTH = len(matrix[0])

        def smallestGTE(avl, num):
            index = avl.bisect_left(num)
            if index < len(avl):
                return avl[index]
            else:
                return None

        prefix = defaultdict(list) # maps a row to prefix sums
        for r in range(HEIGHT):
            running = 0
            for c in range(WIDTH):
                running += matrix[r][c]
                prefix[r].append(running)

        def querySum(prefixRow, l, r):
            if l == 0:
                return prefixRow[r]
            return prefixRow[r] - prefixRow[l - 1]

        res = float('-inf')

        for width in range(1, WIDTH + 1):
            for leftOffset in range(WIDTH - width + 1):
                l = leftOffset
                r = leftOffset + width - 1
                avl = sortedcontainers.SortedList()
                avl.add(0)
                running = 0
                for i in range(HEIGHT):
                    rowAddition = querySum(prefix[i], l, r)
                    running += rowAddition
                    # if we have 10 and k=30, we can remove >= -20
                    smallestRemoval = running - k # if we have 20 and k=15, we can remove >= 5
                    optimalRemoval = smallestGTE(avl, smallestRemoval)
                    if optimalRemoval != None:
                        newAmount = running - optimalRemoval
                        res = max(res, newAmount)

                    # goes after, since we are not allowed to remove everything
                    avl.add(running)

        return res




