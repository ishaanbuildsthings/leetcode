# https://leetcode.com/problems/minimum-elements-to-add-to-form-a-given-sum/
# difficulty: medium

# Problem
# You are given an integer array nums and two integers limit and goal. The array nums has an interesting property that abs(nums[i]) <= limit.

# Return the minimum number of elements you need to add to make the sum of the array equal to goal. The array must maintain its property that abs(nums[i]) <= limit.

# Note that abs(x) equals x if x >= 0, and -x otherwise.

# Solution, O(n) time, O(1) space

class Solution:
    def minElements(self, nums: List[int], limit: int, goal: int) -> int:
        total = sum(nums)
        distance = abs(total - goal)
        return math.ceil(distance / limit)