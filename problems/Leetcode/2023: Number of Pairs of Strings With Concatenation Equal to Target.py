# https://leetcode.com/problems/number-of-pairs-of-strings-with-concatenation-equal-to-target/description/
# Difficulty: medium

# Problem
# Given an array of digit strings nums and a digit string target, return the number of pairs of indices (i, j) (where i != j) such that the concatenation of nums[i] + nums[j] equals target.

# Solution, O(nums ^ 3) time, O(max(nums)) space
# Just test adding all pairs, I believe this can be done faster in a myriad of ways with various things like prefix/suffix, tries, rolling hash, etc

class Solution:
    def numOfPairs(self, nums: List[str], target: str) -> int:
        res = 0
        for i in range(len(nums)):
            for j in range(len(nums)):
                if i == j:
                    continue
                if nums[i] + nums[j] == target:
                    res += 1
        return res