# https://leetcode.com/problems/search-in-a-sorted-array-of-unknown-size/
# Difficulty: Medium
# Tags: binary search

# Problem
# This is an interactive problem.

# You have a sorted array of unique elements and an unknown size. You do not have an access to the array but you can use the ArrayReader interface to access it. You can call ArrayReader.get(i) that:

# returns the value at the ith index (0-indexed) of the secret array (i.e., secret[i]), or
# returns 231 - 1 if the i is out of the boundary of the array.
# You are also given an integer target.

# Return the index k of the hidden array where secret[k] == target or return -1 otherwise.

# You must write an algorithm with O(log n) runtime complexity.

# Solution, O(log n) time, O(1) space
# First, search for the bounds of the array. Then search within those bounds. Though I feel like you could just do it with one search...

# """
# This is ArrayReader's API interface.
# You should not implement it, or speculate about its implementation
# """
#class ArrayReader:
#    def get(self, index: int) -> int:

class Solution:
    def search(self, reader: 'ArrayReader', target: int) -> int:
        # first, find the length of the array
        l = 1
        r = 10**4
        while (l <= r):
            m = ((r+l)//2) # the inde we check for the length
            if reader.get(m) == 2147483647:
                r = m - 1
            else:
                l = m + 1
        arr_length = r
        l = 0
        r = arr_length
        # do a binary search to find the number
        while (l < r):
            m = (r+l)//2 # m is the index of the number we are looking for
            if reader.get(m) < target:
                l = m + 1
            else:
                r = m
        if reader.get(r) == target:
            return r
        return -1
