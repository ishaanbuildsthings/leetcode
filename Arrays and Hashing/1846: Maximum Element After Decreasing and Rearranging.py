# https://leetcode.com/problems/maximum-element-after-decreasing-and-rearranging/?envType=daily-question&envId=2023-11-15
# difficulty: medium

# Problem
# You are given an array of positive integers arr. Perform some operations (possibly none) on arr so that it satisfies these conditions:

# The value of the first element in arr must be 1.
# The absolute difference between any 2 adjacent elements must be less than or equal to 1. In other words, abs(arr[i] - arr[i - 1]) <= 1 for each i where 1 <= i < arr.length (0-indexed). abs(x) is the absolute value of x.
# There are 2 types of operations that you can perform any number of times:

# Decrease the value of any element of arr to a smaller positive integer.
# Rearrange the elements of arr to be in any order.
# Return the maximum possible value of an element in arr after performing the operations to satisfy the conditions.

# Solution, O(n log n) time and O(sort) space.
# Sorting always benefits us, we sort then whenever we can exceed our goal we drop to it.
# We can also do an O(n) time solution by counting values, since we know we need target values of 1, 2, 3, ...

class Solution:
    def maximumElementAfterDecrementingAndRearranging(self, arr: List[int]) -> int:
        arr.sort()
        goal = 1 # what we are aiming to see next
        for num in arr:
            if num >= goal:
                goal += 1
        return goal - 1
