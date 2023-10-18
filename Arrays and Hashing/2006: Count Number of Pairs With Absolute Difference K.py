# https://leetcode.com/problems/count-number-of-pairs-with-absolute-difference-k/
# Difficulty: Easy

# Problem
# Given an integer array nums and an integer k, return the number of pairs (i, j) where i < j such that |nums[i] - nums[j]| == k.

# The value of |x| is defined as:

# x if x >= 0.
# -x if x < 0.

# Solution, O(n) time and space. Treat each number as the smaller and the bigger, check the presence of the other number.

class Solution:
    def countKDifference(self, nums: List[int], k: int) -> int:
        frqs = defaultdict(int)
        res = 0
        for i in range(len(nums)):
            above = nums[i] + k
            below = nums[i] - k
            res = res + frqs[above] + frqs[below]
            frqs[nums[i]] += 1
        return res