# https://leetcode.com/problems/rank-transform-of-an-array/description/
# difficulty: easy

# Problem
# Given an array of integers arr, replace each element with its rank.

# The rank represents how large the element is. The rank has the following rules:

# Rank is an integer starting from 1.
# The larger the element, the larger the rank. If two elements are equal, their rank must be the same.
# Rank should be as small as possible.

# Solution
# I sorted then solved, but I did it kind of poorly. I can just sort without zipping the indices, map a number to its rank, then write the answer.

class Solution:
    def arrayRankTransform(self, arr: List[int]) -> List[int]:
        if not arr:
            return []

        # stores a number to its original index
        zipped = sorted(
            [
                (arr[i], i)
                for i in range(len(arr))
            ])

        res = [None] * len(arr)


        smallest, originalIndex = zipped[0]
        res[originalIndex] = 1

        rank = 1
        for i in range(1, len(zipped)):
            val, originalIdx = zipped[i]
            if val != zipped[i - 1][0]:
                rank += 1
            res[originalIdx] = rank

        return res


