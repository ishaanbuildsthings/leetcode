# https://leetcode.com/problems/apply-operations-to-an-array/description/
# difficulty: easy
# tags: multiconcept

# Problem
# You are given a 0-indexed array nums of size n consisting of non-negative integers.

# You need to apply n - 1 operations to this array where, in the ith operation (0-indexed), you will apply the following on the ith element of nums:

# If nums[i] == nums[i + 1], then multiply nums[i] by 2 and set nums[i + 1] to 0. Otherwise, you skip this operation.
# After performing all the operations, shift all the 0's to the end of the array.

# For example, the array [1,0,2,0,0,1] after shifting all its 0's to the end, is [1,2,1,0,0,0].
# Return the resulting array.

# Note that the operations are applied sequentially, not all at once.

# Solution, O(n) time, O(1) space, construct then move zeroes

class Solution:
    def applyOperations(self, nums: List[int]) -> List[int]:
        res = nums[:]
        for i in range(len(res) - 1):
            if res[i] == res[i + 1]:
                res[i] *= 2
                res[i + 1] = 0
        # move zeroes
        l = 0
        for r in range(len(res)):
            if res[r]:
                res[l], res[r] = res[r], res[l]
                l += 1
        return res