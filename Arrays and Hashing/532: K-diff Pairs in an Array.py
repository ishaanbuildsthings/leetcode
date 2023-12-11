# https://leetcode.com/problems/k-diff-pairs-in-an-array/description/
# difficulty: medium

# Problem
# Given an array of integers nums and an integer k, return the number of unique k-diff pairs in the array.

# A k-diff pair is an integer pair (nums[i], nums[j]), where the following are true:

# 0 <= i, j < nums.length
# i != j
# |nums[i] - nums[j]| == k
# Notice that |val| denotes the absolute value of val.

# Solution, O(n) time and space, just keep a running count of what we have seen

class Solution:
    def findPairs(self, nums: List[int], k: int) -> int:
        unique = set()
        seen = set()
        for num in nums:
            target1 = num + k
            target2 = num - k
            if target1 in seen:
                unique.add( (min(target1, num), max(target1, num)) )
            if target2 in seen:
                unique.add( (min(target2, num), max(target2, num)) )
            seen.add(num)
        return len(unique)