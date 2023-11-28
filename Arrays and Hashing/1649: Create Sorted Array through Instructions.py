# https://leetcode.com/problems/create-sorted-array-through-instructions/description/
# difficulty: hard
# tags: avl tree

# Problem
# Given an integer array instructions, you are asked to create a sorted array from the elements in instructions. You start with an empty container nums. For each element from left to right in instructions, insert it into nums. The cost of each insertion is the minimum of the following:

# The number of elements currently in nums that are strictly less than instructions[i].
# The number of elements currently in nums that are strictly greater than instructions[i].
# For example, if inserting element 3 into nums = [1,2,3,5], the cost of insertion is min(2, 1) (elements 1 and 2 are less than 3, element 5 is greater than 3) and nums will become [1,2,3,3,5].

# Return the total cost to insert all elements from instructions into nums. Since the answer may be large, return it modulo 109 + 7

# Solution, O(n log n) time, O(n) space, I just used a sorted list. Using SortedList.bisect is faster than bisect.bisect.

import sortedcontainers

class Solution:
    def createSortedArray(self, instructions: List[int]) -> int:
        nums = sortedcontainers.SortedList()
        res = 0
        for instruct in instructions:
            numLess = nums.bisect_left(instruct)
            numMore = len(nums) - nums.bisect_right(instruct)
            res += min(numLess, numMore)
            nums.add(instruct)
        return res % (10**9 + 7)