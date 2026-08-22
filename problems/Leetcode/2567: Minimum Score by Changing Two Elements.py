# https://leetcode.com/problems/minimum-score-by-changing-two-elements/description/
# Difficulty: Medium
# tags: greedy

# Problem
# You are given a 0-indexed integer array nums.

# The low score of nums is the minimum value of |nums[i] - nums[j]| over all 0 <= i < j < nums.length.
# The high score of nums is the maximum value of |nums[i] - nums[j]| over all 0 <= i < j < nums.length.
# The score of nums is the sum of the high and low scores of nums.
# To minimize the score of nums, we can change the value of at most two elements of nums.

# Return the minimum possible score after changing the value of at most two elements of nums.

# Note that |x| denotes the absolute value of x.

# Solution
# There's only a few possible optimal cases. We can do it in linear time and constant space by iterating and tracking the smallest and biggest few.


class Solution:
    def minimizeSum(self, nums: List[int]) -> int:
        nums.sort()
        # change the two from the left
        res1 = nums[-1] - nums[2]
        # change the two from the right
        res2 = nums[-3] - nums[0]
        # change one from each
        res3 = nums[-2] - nums[1]
        return min(res1, res2, res3)
