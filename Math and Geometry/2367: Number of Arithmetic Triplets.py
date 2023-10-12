# https://leetcode.com/problems/number-of-arithmetic-triplets/
# difficulty: easy
# tags: math

# Problem
# You are given a 0-indexed, strictly increasing integer array nums and a positive integer diff. A triplet (i, j, k) is an arithmetic triplet if the following conditions are met:

# i < j < k,
# nums[j] - nums[i] == diff, and
# nums[k] - nums[j] == diff.
# Return the number of unique arithmetic triplets.

# Solution, O(n) time and space
# Assume each number is the middle of a triplet (could do it differently, but you need to create the entire set first then), then check for the presence of the other elements

class Solution:
    def arithmeticTriplets(self, nums: List[int], diff: int) -> int:
        numSet = set(nums)
        res = 0
        for num in nums:
            if num - diff in numSet and num + diff in numSet:
                res += 1
        return res