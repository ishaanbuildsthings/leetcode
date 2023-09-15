# https://leetcode.com/problems/maximize-the-beauty-of-the-garden/
# Difficulty: Hard
# Tags: prefix

# Problem
# There is a garden of n flowers, and each flower has an integer beauty value. The flowers are arranged in a line. You are given an integer array flowers of size n and each flowers[i] represents the beauty of the ith flower.

# A garden is valid if it meets these conditions:

# The garden has at least two flowers.
# The first and the last flower of the garden have the same beauty value.
# As the appointed gardener, you have the ability to remove any (possibly none) flowers from the garden. You want to remove flowers in a way that makes the remaining garden valid. The beauty of the garden is the sum of the beauty of all the remaining flowers.

# Return the maximum possible beauty of some valid garden after you have removed any (possibly none) flowers.

# Solution, O(n) time and space
# Store the rightmost occurence of each beauty. Iterate through, for each beauty, find the rightmost index. Then check the sum of the elements in between using a range query. Range query is modified so negative elements are not included, since we would remove those. We also take the range of inside the two boundaries then add the two boundaries separately in case the boundaries are negative.

class Solution:
    def maximumBeauty(self, flowers: List[int]) -> int:
        rightmostOccurences = {} # maps a flower beauty to the rightmost index it occurs at
        for i in range(len(flowers) - 1, -1, -1):
            beauty = flowers[i]
            if not beauty in rightmostOccurences:
                rightmostOccurences[beauty] = i

        running_sum = 0
        prefix_sums = [] # store sums of prior elements
        for num in flowers:
            # modification since we will always remove negative flowers

            prefix_sums.append(running_sum)
            if num > 0:
                running_sum += num
        prefix_sums.append(running_sum)

        def sum_query(l, r):
            return prefix_sums[r + 1] - prefix_sums[l]


        result = float('-inf')
        for i in range(len(flowers)):
            beauty = flowers[i]
            rightmost = rightmostOccurences[beauty]
            # we are at the rightmost flower then skip
            if rightmost == i:
                continue
            sumForThis = sum_query(i + 1, rightmost - 1) + (2 * beauty)
            result = max(result, sumForThis)
        return result

