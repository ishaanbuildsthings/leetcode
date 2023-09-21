# https://leetcode.com/problems/unique-number-of-occurrences/
# Difficulty: Easy

# Problem
# Given an array of integers arr, return true if the number of occurrences of each value in the array is unique or false otherwise.
# O(n) time and space
# Count the values, store it in a set to remove duplicates, and see if the sum is the length of the array!

class Solution:
    def uniqueOccurrences(self, arr: List[int]) -> bool:
        return sum(set(Counter(arr).values())) == len(arr)
