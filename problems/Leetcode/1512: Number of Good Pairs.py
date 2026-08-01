# https://leetcode.com/problems/number-of-good-pairs/
# Difficulty: Easy

# Problem
# Given an array of integers nums, return the number of good pairs.

# A pair (i, j) is called good if nums[i] == nums[j] and i < j.

# Solution, O(n) time and space. Store prior counts as we iterate.
# While easy, this is a foundational concept for many harder problems.

class Solution:
    def numIdenticalPairs(self, nums: List[int]) -> int:
        counts = defaultdict(int)
        res = 0
        for i in range(len(nums)):
            num = nums[i]
            res += counts[num]
            counts[num] += 1
        return res