# https://leetcode.com/problems/global-and-local-inversions/description/
# Difficulty: medium
# tags: prefix

# Problem
# You are given an integer array nums of length n which represents a permutation of all the integers in the range [0, n - 1].

# The number of global inversions is the number of the different pairs (i, j) where:

# 0 <= i < j < n
# nums[i] > nums[j]
# The number of local inversions is the number of indices i where:

# 0 <= i < n - 1
# nums[i] > nums[i + 1]
# Return true if the number of global inversions is equal to the number of local inversions.

# Solution, O(n) time and space
# Global equals local if there is no global, I wrote an O(n) space but we can just use O(1) space and not precompute the prefixes

class Solution:
    def isIdealPermutation(self, nums: List[int]) -> bool:
        prefixBiggest = {}
        runningBiggest = 0
        for i in range(len(nums)):
            runningBiggest = max(runningBiggest, nums[i])
            prefixBiggest[i] = runningBiggest
        prefixBiggest[-1] = 0
        prefixBiggest[-2] = 0

        for i in range(len(nums)):
            num = nums[i]
            twoBackBiggest = prefixBiggest[i - 2]
            if twoBackBiggest > num:
                return False

        return True