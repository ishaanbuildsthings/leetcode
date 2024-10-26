# https://leetcode.com/problems/replace-elements-in-an-array/description/
# difficulty: Medium

# Problem
# You are given a 0-indexed array nums that consists of n distinct positive integers. Apply m operations to this array, where in the ith operation you replace the number operations[i][0] with operations[i][1].

# It is guaranteed that in the ith operation:

# operations[i][0] exists in nums.
# operations[i][1] does not exist in nums.
# Return the array obtained after applying all the operations.

# Solution, O(n) time and space
# First map the position of each number. For each operation, delete that old position and update a new one. Due to constraints there can never be a duplicate number. If that constraint weren't there, we may be able to use something more advanced, like storing paths, a points to b, b points to c, etc. And if we want to update a, we traverse to the parent, and update its root parent c points to d. We path compress along the way.

class Solution:
    def arrayChange(self, nums: List[int], operations: List[List[int]]) -> List[int]:
        # map each element to its position
        positions = {}
        for i, val in enumerate(nums):
            positions[val] = i
        for toReplace, replaceWith in operations:
            pos = positions[toReplace]
            nums[pos] = replaceWith
            positions[replaceWith] = pos
            del positions[toReplace]
        return nums